"""IDCODE JTAG support for ftd2jtag"""

from .mpsse_commands import *
import json
import os
import time
import serial
import re
from ftd2xx import FT_PURGE_RX
import ftd2xx as ft
#region agent log
def _agent_log(hypothesis_id, message, data):
    log_path = r"c:\work\pcie\P5\host\python\ft2232h\ftd2jtag-main\.cursor\debug.log"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as _f:
            _f.write(
                json.dumps(
                    {
                        "sessionId": "debug-session",
                        "runId": "pre-fix",
                        "hypothesisId": hypothesis_id,
                        "location": f"serdes_reg.py:{message}",
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception as e:
        print(f"[agent_log error] {e}")
#endregion

'''
初使化流程命令：
8a
97
8d
80080b
820000
860000  (86 分频系数低字节 分频系数高字节 )
85
80080b 4b067f 4b0000
4b0303 1b06ee 4b0383
4b0303 1b0601 4b0303 (serdes) 
4b0201 280200 2a066b 020387(serdes) 

寄存器写命令：
SERDES寄存器写命令：
0x4b,0x03,0x03,0x1b,0x06,0x31,0x4b,0x03,0x03
0x4b,0x02,0x01,0x19,0x01,0x00,0x00（地址低字节）,0x10（地址高字节）,0x1b,0x00,0x00,0x4b,0x02,0x03,0x8e,0x04
0x4b,0x02,0x01,0x19,0x01,0x00,0x34（数据低字节）,0x12（数据低字节）,0x1b,0x00,0x01,0x4b,0x02,0x03,0x8e,0x04

DDR寄存器写命令：
0x4b,0x03,0x03,0x1b,0x06,0x08,0x4b,0x03,0x03
0x80,0x00,0x40,0x4b,0x02,0x01,0x19,0x03,0x00,0x84（地址低字节0）,0x00（地址字节1）,0x00（地址字节2）,0x00（地址高字节3）,0x1b,0x00,0x00,0x4b,0x02,0x03
0x4b,0x02,0x01,0x19,0x03,0x00,0x84（数据低字节0）,0x00（数据字节1）,0x00（数据字节2）,0x00（数据高字节3）,0x1b,0x00,0x01,0x4b,0x02,0x03,0x94
0x80,0x40,0x40


寄存器读命令：
SERDES寄存器读命令：
0x4b,0x03,0x03,0x1b,0x06,0x31,0x4b,0x03,0x03 
0x4b,0x02,0x01,0x19,0x01,0x00,0x00（地址低字节）,0x10（地址高字节）,0x1b,0x00,0x03,0x4b,0x02,0x83,0x8e,0x04
0x4b,0x02,0x01,0x28,0x01,0x00,0x2a,0x00,0x6b,0x02,0x03,0x87
然后读

DDR寄存器读命令：
0x4b,0x03,0x03,0x1b,0x06,0x08,0x4b,0x03,0x03
0x80,0x00,0x40,0x4b,0x02,0x01,0x19,0x03,0x00,0x84（地址低字节0）,0x00（地址字节1）,0x00（地址字节2）,0x00（地址高字节3）,0x1b,0x00,0x03,0x4b,0x02,0x83
0x4b,0x02,0x01,0x28,0x03,0x00,0x2a,0x00,0x6b,0x02,0x03,0x87,0x8e,0x01,0x94
0x80,0x40,0x40
然后读
'''


def init_top(device):
    """Send the documented initialization byte sequence."""
    seq0 = bytes.fromhex(
        "8a 97 8d"
    )
    seq1 = bytes.fromhex(
        "80 08 0b"
    )
    seq2 = bytes.fromhex(
        "82 00 00"
    )
    seq21 = bytes.fromhex(
        "86 05 00"
    )    
    seq3 = bytes.fromhex(
        "85"
    )    
    seq4 = bytes.fromhex(
        "80 08 0b 4b 06 7f 4b 00 00 "
    )  
    seq5 = bytes.fromhex(
        "4b 03 03 1b 06 ee 4b 03 83 "
    )      
    
    _agent_log("H_INIT", "init_serdes_start", {"len": len(seq0)})
    device.write(seq0)
    device.write(seq1)
    device.write(seq2)
    device.write(seq21)
    device.write(seq3)
    device.write(seq4)
    device.write(seq5)
    _agent_log("H_INIT", "init_serdes_done", {"sent_hex": seq0.hex()})

def init_serdes(device):
    """Send the documented initialization byte sequence."""
    seq0 = bytes.fromhex(
        "8a 97 8d"
    )
    seq1 = bytes.fromhex(
        "80 08 0b"
    )
    seq2 = bytes.fromhex(
        "82 00 00"
    )
    seq21 = bytes.fromhex(
        "86 05 00"
    )    
    seq3 = bytes.fromhex(
        "85"
    )    
    seq4 = bytes.fromhex(
        "80 08 0b 4b 06 7f 4b 00 00 "
    )  
    seq5 = bytes.fromhex(
        "4b 03 03 1b 06 ee 4b 03 83 "
    )      
    seq6 = bytes.fromhex(
        "4b 03 03 1b  06 01 4b 03  03 "
    )      
    seq7 = bytes.fromhex(
        "4b 02 01 28  02 00 2a 06  6b 02 03 87 "
    )     
    
    _agent_log("H_INIT", "init_serdes_start", {"len": len(seq0)})
    device.write(seq0)
    device.write(seq1)
    device.write(seq2)
    device.write(seq21)
    device.write(seq3)
    device.write(seq4)
    device.write(seq5)
    device.write(seq6)
    device.write(seq7)
    device.read(5)
    _agent_log("H_INIT", "init_serdes_done", {"sent_hex": seq0.hex()})


def close_serdes(device):
    """Send the documented initialization byte sequence."""
    seq0 = bytes.fromhex(
        "80 08 0b 4b  06 7f 4b 00  00"
    )
    seq1 = bytes.fromhex(
        "4b 03 03 1b  06 e0 4b 03  83"
    )
   
    device.write(seq0)
    device.write(seq1)
    device.close()

'''
  45.2                              9  OUT    4b 03 03 1b  06 31 4b 03  03                        K....1K..         7.3sc  
  45.2                             16  OUT    4b 02 01 19  01 00 17 f0  1b 00 00 4b  02 03 8e 04  K..........K....  178us  
  45.2                             16  OUT    4b 02 01 19  01 00 34 12  1b 00 01 4b  02 03 8e 04  K.....4....K....  136us  
  45.1                              2  IN     32 60                                               2`                 13ms  
'''
def write_serdes_register(device, addr, value):
    """Write SERDES register using documented command sequence."""
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF
    val_low = value & 0xFF
    val_high = (value >> 8) & 0xFF

    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x31, 0x4B, 0x03, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x00, 0x4B, 0x02, 0x03, 0x8E, 0x04]
    )
    block3 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, val_low, val_high, 0x1B, 0x00, 0x01, 0x4B, 0x02, 0x03, 0x8E, 0x04]
    )

    _agent_log("H_WR", "serdes_write_start", {"addr": addr, "value": value})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    _agent_log(
        "H_WR",
        "serdes_write_done",
        {"block1": block1.hex(), "block2": block2.hex(), "block3": block3.hex()},
    )

