import serial
import serial.tools.list_ports
import time
from typing import Optional, Tuple
import ftd2xx as ft
class TemperatureReader:
    """通过串口读取 TMP117 温度传感器数据（支持上下文管理器）"""

    class CommandSrc:
        TMP117_ADDR48 = 0x08   # PKG 温度
        TMP117_ADDR49 = 0x09   # PCB 温度

    class CommandType:
        GET_TEMP_DATA = 0x02

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, timeout: float = 1.0):
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum

    def _read_exact(self, size: int) -> bytes:
        data = bytearray()
        start = time.time()
        while len(data) < size:
            remaining = size - len(data)
            chunk = self._serial.read(remaining)
            if not chunk:
                if time.time() - start > self.timeout:
                    raise TimeoutError(f"读取超时，已收到 {len(data)}/{size} 字节")
                continue
            data.extend(chunk)
        return bytes(data)

    def _send_command_and_read_response(self, device: int) -> float:
        payload = bytes([device, self.CommandType.GET_TEMP_DATA, 0x00, 0x00])
        checksum = self._calculate_checksum(payload)
        packet = payload + bytes([checksum])

        self._serial.reset_input_buffer()
        self._serial.write(packet)

        response = self._read_exact(5)

        header = response[0]
        if header != device:
            raise RuntimeError(f"响应头不匹配: 期望 0x{device:02X}, 收到 0x{header:02X}")

        status = response[1]
        if status != 0xFD:
            raise RuntimeError(f"命令执行失败，错误码: 0x{status:02X}")

        calc_checksum = self._calculate_checksum(response[1:4])
        recv_checksum = response[4]
        if calc_checksum != recv_checksum:
            raise RuntimeError("响应校验和错误")

        raw_temp = (response[2] << 8) | response[3]
        temperature = self._raw_to_celsius(raw_temp)
        return temperature

    @staticmethod
    def _raw_to_celsius(raw_value: int) -> float:
        if raw_value & 0x8000:
            abs_raw = (~raw_value + 1) & 0x7FFF
            return - (abs_raw * 0.0078125)
        else:
            return raw_value * 0.0078125

    def get_temperature_pkg(self) -> float:
        return self._send_command_and_read_response(self.CommandSrc.TMP117_ADDR48)

    def get_temperature_pcb(self) -> float:
        return self._send_command_and_read_response(self.CommandSrc.TMP117_ADDR49)

    def get_all_temperatures(self) -> Tuple[float, float]:
        pkg = self.get_temperature_pkg()
        pcb = self.get_temperature_pcb()
        return pkg, pcb

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



if __name__ == "__main__":
    try:
        port=get_com_port_for_channel()
        reader = TemperatureReader(port=port)   # 自动查找串口
        # 单次读取两个温度
        for i in range(10):
            pkg, pcb = reader.get_all_temperatures()
            print(f"PKG 温度: {pkg:.3f} °C")
            print(f"PCB 温度: {pcb:.3f} °C")

        # 或者单独读取
        # pkg = reader.get_temperature_pkg()
        # pcb = reader.get_temperature_pcb()

        reader.close()
    except Exception as e:
        print(f"错误: {e}")