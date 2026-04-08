import time

import pyvisa


address="USB0::0x1AB1::0x0E11::DP8C162851463::INSTR"
resourceManager = pyvisa.ResourceManager()
time.sleep(0.05)
instance = resourceManager.open_resource(address)
time.sleep(0.05)
def init(address):
    # resourceManager = pyvisa.ResourceManager()
    # instance = resourceManager.open_resource(address)
    instr=instance.query("*IDN?")
    print(instr)
    print("仪器连接成功")

def reset():
    # resourceManager = pyvisa.ResourceManager()
    # instance = resourceManager.open_resource(address)
    instance.write("*RST")
    print("仪器复位成功")

def output(channel,state):
    # resourceManager = pyvisa.ResourceManager()
    # time.sleep(0.01)
    # instance = resourceManager.open_resource(address)
    # time.sleep(0.01)
    instance.write(f":OUTP CH{channel},{state}")
    time.sleep(0.01)
def get_voltage(channel):
    # resourceManager = pyvisa.ResourceManager()
    # time.sleep(0.01)
    # instance = resourceManager.open_resource(address)
    # time.sleep(0.01)
    volt=instance.query(f":MEAS? CH{channel}")
    time.sleep(0.01)
    return float(volt)
def get_current(channel):
    # resourceManager = pyvisa.ResourceManager()
    # time.sleep(0.01)
    # instance = resourceManager.open_resource(address)
    # time.sleep(0.01)
    current=instance.query(f":MEAS:CURR? CH{channel}")
    time.sleep(0.01)
    return float(current)

def set_voltage_current(channel,voltage,current):
    # resourceManager = pyvisa.ResourceManager()
    # time.sleep(0.01)
    # instance = resourceManager.open_resource(address)
    # time.sleep(0.01)
    instance.write(f":APPL CH{channel},{voltage},{current}")
    time.sleep(0.01)

if __name__ == '__main__':

    init(address)
    while True:
        output(3,"OFF")
        time.sleep(1)
        output(3, "ON")
        time.sleep(1)