def read_serdes_register(device, addr, read_len=2):
    """Read SERDES register; returns bytes read."""
    '''
    45.2                              9  OUT    4b 03 03 1b  06 31 4b 02  03                        K....1K..         
    45.2                             16  OUT    4b 02 01 19  01 00 1e f0  1b 00 03 4b  02 83 8e 04  K..........K....  
    45.2                             14  OUT    4b 02 01 28  01 00 2a 00  6b 02 03 87  8e 01        K..(..*.k.....    
    45.1                              6  IN     32 60 83 59  2c 25                                  2`.Y,%            
 
    '''

    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF

    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x31, 0x4B, 0x02, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83, 0x8E, 0x04]
    )
    block3 = bytes([0x4B, 0x02, 0x01, 0x28, 0x01, 0x00, 0x2A, 0x00, 0x6B, 0x02, 0x03, 0x87, 0x8e, 0x01])

    _agent_log("H_RD", "serdes_read_start", {"addr": addr, "read_len": read_len})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    data = device.read(read_len)
    data_le = data[::-1]
    device.read(2)
    _agent_log("H_RD", "serdes_read_done", {"data_hex": data.hex()})
    data=data_le.hex()
    data = int(data, 16)
    #print(hex(data))  # 0xf01e
    """
    将16位整数的比特位顺序完全反转（bit-reverse）。
    """
    # 确保输入为16位
    data &= 0xFFFF

    # 交换相邻1位
    data = ((data & 0xAAAA) >> 1) | ((data & 0x5555) << 1)
    data &= 0xFFFF

    # 交换相邻2位
    data = ((data & 0xCCCC) >> 2) | ((data & 0x3333) << 2)
    data &= 0xFFFF

    # 交换相邻4位
    data = ((data & 0xF0F0) >> 4) | ((data & 0x0F0F) << 4)
    data &= 0xFFFF

    # 交换高低字节
    data = ((data >> 8) | (data << 8)) & 0xFFFF
    return hex(data)


