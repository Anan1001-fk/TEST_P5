import pyvisa
import time


class E8257D(object):
    def __init__(self, addr="TCPIP0::169.254.184.140::inst0::INSTR"):
        rm = pyvisa.ResourceManager()
        self.uxr_id = rm.open_resource(addr)
        self.uxr_id.write_termination = "\n"
        self.uxr_id.read_termination = "\n"
        self.uxr_id.timeout = 20000

    def get_id(self):
        """Returns the instrument identification code to check whether the remote communication is normal
        """
        cmd = "*IDN?"
        print(self.uxr_id.query(cmd))

    def output_state(self,state):
        cmd = f":POWer:STATe {state}"
        return self.uxr_id.write(cmd)

    def set_frequency(self,frequency):
        cmd = f":FREQuency:FIXed {frequency}GHz"
        self.uxr_id.write(cmd)
        print(f"此时设定的频率是{frequency}Ghz")

    def set_amplitude(self,amplitude,unit):
        cmd = f":POWer:AMPLitude {amplitude}{unit}"
        self.uxr_id.write(cmd)
        print("此时设定的幅度是",amplitude,unit)

if __name__ == "__main__":
    uxr = E8257D("TCPIP0::192.168.1.11::inst0::INSTR")
    uxr.get_id()
    uxr.set_frequency(16)
    uxr.set_amplitude(52,"mv")
    uxr.output_state("ON")

