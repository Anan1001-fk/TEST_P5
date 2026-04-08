def test():
    addr=0
    value=0x12345678
    addr_low = addr & 0xFF
    addr_high = (addr >> 8) & 0xFF
    val_low = value & 0xFF
    val_middle1 = (value >> 8) & 0xFF
    val_middle2 = (value >> 16) & 0xFF
    val_high = (value >> 24) & 0xFF
    print(hex(addr))
    print(hex(addr_high))
    print(hex(val_low))
    print(hex(val_middle1))
    print(hex(val_middle2))
    print(hex(val_high))


if __name__ == '__main__':
    test()