def read_serdes_lane_register(device, lane,addr, read_len=2):
    """Read SERDES register; returns bytes read."""
    '''
    45.2                              9  OUT    4b 03 03 1b  06 31 4b 02  03                        K....1K..         
    45.2                             16  OUT    4b 02 01 19  01 00 1e f0  1b 00 03 4b  02 83 8e 04  K..........K....  
    45.2                             14  OUT    4b 02 01 28  01 00 2a 00  6b 02 03 87  8e 01        K..(..*.k.....    
    45.1                              6  IN     32 60 83 59  2c 25                                  2`.Y,%            

    '''
    # 需要按lane计算的寄存器前缀
    LANE_BASED_PREFIXES = {
        0xE0: "serdes_lane",  # 0xE0xx -> 0xENxx
        0xC0: "common_lane",  # 0xC0xx -> 0xCNxx
    }

    addr = addr + lane * 256
    """Write SERDES register using documented command sequence."""
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF

    if addr_high in LANE_BASED_PREFIXES:
        # 计算新的高字节
        new_high = (addr_high & 0xF0) + lane
        actual_addr = (new_high << 8) | addr_low
        addr = actual_addr
    else:
        # 不需要修改
        addr
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF

    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x31, 0x4B, 0x02, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83, 0x8E, 0x04]
    )
    block3 = bytes([0x4B, 0x02, 0x01, 0x28, 0x01, 0x00, 0x2A, 0x00, 0x6B, 0x02, 0x03, 0x87, 0x8e, 0x01])

    _agent_log("H_RD", "serdes_read_start", {"addr": addr, "read_len": read_len})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    data = device.read(read_len)
    data_le = data[::-1]
    device.read(2)
    _agent_log("H_RD", "serdes_read_done", {"data_hex": data.hex()})
    data = data_le.hex()
    data = int(data, 16)
    # print(hex(data))  # 0xf01e
    """
    将16位整数的比特位顺序完全反转（bit-reverse）。
    """
    # 确保输入为16位
    data &= 0xFFFF

    # 交换相邻1位
    data = ((data & 0xAAAA) >> 1) | ((data & 0x5555) << 1)
    data &= 0xFFFF

    # 交换相邻2位
    data = ((data & 0xCCCC) >> 2) | ((data & 0x3333) << 2)
    data &= 0xFFFF

    # 交换相邻4位
    data = ((data & 0xF0F0) >> 4) | ((data & 0x0F0F) << 4)
    data &= 0xFFFF

    # 交换高低字节
    data = ((data >> 8) | (data << 8)) & 0xFFFF
    return hex(data)


def write_top_register(device, addr, value):
    """Write DDR register using documented command sequence."""
    a0 = addr & 0xFF
    a1 = (addr >> 8) & 0xFF
    a2 = (addr >> 16) & 0xFF
    a3 = (addr >> 24) & 0xFF
    v0 = value & 0xFF
    v1 = (value >> 8) & 0xFF
    v2 = (value >> 16) & 0xFF
    v3 = (value >> 24) & 0xFF

    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x08, 0x4B, 0x03, 0x03])
    block2 = bytes([0x4B, 0x02, 0x01, 0x19, 0x03, 0x00, a0, a1, a2, a3, 0x1B, 0x00, 0x00, 0x4B, 0x02, 0x03])
    block3 = bytes([0x4B, 0x02, 0x01, 0x19, 0x03, 0x00, v0, v1, v2, v3, 0x1B, 0x00, 0x01, 0x4B, 0x02, 0x03])

    _agent_log("H_WR_DDR", "ddr_write_start", {"addr": addr, "value": value})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    _agent_log(
        "H_WR_DDR",
        "ddr_write_done",
        {"block1": block1.hex(), "block2": block2.hex(), "block3": block3.hex()},
    )


def read_top_register(device, addr, read_len=4):
    """Read DDR register; returns bytes read."""
    a0 = addr & 0xFF
    a1 = (addr >> 8) & 0xFF
    a2 = (addr >> 16) & 0xFF
    a3 = (addr >> 24) & 0xFF

    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x08, 0x4B, 0x02, 0x03])
    block2 = bytes([0x4B, 0x02, 0x01, 0x19, 0x03, 0x00, a0, a1, a2, a3, 0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83])
    block3 = bytes([0x4B, 0x02, 0x01, 0x28, 0x03, 0x00, 0x2a, 0x00, 0x6B, 0x02, 0x03, 0x87, 0x8E, 0x01])
    block4 = bytes([0x80, 0x40, 0x40])

    _agent_log("H_RD_DDR", "ddr_read_start", {"addr": addr, "read_len": read_len})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    data = device.read(read_len)
    data_le = data[::-1]
    device.read(2)
    _agent_log("H_RD_DDR", "ddr_read_done", {"data_hex": data.hex()})
    return data_le


