import serial
import serial.tools.list_ports
import time
from typing import Optional, Tuple

class TemperatureReader:
    """通过串口读取 TMP117 温度传感器数据（无 UI 依赖）"""

    # ---------- 枚举定义（与原代码一致） ----------
    class CommandSrc:
        TMP117_ADDR48 = 0x08   # PKG 温度
        TMP117_ADDR49 = 0x09   # PCB 温度

    class CommandType:
        GET_TEMP_DATA = 0x02   # 获取温度命令

    # ---------- 初始化与串口管理 ----------
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, timeout: float = 1.0):
        """
        初始化温度读取器
        :param port: 串口名（如 COM3, /dev/ttyUSB0），若为 None 则自动查找 FT4232H D 通道
        :param baudrate: 波特率
        :param timeout: 串口读取超时（秒）
        """
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None

        if port is None:
            port = self._find_ft4232h_d_channel()
            if port is None:
                raise RuntimeError("未找到 FT4232H D 通道串口")

        self._open_serial(port)

    def _find_ft4232h_d_channel(self) -> Optional[str]:
        """查找 FT4232H 的 D 通道设备名（根据 VID/PID 和接口描述）"""
        for port in serial.tools.list_ports.comports():
            if port.vid == 0x0403 and port.pid == 0x6011:   # FT4232H 常见 ID
                if 'D' in port.description or port.interface == 3:
                    return port.device
        return None

    def _open_serial(self, port: str):
        """打开并配置串口"""
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            # 清空缓冲区
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
        except Exception as e:
            raise RuntimeError(f"打开串口 {port} 失败: {e}")

    def close(self):
        """关闭串口"""
        if self._serial and self._serial.is_open:
            self._serial.close()

    def __del__(self):
        self.close()

    # ---------- 辅助函数 ----------
    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        """异或校验和"""
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum

    def _read_exact(self, size: int) -> bytes:
        """读取指定字节数，超时则抛出异常"""
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
        """
        发送温度读取命令并等待响应，返回解析后的温度值（摄氏度）
        :param device: 命令源地址（0x08 或 0x09）
        """
        # 构建命令: [cmd_src, cmd_type, 0x00, 0x00, checksum]
        payload = bytes([device, self.CommandType.GET_TEMP_DATA, 0x00, 0x00])
        checksum = self._calculate_checksum(payload)
        packet = payload + bytes([checksum])

        # 清空输入缓冲区，避免残留数据
        self._serial.reset_input_buffer()
        # 发送
        self._serial.write(packet)

        # 读取响应（固定 5 字节）
        response = self._read_exact(5)

        # 解析
        header = response[0]
        if header != device:
            raise RuntimeError(f"响应头不匹配: 期望 0x{device:02X}, 收到 0x{header:02X}")

        status = response[1]
        if status != 0xFD:
            raise RuntimeError(f"命令执行失败，错误码: 0x{status:02X}")

        # 校验和（对 status + 2字节数据 共3字节）
        calc_checksum = self._calculate_checksum(response[1:4])  # 索引1~3
        recv_checksum = response[4]
        if calc_checksum != recv_checksum:
            raise RuntimeError("响应校验和错误")

        # 解析温度原始值（大端序）
        raw_temp = (response[2] << 8) | response[3]
        temperature = self._raw_to_celsius(raw_temp)
        return temperature

    @staticmethod
    def _raw_to_celsius(raw_value: int) -> float:
        """TMP117 原始值转摄氏度（公式与原代码一致）"""
        if raw_value & 0x8000:   # 负温度
            abs_raw = (~raw_value + 1) & 0x7FFF
            return - (abs_raw * 0.0078125)
        else:
            return raw_value * 0.0078125

    # ---------- 公开接口 ----------
    def get_temperature_pkg(self) -> float:
        """获取 PKG 温度（传感器地址 0x48）"""
        return self._send_command_and_read_response(self.CommandSrc.TMP117_ADDR48)

    def get_temperature_pcb(self) -> float:
        """获取 PCB 温度（传感器地址 0x49）"""
        return self._send_command_and_read_response(self.CommandSrc.TMP117_ADDR49)

    def get_all_temperatures(self) -> Tuple[float, float]:
        """依次获取 PKG 和 PCB 温度，返回 (pkg_temp, pcb_temp)"""
        pkg = self.get_temperature_pkg()
        pcb = self.get_temperature_pcb()
        return pkg, pcb


# ---------- 使用示例 ----------
if __name__ == "__main__":
    try:
        reader = TemperatureReader()   # 自动查找串口
        # 单次读取两个温度
        pkg, pcb = reader.get_all_temperatures()
        print(f"PKG 温度: {pkg:.3f} °C")
        print(f"PCB 温度: {pcb:.3f} °C")

        # 或者单独读取
        # pkg = reader.get_temperature_pkg()
        # pcb = reader.get_temperature_pcb()

        reader.close()
    except Exception as e:
        print(f"错误: {e}")