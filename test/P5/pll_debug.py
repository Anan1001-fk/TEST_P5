from ftd2jtag.jtag_reg_op import  *
def test():
    com_c = get_com_port_for_channel("C")
    port = com_c
    baudrate = 115200
    ser = uartm_init(port=port, baudrate=baudrate)

    part1 = ["1004b04048a000090900", "1104b04048a0",
             "1004b040483c01020000", "1104b0404828",
             "1004b04048a000050600", "1104b04048a0",
             ]
    write_uartm(part1, ser)

if __name__ == "__main__":
    test()