def write_serdes_lane_register(device, lane,addr, value):
    # 需要按lane计算的寄存器前缀
    LANE_BASED_PREFIXES = {
        0xE0: "serdes_lane",  # 0xE0xx -> 0xENxx
        0xC0: "common_lane",  # 0xC0xx -> 0xCNxx
    }

    addr=addr+lane*256
    """Write SERDES register using documented command sequence."""
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF

    if addr_high in LANE_BASED_PREFIXES:
        # 计算新的高字节
        new_high = (addr_high & 0xF0) + lane
        actual_addr = (new_high << 8) | addr_low
        addr=actual_addr
    else:
        # 不需要修改
        addr
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF
    val_low = value & 0xFF
    val_high = (value >> 8) & 0xFF
    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x31, 0x4B, 0x03, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x00, 0x4B, 0x02, 0x03, 0x8E, 0x04]
    )
    block3 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, val_low, val_high, 0x1B, 0x00, 0x01, 0x4B, 0x02, 0x03, 0x8E, 0x04]
    )

    _agent_log("H_WR", "serdes_write_start", {"addr": addr, "value": value})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    _agent_log(
        "H_WR",
        "serdes_write_done",
        {"block1": block1.hex(), "block2": block2.hex(), "block3": block3.hex()},
    )
    #print(read_serdes_register(device,addr))


def write_serdes_bit_reg(device, lane, addr, startbit, endbit, value):
    """
    将寄存器 addr 中从 startbit 到 endbit（包含）的位域设置为 value。
    参数：
        device: 设备对象
        lane: 通道号（0~3）
        addr: 寄存器地址（lane0的基地址，如 0xf01e）
        startbit: 起始位（低位）
        endbit: 结束位（高位）
        value: 要设置的值，应小于 2^(endbit-startbit+1)
    """
    # 确保 startbit <= endbit
    if startbit > endbit:
        startbit, endbit = endbit, startbit

    # 1. 读取当前寄存器值（假设已有 read_serdes_lane_register 函数）
    current = read_serdes_register(device, addr)
    current = int(current, 16)



    # 2. 构造掩码
    width = endbit - startbit + 1
    mask = ((1 << width) - 1) << startbit

    # 3. 清除目标位，并设置新值
    current = (current & ~mask) | ((value << startbit) & mask)
    # 确保输入为16位
    current &= 0xFFFF

    # 交换相邻1位
    current = ((current & 0xAAAA) >> 1) | ((current & 0x5555) << 1)
    current &= 0xFFFF

    # 交换相邻2位
    current = ((current & 0xCCCC) >> 2) | ((current & 0x3333) << 2)
    current &= 0xFFFF

    # 交换相邻4位
    current = ((current & 0xF0F0) >> 4) | ((current & 0x0F0F) << 4)
    current &= 0xFFFF

    # 交换高低字节
    current = ((current >> 8) | (current << 8)) & 0xFFFF

    # 4. 写入新值
    write_serdes_lane_register(device, lane, addr, current)

def write_serdes_register_32b(device, addr, value):
    device.purge(0x1)
    """Write SERDES register using documented command sequence."""
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF
    val_low = value & 0xFF
    val_middle1 = (value >> 8) & 0xFF
    val_middle2 = (value >> 16) & 0xFF
    val_high = (value >> 24) & 0xFF
    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x15, 0x4B, 0x03, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x00, 0x4B, 0x02, 0x03, 0x8E, 0x04]
    )
    block3 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x03, 0x00, val_low, val_middle1, val_middle2,val_high, 0x1b, 0x00, 0x01, 0x4b, 0x02, 0x03]
    )

    _agent_log("H_WR", "serdes_write_start", {"addr": addr, "value": value})
    device.write(block1)
    device.write(block2)
    device.write(block3)

    _agent_log(
        "H_WR",
        "serdes_write_done",
        {"block1": block1.hex(), "block2": block2.hex(), "block3": block3.hex()},
    )


def soc_debug( port='COM21', baudrate=115200):
    try:
        # 初始化串口
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        flag=0
        top_sequences=["1004b062000410000000","1104b0620004",
                       "1004b04048e0040f7f00","1104b04048e0",
                       "1004b04048d000000000","1104b04048d0"]
        for i, seq in enumerate(top_sequences, 1):
            byte_data = bytes.fromhex(seq)
            ser.write(byte_data)
            # 根据前缀决定是否读取响应
            if seq.startswith('1104'):
                time.sleep(0.2)
                response = ser.read_all()
                if response:
                    big_endian_value = int.from_bytes(response[:4], byteorder='big')  # 大端解析
                    little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')  # 转为小端字节
                    print(f"接收数据: {little_endian_bytes.hex()}")
                else:
                    print("[警告] 未收到响应数据")
                    print("soc init failed")
                    flag = 1
                    break

        if(flag==0):
            print("===========debug success==========")
    except serial.SerialException as e:
        print(f"[错误] 串口通信异常: {e}")
        exit()
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n[状态] 串口已安全关闭")


