#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试SDK Drive层的Python示例"""

import sys

from retimer_sdk_drive import BIF_NAMES, LINK_NAMES, LTSSM_NAMES, RetimerSDKDrive




def main():
    """主测试函数"""
    print("=" * 60)
    print("Retimer SDK Drive 测试程序")
    print("=" * 60)
    
    try:
        # 创建SDK Drive实例
        sdk = RetimerSDKDrive()
        
        # 设置日志级别 (2=INFO)
        sdk.lib.retimer_set_log_level(2)
        
        # 1. 枚举设备
        print("\n1. 枚举设备...")
        devices = sdk.enumerate_devices()
        print(f"   找到 {len(devices)} 个设备:")
        for i, dev in enumerate(devices):
            print(f"   [{i}] Type={dev['type']}, Port={dev['port']}, "
                  f"Status={dev['status']}, Desc={dev['description']}")
        
        if len(devices) == 0:
            print("   未找到设备，退出测试")
            return
        
        # 2. 打开设备
        print("\n2. 打开设备...")
        handle = sdk.open_device(
            adapter_type=devices[0]['type'],
            port=devices[0]['port'],
            slave_addr=0x20,
            bitrate_khz=800,
            pec_enable=True,
            chip_version=1  # 1=NTO
        )
        print(f"   设备已打开: handle={handle}")
        
        try:

            # 4. 读取寄存器
            print("\n4. 读取寄存器...")
            value = sdk.read_reg32(handle, 0x5800c044)
            print(f"   Register[0x58510224] = 0x{value:08X}")

            print("\n4. 写寄存器...")
            value = sdk.write_reg32(handle, 0x5800c044, 0x01)
            print(f"   Register[0x58510224] = 0x{value:08X}")
            
            print("\n测试完成!")

        finally:
            # 8. 关闭设备
            print("\n8. 关闭设备...")
            sdk.close_device(handle)
            print("   设备已关闭")
    
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

