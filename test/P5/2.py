from pyftdi.ftdi import Ftdi

from ftd2jtag.jtag_reg_op import  *
from ftd2jtag.ftd2jtag import *
import datetime
import serial
import time

from pyftdi.jtag import JtagEngine




def configure_from_txt(txt_file, device, lane):
    """
    从TXT文件读取并配置寄存器

    参数:
        txt_file: TXT文件路径
        device: 设备对象
        lane: 通道号
    """
    with open(txt_file, 'r') as f:
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

        # 处理寄存器配置 (格式: 地址,值)
        if ',' in line:
            try:
                # 分割地址和值
                addr_str, value_str = line.split(',')

                # 转换为十六进制整数
                addr = int(addr_str.strip(), 16)
                value = int(value_str.strip(), 16)

                # 写入寄存器
                write_serdes_lane_register(device, lane, addr, value)
                time.sleep(0.005)
                value0=read_serdes_register(device, addr)
                print(f"addr=0x{addr:04X},{value0}")
                print(f"配置: lane={lane}, addr=0x{addr:04X}, value=0x{value:04X}")


            except ValueError as e:
                print(f"解析行失败 '{line}': {e}")


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




if __name__=="__main__":
    test_start_time = datetime.datetime.now()
    print(f"测试开始时间: {test_start_time}")
    port = get_com_port_for_channel("C")
    baudrate = 115200
    #ser = uartm_init(port=port, baudrate=baudrate)
    soc_init(port=port, baudrate=115200)
    # datawidth = ["1004b00008c0c4000000", "1004b00008c0c2000000", "1004b00008c0c1000000"]
    # write_uartm(datawidth, ser)
    # for i in datawidth:
    #     write_uartm([i], ser)
    FTDI_CABLE_SERDES = b"A"  #
    device1 = setup_device(FTDI_CABLE_SERDES)
    print("Verifying serdes...")
    init_serdes(device1)
    write_serdes_bit_reg(device1,0,0xe115,1,7,17)
    value=read_serdes_bit_reg(device1,0,0xe115,1,7)
    print("0xf01e:", value)
    if (value == "0x4967"):
        print("环境没有问题！！！")
    else:
        print("环境有问题！！！")
        exit()

    txt_file = "phy_init_cal_eq_code_rd(1).txt"

    results = read_register_bits_from_txt(txt_file, device1, 1)

    for r in results:
        print(f"注释: {r['comment']}")
        print(f"地址: {r['addr_str']} -> 实际: 0x{r['actual_addr']:04X}")
        print(f"位段 [{r['high_bit']}:{r['low_bit']}]")
        print(f"原始值: 0x{r['raw_value']:04X}, 位段值: {r['bit_value']} (0x{r['bit_value']:X})")
        print()
    close_serdes(device1)