def soc_debug1( port='COM21', baudrate=115200):
    try:
        # 初始化串口
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        flag=0
        top_sequences=["1004b0620b1430000000","1104b0620b14",]
        for i, seq in enumerate(top_sequences, 1):
            byte_data = bytes.fromhex(seq)
            ser.write(byte_data)
            # 根据前缀决定是否读取响应
            if seq.startswith('1104'):
                time.sleep(0.2)
                response = ser.read_all()
                if response:
                    big_endian_value = int.from_bytes(response[:4], byteorder='big')  # 大端解析
                    little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')  # 转为小端字节
                    print(f"接收数据: {little_endian_bytes.hex()}")
                else:
                    print("[警告] 未收到响应数据")
                    print("soc init failed")
                    flag = 1
                    break

        if(flag==0):
            print("===========debug success==========")
    except serial.SerialException as e:
        print(f"[错误] 串口通信异常: {e}")
        exit()
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n[状态] 串口已安全关闭")



def soc_debug2( port='COM21', baudrate=115200):
    try:
        # 初始化串口
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        flag=0
        top_sequences=["1004b060000802000000","1104b0600008",]
        for i, seq in enumerate(top_sequences, 1):
            byte_data = bytes.fromhex(seq)
            ser.write(byte_data)
            # 根据前缀决定是否读取响应
            if seq.startswith('1104'):
                time.sleep(0.2)
                response = ser.read_all()
                if response:
                    big_endian_value = int.from_bytes(response[:4], byteorder='big')  # 大端解析
                    little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')  # 转为小端字节
                    print(f"接收数据: {little_endian_bytes.hex()}")
                else:
                    print("[警告] 未收到响应数据")
                    print("soc init failed")
                    flag = 1
                    break

        if(flag==0):
            print("===========debug success==========")
    except serial.SerialException as e:
        print(f"[错误] 串口通信异常: {e}")
        exit()
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n[状态] 串口已安全关闭")


def uartm_init(port='COM21', baudrate=115200):
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1
    )
    return ser

def write_uartm(sequences,ser):
    for i, seq in enumerate(sequences, 1):
        byte_data = bytes.fromhex(seq)
        ser.write(byte_data)
        time.sleep(0.1)
        if seq.startswith('1104'):
            time.sleep(0.2)
            response = ser.read_all()
            if response:
                big_endian_value = int.from_bytes(response[:4], byteorder='big')  # 大端解析
                little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')  # 转为小端字节
                print(f"接收数据: {little_endian_bytes.hex()}")
                #return little_endian_bytes.hex()
            else:
                print("[警告] 未收到响应数据")
                print("soc init failed")
                ser.close()
                print("===========串口已安全关闭==========")
                break



def read_uartm(sequences,ser):
    for i, seq in enumerate(sequences, 1):
        byte_data = bytes.fromhex(seq)
        ser.write(byte_data)
        time.sleep(0.1)
        if seq.startswith('1104'):
            time.sleep(0.2)
            response = ser.read_all()
            if response:
                big_endian_value = int.from_bytes(response[:4], byteorder='big')  # 大端解析
                little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')  # 转为小端字节
                print(f"接收数据: {little_endian_bytes.hex()}")
                return little_endian_bytes.hex()
            else:
                print("[警告] 未收到响应数据")
                print("soc init failed")
                ser.close()
                print("===========串口已安全关闭==========")
                break


def soc_init( port='COM21', baudrate=115200):
    try:
        # 初始化串口
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
        flag=0
        top_sequences=["1104b0404850","1004b04048e0040f7F00","1104b04048e0",
                       "1004b04048d000000000","1104b04048d0","1004b04048ccFFFFBC2b","1104b04048CC"]
        for i, seq in enumerate(top_sequences, 1):
            byte_data = bytes.fromhex(seq)
            ser.write(byte_data)
            # 根据前缀决定是否读取响应
            if seq.startswith('1104'):
                time.sleep(0.2)
                response = ser.read_all()
                if response:
                    big_endian_value = int.from_bytes(response[:4], byteorder='big')  # 大端解析
                    little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')  # 转为小端字节
                    print(f"接收数据: {little_endian_bytes.hex()}")
                else:
                    print("[警告] 未收到响应数据")
                    print("soc init failed")
                    flag = 1
                    break

        if(flag==0):
            print("===========soc init success==========")
    except serial.SerialException as e:
        print(f"[错误] 串口通信异常: {e}")
        exit()
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n[状态] 串口已安全关闭")


def phy_init(device1):
    print("Verifying serdes...")
    init_serdes(device1)
    # value = read_serdes_register(device1,0, 0xf01e)
    # print("0xf01e:", value)
    # if (value == "0x4967"):
    #     print("环境没有问题！！！")
    # else:
    #     print("环境有问题！！！")
    #     exit()



