from ftd2jtag.jtag_reg_op import  *

import winsound
from ftd2jtag.jtag_reg_op import  *
from ftd2jtag.ftd2jtag import *

import datetime

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
                print(f"配置: lane={lane}, addr=0x{addr:04X}, value=0x{value:04X}")

            except ValueError as e:
                print(f"解析行失败 '{line}': {e}")


def initial_top(device):
    print("==============初始化top================")
    print("Verifying top...")
    init_top(device)

    '''
    [16:24:06.690] 读取成功 -> 地址: 0xb1204800, 数据: 0x20240821
    [16:24:06.691] 读取成功 -> 地址: 0xb1204804, 数据: 0x22334455
    [16:24:06.691] 读取成功 -> 地址: 0xb12048ac, 数据: 0x00000003
    [16:24:06.693] 读取成功 -> 地址: 0xb1204818, 数据: 0x00000001
    [16:24:06.693] 读取成功 -> 地址: 0xb1204848, 数据: 0x134d04d3
    [16:24:06.693] 读取成功 -> 地址: 0xb1204824, 数据: 0x02000000
    '''

    write_top_register(device, 0xb12048ac, 0x3)
    write_top_register(device, 0xb1204818, 0x1)
    write_top_register(device, 0xb1204848, 0x134d04d3)
    write_top_register(device, 0xb1204824, 0x2000000)

    print("0xb1204800:", read_top_register(device, 0xb1204800).hex())
    print("0xb1204804:", read_top_register(device, 0xb1204804).hex())
    print("0xb12048ac:", read_top_register(device, 0xb12048ac).hex())
    print("0xb1204818:", read_top_register(device, 0xb1204818).hex())
    print("0xb1204848:", read_top_register(device, 0xb1204848).hex())
    print("0xb1204824:", read_top_register(device, 0xb1204824).hex())

    print("==============top初始化成功================")
    time.sleep(0.1)
    print("==============*************************================")

def initial_serdes(device1):
    print("Verifying serdes...")
    init_serdes(device1)
    value = read_serdes_register(device1, 0xf01e).hex()
    print("0xf01e:", value)
    if (value == "5983"):
        print("环境没有问题！！！")
    else:
        print("环境有问题！！！")
        exit()

if __name__ == '__main__':
    test_start_time = datetime.datetime.now()
    print(f"测试开始时间: {test_start_time}")
    FTDI_CABLE_SERDES = b"A"  #
    FTDI_CABLE_TOP = b"B"  # fixme 设备名称，需要过滤出支持的设备列表供选择，或手动输入名称
    device = setup_device(FTDI_CABLE_TOP)
    device1 = setup_device(FTDI_CABLE_SERDES)
    initial_top(device)
    initial_serdes(device1)
    txt_file = '16G_config_prbs7.txt'
    configure_from_txt(txt_file,device1,0)
    print("rx_det", read_serdes_register(device1, 0xe00f).hex())
    write_serdes_lane_register(device1, 0, 0xe01e, 0xb099)
    print(read_serdes_register(device1, 0xe01e).hex())
    write_serdes_lane_register(device1, 0, 0xe01e, 0xb089)
    print(read_serdes_register(device1, 0xe11e).hex())
    write_serdes_lane_register(device1, 0, 0xe01e, 0xf089)
    print(read_serdes_register(device1, 0xe01e).hex())
    print("rx_det", read_serdes_register(device1, 0xe00f).hex())
    write_serdes_lane_register(device1, 0, 0xe01e, 0xb089)
    print(read_serdes_register(device1, 0xe01e).hex())
