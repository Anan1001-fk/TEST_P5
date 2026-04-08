import time
import pyvisa


address="TCPIP0::192.254.202.8::hislip0::INSTR"
resourceManager = pyvisa.ResourceManager()
time.sleep(0.05)
instance = resourceManager.open_resource(address)
time.sleep(0.05)


def init():
    instr = instance.query("*IDN?")
    print(instr)
    print("仪器连接成功")

def sj1_output(state):
    instance.write(f":UENTry:ID 1; :MODule:ID 4; :SOURce:JITTer:SJ:ENABle {state}")
    time.sleep(0.01)

def sj1_setfreq(freq):
    # unit Mhz
    freq=freq*1e6
    instance.write(f":UENTry:ID 1; :MODule:ID 4; :SOURce:JITTer:SJ:FREQuency {freq}")
    print(f"*********==========此时设定的幅度是{freq}hz=========*************")
    time.sleep(0.1)

def sj1_setamp(amp):
    amp=amp/100
    instance.write(f":UENTry:ID 1; :MODule:ID 4; :SOURce:JITTer:SJ:AMPLitude {amp}")
    print(f"*********==========此时设定的幅度是{amp}UI=========*************")
    time.sleep(0.2)



if __name__ == "__main__":
    init()
    sj1_output("ON")
    sj1_setfreq(1)
    sj1_setamp(7/10)