def write_serdes_bit_reg(device, lane, addr, startbit, endbit, value):
    """
    将寄存器 addr 中从 startbit 到 endbit（包含）的位域设置为 value。
    参数：
        device: 设备对象
        lane: 通道号（0~3）
        addr: 寄存器地址（lane0的基地址，如 0xf01e）
        startbit: 起始位（低位）
        endbit: 结束位（高位）
        value: 要设置的值，应小于 2^(endbit-startbit+1)
    """
    # 确保 startbit <= endbit
    if startbit > endbit:
        startbit, endbit = endbit, startbit

    # 1. 读取当前寄存器值（假设已有 read_serdes_lane_register 函数）
    current = read_serdes_register(device, addr)
    current = int(current, 16)



    # 2. 构造掩码
    width = endbit - startbit + 1
    mask = ((1 << width) - 1) << startbit

    # 3. 清除目标位，并设置新值
    current = (current & ~mask) | ((value << startbit) & mask)
    # 确保输入为16位
    current &= 0xFFFF

    # 交换相邻1位
    current = ((current & 0xAAAA) >> 1) | ((current & 0x5555) << 1)
    current &= 0xFFFF

    # 交换相邻2位
    current = ((current & 0xCCCC) >> 2) | ((current & 0x3333) << 2)
    current &= 0xFFFF

    # 交换相邻4位
    current = ((current & 0xF0F0) >> 4) | ((current & 0x0F0F) << 4)
    current &= 0xFFFF

    # 交换高低字节
    current = ((current >> 8) | (current << 8)) & 0xFFFF

    # 4. 写入新值
    write_serdes_lane_register(device, lane, addr, current)

def read_serdes_bit_reg(device,lane, addr, startbit, endbit):
    """
    读取寄存器 addr 中从 startbit 到 endbit（包含）的位域值。

    参数：
        device: 设备对象
        lane: 通道号（0~3）
        addr: 寄存器地址（lane0的基地址，如 0xf01e）
        startbit: 起始位（低位）
        endbit: 结束位（高位）

    返回：
        指定位段的整数值（例如 0~3）
    """
    # 确保 startbit <= endbit
    if startbit > endbit:
        startbit, endbit = endbit, startbit

    # 1. 读取当前寄存器值
    current = read_serdes_lane_register(device, lane,addr)
    current = int(current, 16)
    # 2. 提取指定位段
    width = endbit - startbit + 1
    mask = (1 << width) - 1
    bit_value = (current >> startbit) & mask

    return bit_value

