# pip install pyserial
import serial
import time

#### 串口号，右键计算机->点击设备->点击端口->查看获取
SERIAL_PORT = 'COM4'
ser = serial.Serial(SERIAL_PORT, baudrate=9600, timeout=0.5)
# 波特率（baud rate），单位是比特/秒，用于指定数据传输速率。波特率必须与你想要通信的设备设置相匹配。
# 用于设置读操作的超时时间（以秒为单位）。如果在指定的时间内没有接收到任何数据，可能返回空结果

######## 指令声明
LIGHT_BUZZ1="0110001A000101CE18"   #闪光+声音1
LIGHT_BUZZ2="0110001A0001040E1B"   #闪光+声音2
LIGHT="0110001A0001028E19"         #闪光
BUZZ1="0110001A0001034FD9"         #声音1
BUZZ2="0110001A000105CFDB"         #声音2
BUZZ_CMD_CLOSE = "0110001A0001000FD8"  # 关闭声音和闪光

# f=open('a.txt','w')
# f.write('xxx')
# f.close()
####

# 向设备发送指令
####
# 2个用法
def sendCmdToDevice(cmd):
    cmdd = bytes.fromhex(cmd)
    # 将包含十六进制数字的字符串转换为bytes对象
    # 每对十六进制字符会被转换成一个字节。
    # print(cmdd)
    ser.write(cmdd)


if __name__ == '__main__':
    sendCmdToDevice(LIGHT)
    time.sleep(5)
    sendCmdToDevice(BUZZ_CMD_CLOSE)
    # time.sleep(5)
    # sendCmdToDevice(LIGHT)
    # time.sleep(5)
    # sendCmdToDevice(BUZZ_CMD_CLOSE)
    ser.close()
