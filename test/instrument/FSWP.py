import time

import pyvisa


address="TCPIP0::169.254.169.8::inst0::INSTR"
resourceManager = pyvisa.ResourceManager()
time.sleep(0.05)
instance = resourceManager.open_resource(address)
time.sleep(0.05)

def init():
    instr=instance.query("*IDN?")
    print(instr.strip())
    print("仪器连接成功")

def reset():
    instance.write("*RST")
    print("仪器复位成功")
    instance.query("*OPC?")

def get_mark_y():
    y=instance.query("CALC:MARK1:Y?")
    time.sleep(0.1)
    y=round(float(y), 3)
    return y


def get_mark_X():
    x=instance.query("CALC:MARK1:X?")
    time.sleep(0.1)
    x=(float)(x)*1e-6
    x=round(float(x), 3)
    return x

def run():
    instance.write(":INIT:CONT ON")
    time.sleep(1)

def stop():
    instance.write(":INIT:CONT OFF")
    instance.write(":INIT:IMM")
    time.sleep(1)

def peaking_search():
    instance.write(":CALC1:MARK1:MAX:PEAK")
    time.sleep(0.5)

def peaking_next():
    instance.write(":CALC1:MARK1:STAT ON")
    time.sleep(0.1)
    instance.write(":CALC1:MARK1:MAX:NEXT")
    time.sleep(0.1)

def get_rmsjitter():
    jitter=instance.query(":FETC1:RANGE:PNO1:RMS?")
    time.sleep(0.1)
    jitter = (float)(jitter) * 1e15
    jitter = round(float(jitter), 3)
    return jitter

def save_picture(file_name):
    instance.write(f":MMEM:NAME 'C:\\FK\\{file_name}.PNG'")
    instance.write(":HCOP:IMM1")


if __name__=="__main__":
    run()
    stop()
    time.sleep(3)
    peaking_search()
    x=get_mark_X()
    print(x)
    y=get_mark_y()
    print(y)
    jitter=get_rmsjitter()
    print(jitter)
    save_picture(222)