def configure_from_txt(txt_file, device):
        """
        从文件读取并配置寄存器
        支持两种格式：
        1. 原有格式：地址,值  （例如：0xe01f,0x0005）
        2. wr格式：wr 地址,值  或 wr 地址 值 （例如：wr d02f,0000 或 wr d02f 0000）
        """
        with open(txt_file, 'r',encoding="UTF-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith('//') or line.startswith('#'):
                continue

            # 处理延迟
            if line.startswith('delay'):
                parts = line.split()
                if len(parts) > 1:
                    delay_ms = int(parts[1])
                    time.sleep(delay_ms / 1000.0)
                continue

            # 处理寄存器配置
            # 1. 处理 wr 格式
            if line.startswith('wr'):
                # 移除 'wr ' 前缀
                content = line[2:].strip()

                # 支持逗号分隔或空格分隔
                if ',' in content:
                    parts = content.split(',')
                    addr_str = parts[0].strip()
                    value_str = parts[1].strip()
                else:
                    parts = content.split()
                    if len(parts) >= 2:
                        addr_str = parts[0]
                        value_str = parts[1]
                    else:
                        print(f"警告：无效的wr格式: {line}")
                        continue

                # 处理地址和值，添加0x前缀（如果没有）
                if not addr_str.startswith('0x'):
                    addr_str = '0x' + addr_str
                if not value_str.startswith('0x'):
                    value_str = '0x' + value_str

                try:
                    addr = int(addr_str, 16)
                    value = int(value_str, 16)
                    write_serdes_register(device,  addr, value)  # lane参数可根据需要调整
                    print(f"配置: addr=0x{addr:04X}, value=0x{value:04X}")
                except ValueError as e:
                    print(f"解析失败: {line} - {e}")
                continue

            # 2. 处理原有的 "地址,值" 格式
            if ',' in line:
                try:
                    # 分割地址和值
                    parts = line.split(',')
                    addr_str = parts[0].strip()
                    value_str = parts[1].strip()

                    # 确保有0x前缀
                    if not addr_str.startswith('0x'):
                        addr_str = '0x' + addr_str
                    if not value_str.startswith('0x'):
                        value_str = '0x' + value_str

                    addr = int(addr_str, 16)
                    value = int(value_str, 16)
                    write_serdes_register(device,  addr, value)
                    print(f"配置: addr=0x{addr:04X}, value=0x{value:04X}")
                except ValueError as e:
                    print(f"解析失败: {line} - {e}")
                continue


def parse_register_txt(txt_file, lane):
    """
    解析txt文件，返回每个寄存器的信息（注释、实际地址、位段范围）
    """
    results = []
    current_comment = []

    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 注释行
        if line.startswith('//'):
            comment = line[2:].strip()
            if comment:
                current_comment.append(comment)
            continue

        # 寄存器行，格式如 "0xf077[9:0]" 或 "0xEN5c[9:0]"
        match = re.match(r'(0x[0-9a-fA-FNM]+)\[(\d+):(\d+)\]', line)
        if not match:
            continue

        addr_str = match.group(1)
        high_bit = int(match.group(2))
        low_bit = int(match.group(3))

        # 处理占位符 N 或 M
        if 'N' in addr_str:
            replace_val = lane * 2  # 0,2,4,6
            actual_addr_str = addr_str.replace('N', format(replace_val, 'x'))
        elif 'M' in addr_str:
            replace_val = lane * 2 + 1  # 1,3,5,7
            actual_addr_str = addr_str.replace('M', format(replace_val, 'x'))
        else:
            actual_addr_str = addr_str

        actual_addr = int(actual_addr_str, 16)
        comment = ' '.join(current_comment) if current_comment else ''

        results.append({
            'comment': comment,
            'addr_str': line,
            'actual_addr': actual_addr,
            'high_bit': high_bit,
            'low_bit': low_bit
        })

        current_comment = []  # 清空注释，准备下一个寄存器

    return results


def read_register_bits_from_txt(txt_file, device, lane):
    """
    从txt文件读取每个寄存器的指定位段值，返回带注释的结果列表
    """
    parsed = parse_register_txt(txt_file, lane)
    results = []

    for item in parsed:
        raw_value = read_serdes_reg(device, lane, item['actual_addr'])
        raw_value = int(raw_value, 16)
        high = item['high_bit']
        low = item['low_bit']
        width = high - low + 1
        mask = (1 << width) - 1
        bit_value = (raw_value >> low) & mask

        results.append({
            'comment': item['comment'],
            'addr_str': item['addr_str'],
            'actual_addr': item['actual_addr'],
            'high_bit': high,
            'low_bit': low,
            'raw_value': raw_value,
            'bit_value': bit_value
        })

    return results


def read_serdes_reg(device, addr,read_len=2):
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF
    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x31, 0x4B, 0x02, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83, 0x8E, 0x04]
    )
    block3 = bytes([0x4B, 0x02, 0x01, 0x28, 0x01, 0x00, 0x2A, 0x00, 0x6B, 0x02, 0x03, 0x87, 0x8e, 0x01])

    _agent_log("H_RD", "serdes_read_start", {"addr": addr, "read_len": read_len})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    data = device.read(read_len)
    data_le = data[::-1]
    device.read(2)
    _agent_log("H_RD", "serdes_read_done", {"data_hex": data.hex()})
    data = data_le.hex()
    data = int(data, 16)

    """
    将16位整数的比特位顺序完全反转（bit-reverse）。
    """
    # 确保输入为16位
    data &= 0xFFFF

    # 交换相邻1位
    data = ((data & 0xAAAA) >> 1) | ((data & 0x5555) << 1)
    data &= 0xFFFF

    # 交换相邻2位
    data = ((data & 0xCCCC) >> 2) | ((data & 0x3333) << 2)
    data &= 0xFFFF

    # 交换相邻4位
    data = ((data & 0xF0F0) >> 4) | ((data & 0x0F0F) << 4)
    data &= 0xFFFF

    # 交换高低字节
    data = ((data >> 8) | (data << 8)) & 0xFFFF
    return hex(data)


def write_32bit_data_from_txt(txt_file, device, start_addr=0, step=1, delay_ms=1):
    """
    从文本文件读取32位十六进制数据，并依次写入从 start_addr 开始的连续寄存器。
    每行一个32位十六进制数（可带0x前缀或不带）。
    """
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    total = len(lines)
    for idx, line in enumerate(lines):
        try:
            value = int(line, 16) & 0xFFFFFFFF
            addr = start_addr + idx * step
            print(f"[{idx+1}/{total}] 写入地址 0x{addr:04X}: 0x{value:08X}...", end='', flush=True)
            write_serdes_register_32b(device, addr, value)
            # read_serdes_register_32bit(device, addr)
            print("完成")
        except ValueError as e:
            print(f"\n跳过无效行: {line} ({e})")
        except Exception as e:
            print(f"\n写入失败: {e}")
            break  # 可选择停止或继续


