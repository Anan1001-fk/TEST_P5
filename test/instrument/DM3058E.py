import time

import pyvisa

class Dm3058e(object):
    def __init__(self,address):
        rm = pyvisa.ResourceManager()
        time.sleep(0.05)
        self.instance = rm.open_resource(address)
        time.sleep(0.05)
        instr = self.instance.query("*IDN?")
        print(instr.strip())
        print("仪器连接成功")

    def reset(self):
        self.instance.write("*RST")
        print("仪器复位成功")
        time.sleep(3)

    def get_voltage(self):
        time.sleep(1)
        volt = self.instance.query(f":MEASure:VOLTage:DC?")
        time.sleep(1)
        volt = round(float(volt), 3)
        return volt




if __name__=="__main__":
    dm2 = Dm3058e(address="USB0::0x1AB1::0x09C4::DM3R261200875::INSTR")
