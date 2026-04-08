"""FTDI JTAG设备基类"""

import threading
from typing import Optional, List


class FTDIJTAGDevice:
    """FTDI JTAG设备基类
    
    属性:
        device: FTDI设备对象
        device_name: 设备名称
        ir_value: IR寄存器值（影响block1中第5个数据）
        addr_width: 地址位宽（字节数）
        data_width: 数据位宽（字节数）
        clock_divisor: 时钟分频系数（影响seq21中的值）
        _lock: 线程锁，保证读写操作的线程安全
        _init_extra_seqs: 初始化序列的额外部分（在基础序列之后）
        _init_read_bytes: 初始化后需要读取的字节数（0表示不需要读取）
        _write_block2_prefix: 写入操作block2的前缀（None表示无前缀）
        _read_block2_suffix: 读取操作block2的后缀（None表示无后缀）
        _write_block3_suffix: 写入操作block3的后缀（None表示无后缀）
        _read_block4: 读取操作是否需要block4（None表示不需要）
        _write_block4: 写入操作是否需要block4（None表示不需要）
    """
    
    def __init__(self, device, device_name: str, ir_value: int, 
                 addr_width: int, data_width: int, clock_divisor: int = 0x00,
                 init_extra_seqs: Optional[List[bytes]] = None,
                 init_read_bytes: int = 0,
                 write_block2_prefix: Optional[bytes] = None,
                 read_block2_suffix: Optional[bytes] = None,
                 write_block3_suffix: Optional[bytes] = None,
                 read_block4: Optional[bytes] = None,
                 write_block4: Optional[bytes] = None):
        """初始化JTAG设备
        
        Args:
            device: FTDI设备对象
            device_name: 设备名称（如'serdes'或'top'）
            ir_value: IR寄存器值
            addr_width: 地址位宽（字节数）
            data_width: 数据位宽（字节数）
            clock_divisor: 时钟分频系数，默认0x00
            init_extra_seqs: 初始化序列的额外部分
            init_read_bytes: 初始化后需要读取的字节数
            write_block2_prefix: 写入操作block2的前缀
            read_block2_suffix: 读取操作block2的后缀
            write_block3_suffix: 写入操作block3的后缀
            read_block4: 读取操作的block4
            write_block4: 写入操作的block4
        """
        self.device = device
        self.device_name = device_name
        self.ir_value = ir_value
        self.addr_width = addr_width
        self.data_width = data_width
        self.clock_divisor = clock_divisor
        self._lock = threading.Lock()  # 线程锁，保证线程安全
        
        # 设备特定配置
        self._init_extra_seqs = init_extra_seqs or []
        self._init_read_bytes = init_read_bytes
        self._write_block2_prefix = write_block2_prefix
        self._read_block2_suffix = read_block2_suffix
        self._write_block3_suffix = write_block3_suffix
        self._read_block4 = read_block4
        self._write_block4 = write_block4
        
    def initialize(self):
        """初始化设备，发送初始化序列"""
        with self._lock:
            self._send_init_sequence()
    
    def read_register(self, addr: int) -> bytes:
        """读取寄存器（线程安全）
        
        Args:
            addr: 寄存器地址
            
        Returns:
            读取的数据（字节数组，小端序）
        """
        with self._lock:
            return self._read_register_impl(addr)
    
    def write_register(self, addr: int, value: int):
        """写入寄存器（线程安全）
        
        Args:
            addr: 寄存器地址
            value: 要写入的值
        """
        with self._lock:
            self._write_register_impl(addr, value)
    
    def _send_init_sequence(self):
        """发送初始化序列"""
        # 基础初始化序列（所有设备通用）
        seq0 = bytes.fromhex("8a 97 8d")
        seq1 = bytes.fromhex("80 08 0b")
        seq2 = bytes.fromhex("82 00 00")
        seq21 = bytes([0x86, 0x05, self.clock_divisor])
        seq3 = bytes.fromhex("85")
        seq4 = bytes.fromhex("80 08 0b 4b 06 7f 4b 00 00")
        seq5 = bytes.fromhex("4b 03 03 1b 06 ee 4b 03 83")
        
        self.device.write(seq0)
        self.device.write(seq1)
        self.device.write(seq2)
        self.device.write(seq21)
        self.device.write(seq3)
        self.device.write(seq4)
        self.device.write(seq5)
        
        # 设备特定的额外序列
        for seq in self._init_extra_seqs:
            self.device.write(seq)
        
        # 如果需要，读取并丢弃响应
        if self._init_read_bytes > 0:
            self.device.read(self._init_read_bytes)
    
    def _read_register_impl(self, addr: int) -> bytes:
        """读取寄存器的具体实现"""
        # 将地址分解为字节
        addr_bytes = []
        for i in range(self.addr_width):
            addr_bytes.append((addr >> (i * 8)) & 0xFF)
        
        # block1: IR值设置（所有设备相同）
        block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, self.ir_value, 0x4B, 0x02, 0x03])
        
        # block2: 发送地址（根据地址宽度和配置构建）
        # 基础部分：0x4B, 0x02, 0x01, 0x19, [宽度-1], 0x00, [地址字节], 0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83
        block2_base = [0x4B, 0x02, 0x01, 0x19, self.addr_width - 1, 0x00]
        block2_base.extend(addr_bytes)
        block2_base.extend([0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83])
        
        # 添加后缀（如果有）
        if self._read_block2_suffix:
            block2_base.extend(self._read_block2_suffix)
        
        block2 = bytes(block2_base)
        
        # block3: 读取数据（宽度字段是数据宽度-1）
        block3 = bytes([0x4B, 0x02, 0x01, 0x28, self.data_width - 1, 0x00, 0x2a, 0x00, 0x6B, 0x02, 0x03, 0x87, 0x8E, 0x01])
        
        self.device.write(block1)
        self.device.write(block2)
        self.device.write(block3)
        data = self.device.read(self.data_width)
        data_le = data[::-1]  # 转换为小端序
        self.device.read(2)  # 读取并丢弃2字节
        
        # 如果需要，发送block4
        if self._read_block4:
            self.device.write(self._read_block4)
        
        return data_le
    
    def _write_register_impl(self, addr: int, value: int):
        """写入寄存器的具体实现"""
        # 将地址分解为字节
        addr_bytes = []
        for i in range(self.addr_width):
            addr_bytes.append((addr >> (i * 8)) & 0xFF)
        
        # 将数据分解为字节
        value_bytes = []
        for i in range(self.data_width):
            value_bytes.append((value >> (i * 8)) & 0xFF)
        
        # block1: IR值设置（所有设备相同）
        block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, self.ir_value, 0x4B, 0x03, 0x03])
        
        # block2: 发送地址
        block2_base = []
        # 如果有前缀，先添加前缀
        if self._write_block2_prefix:
            block2_base.extend(self._write_block2_prefix)
        
        # 基础部分：0x4B, 0x02, 0x01, 0x19, [宽度-1], 0x00, [地址字节], 0x1B, 0x00, 0x00, 0x4B, 0x02, 0x03
        block2_base.extend([0x4B, 0x02, 0x01, 0x19, self.addr_width - 1, 0x00])
        block2_base.extend(addr_bytes)
        block2_base.extend([0x1B, 0x00, 0x00, 0x4B, 0x02, 0x03])
        
        block2 = bytes(block2_base)
        
        # block3: 发送数据（宽度字段是数据宽度-1）
        block3_base = [0x4B, 0x02, 0x01, 0x19, self.data_width - 1, 0x00]
        block3_base.extend(value_bytes)
        block3_base.extend([0x1B, 0x00, 0x01, 0x4B, 0x02, 0x03])
        
        # 添加后缀（如果有）
        if self._write_block3_suffix:
            block3_base.extend(self._write_block3_suffix)
        
        block3 = bytes(block3_base)
        
        self.device.write(block1)
        self.device.write(block2)
        self.device.write(block3)
        
        # 如果需要，发送block4
        if self._write_block4:
            self.device.write(self._write_block4)
    
    def close(self):
        """关闭设备"""
        if self.device:
            self.device.close()

