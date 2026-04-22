import serial
import serial.tools.list_ports
from typing import Optional
import ftd2xx as ft
class VoltageController:
    """通过串口设置电压的控制器（无 UI 依赖）"""

    class BankNumber:
        BANK0 = 0x00
        BANK1 = 0x01
        BANK2 = 0x02

    class CommandSrc:
        IIC1_87562   = 0x00
        IIC1_87564   = 0x01
        IIC1_628680  = 0x02
        IIC1_628681  = 0x03
        IIC3_628684  = 0x04
        INA226_ADDR42  = 0x05
        INA226_ADDR43  = 0x06
        INA226_ADDR44  = 0x07
        TMP117_ADDR48 = 0x08
        TMP117_ADDR49 = 0x09

    class CommandType:
        SET_VOLTAGE    = 0x00
        GET_POWER_DATA = 0x01
        GET_TEMP_DATA  = 0x02

    BANK_DEFAULT_VOLTAGES = {0: 0.95, 1: 0.80, 2: 1.80}

    def __init__(self, port, baudrate: int = 115200, timeout: float = 1.0):
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None

        if port is None:
            port = self._find_ft4232h_d_channel()
            if port is None:
                raise RuntimeError("未找到 FT4232H D 通道串口")

        self._open_serial(port)

    def _find_ft4232h_d_channel(self) -> Optional[str]:
        for port in serial.tools.list_ports.comports():
            if port.vid == 0x0403 and port.pid == 0x6011:
                if 'D' in port.description or port.interface == 3:
                    return port.device
        return None

    def _open_serial(self, port: str):
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
        except Exception as e:
            raise RuntimeError(f"打开串口 {port} 失败: {e}")

    def close(self):
        """显式关闭串口"""
        if self._serial and self._serial.is_open:
            self._serial.close()

    # 上下文管理器协议
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def voltage_to_register(voltage: float) -> int:
        if 0.6 <= voltage <= 0.73:
            step = int((voltage - 0.6) / 0.01 + 0.5)
            return 0x0A + step
        elif 0.73 < voltage <= 1.4:
            step = int((voltage - 0.735) / 0.005 + 0.5)
            return 0x18 + step
        elif 1.4 < voltage <= 3.36:
            step = int((voltage - 1.42) / 0.02 + 0.5)
            return 0x9E + step
        else:
            raise ValueError(f"电压 {voltage}V 超出硬件支持范围 (0.6~3.36V)")

    @staticmethod
    def register_to_voltage(reg: int) -> float:
        if 0x0A <= reg <= 0x17:
            return 0.6 + (reg - 0x0A) * 0.01
        elif 0x18 <= reg <= 0x9D:
            return 0.735 + (reg - 0x18) * 0.005
        elif 0x9E <= reg <= 0xFF:
            return 1.42 + (reg - 0x9E) * 0.02
        else:
            raise ValueError(f"无效寄存器值: 0x{reg:02X}")

    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum

    def _send_command(self, cmd_src: int, cmd_type: int, bank_num: int, reg_value: int) -> bool:
        payload = bytes([cmd_src, cmd_type, bank_num, reg_value])
        checksum = self._calculate_checksum(payload)
        packet = payload + bytes([checksum])

        self._serial.reset_input_buffer()
        self._serial.write(packet)

        response = self._serial.read(3)
        if len(response) < 3:
            raise TimeoutError("未收到完整响应")

        if response[0] != cmd_src:
            raise RuntimeError(f"响应头不匹配: 期望 0x{cmd_src:02X}, 收到 0x{response[0]:02X}")

        status = response[1]
        if status != 0xFD:
            raise RuntimeError(f"设置失败，错误码: 0x{status:02X}")

        return True

    def set_voltage(self, bank: int, voltage: float, default_voltage: float = None) -> float:
        if bank not in (0, 1, 2):
            raise ValueError("bank 必须是 0,1,2")

        reg = self.voltage_to_register(voltage)
        actual_voltage = self.register_to_voltage(reg)

        if default_voltage is not None:
            if abs(default_voltage - 0.8) < 0.01:
                min_v, max_v = 0.7, 0.9
            elif abs(default_voltage - 0.95) < 0.01:
                min_v, max_v = 0.85, 1.1
            elif abs(default_voltage - 1.8) < 0.01:
                min_v, max_v = 1.6, 2.2
            else:
                min_v, max_v = default_voltage * 0.9, default_voltage * 1.1

            if actual_voltage < min_v or actual_voltage > max_v:
                raise ValueError(
                    f"电压 {actual_voltage:.3f}V 超出允许范围 [{min_v:.3f}, {max_v:.3f}]V "
                    f"(默认电压 {default_voltage:.3f}V)"
                )

        cmd_src = self.CommandSrc.IIC1_87564
        bank_num_map = {0: self.BankNumber.BANK0, 1: self.BankNumber.BANK1, 2: self.BankNumber.BANK2}
        bank_enum = bank_num_map[bank]

        self._send_command(cmd_src, self.CommandType.SET_VOLTAGE, bank_enum, reg)
        return actual_voltage

    def set_voltage_with_default_check(self, bank: int, voltage: float) -> float:
        default_v = self.BANK_DEFAULT_VOLTAGES[bank]
        return self.set_voltage(bank, voltage, default_voltage=default_v)



def get_com_port_for_channel(channel_letter='D'):
    """
    根据通道字母（A/B/C/D）返回对应的 COM 口号。
    如果未找到或不是串口模式，返回 None。
    """
    # 遍历四个接口（索引 0~3）
    for idx in range(4):
        try:
            dev = ft.open(idx)
            info = dev.getDeviceInfo()
            desc = info['description'].decode('ascii') if isinstance(info['description'], bytes) else info['description']
            # 检查描述中是否包含目标通道字母
            if f'RS232-HS {channel_letter}' in desc:
                try:
                    com = dev.getComPortNumber()
                    if com:
                        dev.close()
                        return f"COM{com}"

                    else:
                        return None
                except:
                    return None
            dev.close()
        except:
            continue


    return None


# ---------- 使用示例（修改后） ----------
if __name__ == "__main__":
    try:
        port=get_com_port_for_channel()
        with VoltageController(port=port) as ctrl:
            # bank0:0.95 bank1:0.8 bank2:1.8
            actual = ctrl.set_voltage_with_default_check(2, 1.88)
            print(f"设置成功，实际电压: {actual:.3f}V")
    except Exception as e:
        print(f"错误: {e}")