def read_serdes_register_32bit(device, addr, timeout_ms=100):
    """
    通过FTDI JTAG从SerDes寄存器读取32位数据（地址为16位）。

    参数:
        device: 已打开的ftd2xx设备对象
        addr: 16位寄存器地址（整数）
        timeout_ms: 超时时间（毫秒）

    返回:
        读取到的32位整数值
    """
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF
    block1 = bytes([0x4B, 0x03, 0x03, 0x1B, 0x06, 0x15, 0x4B, 0x02, 0x03])
    block2 = bytes(
        [0x4B, 0x02, 0x01, 0x19, 0x01, 0x00, addr_low, addr_high, 0x1B, 0x00, 0x03, 0x4B, 0x02, 0x83, 0x8E, 0x04]
    )
    block3 = bytes([0x4B, 0x02, 0x01, 0x28, 0x03, 0x00, 0x2A, 0x00, 0x6B, 0x02, 0x03, 0x87, 0x8e, 0x01])

    _agent_log("H_RD", "serdes_read_start", {"addr": addr, "read_len": 4})
    device.write(block1)
    device.write(block2)
    device.write(block3)
    #data = device.read(2)
    data = device.read(4)
    value = int.from_bytes(data, byteorder='little')
    print(hex(value))
    # data_le = data[::-1]
    # _agent_log("H_RD", "serdes_read_done", {"data_hex": data.hex()})
    # data = data_le.hex()
    # data = int(data, 32)
    #print(hex(data))  # 0xf01e


def get_com_port_for_channel(channel_letter='C'):
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





def read_uartm_from_txt(txt_path: str, ser: serial.Serial):
        """
        从 txt 文件中读取命令，每条命令为十六进制字符串（如 "1004b000089001200220"）。
        自动区分写命令（1004开头）和读命令（1104开头），执行对应的串口操作。
        """
        # 读取所有非空、非注释行
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        for i, seq in enumerate(lines, 1):
            print(f"\n--- 处理第 {i} 条命令: {seq} ---")
            # 转换为字节并发送
            byte_data = bytes.fromhex(seq)
            ser.write(byte_data)
            print(f"发送: {seq}")

            # 如果是读命令（1104开头），需要读取响应
            if seq.startswith('1104'):
                time.sleep(0.2)  # 等待设备响应
                response = ser.read_all()
                if response:
                    # 取前 4 字节，按大端解析为整数
                    big_endian_value = int.from_bytes(response[:4], byteorder='big')
                    # 转换为小端字节序的十六进制字符串
                    little_endian_bytes = big_endian_value.to_bytes(4, byteorder='little')
                    print(f"接收原始数据: {response.hex()}")
                    print(f"解析结果（小端十六进制）: {little_endian_bytes.hex()}")
                else:
                    print("【警告】未收到响应数据")
                    print("SOC init failed")
                    ser.close()
                    print("==========串口已安全关闭==========")
                    break  # 读失败则终止整个流程
            else:
                # 写命令只发送，不等待响应（也可视情况加短延时）
                time.sleep(0.1)

            # 可根据需要增加命令间延时
            time.sleep(0.05)


import serial
import time

def read_uartm_bit_reg(ser: serial.Serial, addr_hex: str, startbit: int, endbit: int, byteorder: str = 'big') -> int | None:
    """
    从指定地址读取一个寄存器（4字节），并提取 [startbit, endbit] 范围内的位值。

    参数:
        ser:       已打开的 pySerial 对象
        addr_hex:  地址部分，例如 "b0000890" (将拼接为 "1104b0000890")
        startbit:  起始位索引（LSB=0）
        endbit:    结束位索引（包含）
        byteorder: 响应数据的字节序，'big' 或 'little'，默认 'big'

    返回:
        提取出的整数值；若读取失败或无响应则返回 None
    """
    # 1. 构造读命令
    cmd = f"1104{addr_hex}"
    print(f"[读命令] 发送: {cmd}")

    # 2. 发送命令
    ser.write(bytes.fromhex(cmd))
    time.sleep(0.2)          # 等待设备响应

    # 3. 读取响应
    response = ser.read_all()
    if not response:
        print("[警告] 未收到响应数据")
        return None

    # 只取前4字节（假设寄存器数据长度为4字节）
    if len(response) < 4:
        print(f"[警告] 响应数据不足4字节: {response.hex()}")
        return None

    data_bytes = response[:4]
    print(f"[接收原始] {data_bytes.hex()}")

    # 4. 根据字节序转换为整数
    if byteorder == 'big':
        reg_value = int.from_bytes(data_bytes, byteorder='big')
    else:
        reg_value = int.from_bytes(data_bytes, byteorder='little')

    print(f"[寄存器完整值] 0x{reg_value:08X} ({reg_value})")

    # 5. 提取位域
    if startbit > endbit:
        raise ValueError("startbit 必须 <= endbit")
    bit_len = endbit - startbit + 1
    mask = ((1 << bit_len) - 1) << startbit
    bit_value = (reg_value & mask) >> startbit

    print(f"[位域提取] bits[{startbit}:{endbit}] = {bit_value} (0x{bit_value:X})")
    return bit_value

