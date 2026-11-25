import sys
import os
import argparse
import re
import time
import logging
import threading
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from numpy import ndarray
from paddleocr import PaddleOCR
import serial
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QDesktopServices
from PyQt5.QtCore import QUrl

# 把项目根目录加到 sys.path，让 HKCamera_class 和海康 SDK 文件可被导入
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from HKCamera_class import HKCamera
from 金寨窗口0 import Ui_MainWindow

def release_capture3(cap):    # 定期释放usb摄像头资源
    while True:
        # 每隔一段时间释放一次资源，这里设置为 30min
        time.sleep(1800)
        cap.release()
        cap.open(opt.cap_numb3)
parser = argparse.ArgumentParser(description='包装型号一致性校验系统（海康 GigE × 2 + USB 摄像头 × 1）')
parser.add_argument("--SERIAL_PORT1", type=str, default='COM14', help='镜头一报警器的串口号')
parser.add_argument("--SERIAL_PORT2", type=str, default='COM16', help='镜头二/三报警器的串口号')
parser.add_argument("--camera1_ip", type=str, default='192.168.20.20', help='海康 GigE 镜头一的 IP')
parser.add_argument("--camera2_ip", type=str, default='192.168.20.60', help='海康 GigE 镜头二的 IP')
parser.add_argument("--cap_numb3", type=int, default=1, help='USB 镜头三的摄像头编号（0=默认）')
parser.add_argument("--frame_delay", type=int, default=67, help='QTimer 取帧间隔（毫秒）')
parser.add_argument("--baojing_dir", type=str, default=None,
                    help='报警截图保存目录（默认 ./baojing，自动创建子目录 镜头一/二/三）')
opt = parser.parse_args()

# 计算报警保存目录：默认项目根目录/baojing
if opt.baojing_dir is None:
    opt.baojing_dir = str(PROJECT_ROOT / 'baojing')
BAOJING_ROOT = Path(opt.baojing_dir)
for sub in ['镜头一', '镜头二', '镜头三']:
    (BAOJING_ROOT / sub).mkdir(parents=True, exist_ok=True)

######## 指令声明

LIGHT_BUZZ1 = "0110001A000101CE18"  # 闪光+声音1
LIGHT_BUZZ2 = "0110001A0001040E1B"  # 闪光+声音1
LIGHT = "0110001A0001028E19"  # 闪光
BUZZ1 = "0110001A0001034FD9"  # 声音1
BUZZ2 = "0110001A000105CFDB"  # 声音2
BUZZ_CMD_CLOSE = "0110001A0001000FD8"  # 关闭声音和闪光

logging.disable(logging.DEBUG)  # 关闭日志的输出

def sendCmdToDevice(cmd, ser):   # 控制警报器
    cmdd = bytes.fromhex(cmd)
    ser.write(cmdd)

def most_common_element(lst):   # 提取列表中出现次数最多的字符
    # 使用Counter统计每个元素出现的次数
    count = Counter(lst)
    # 找到出现次数最多的元素
    most_common_item = count.most_common(1)[0][0]
    return most_common_item

def process_string(input_string):   # 在ocr的结果中筛选出对应型号
    aa=[]
    # 用空格切分字符串
    parts = input_string.split()
    # 正则表达式1: 包含数字和字母或者纯数字
    pattern_alphanumeric = re.compile(r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d-]{2,10}$')
    # 正则表达式2: 至少三个以上数字的纯数字
    pattern_at_least_two_digits = re.compile(r'^\d{4,7}$')
    # 遍历每个切分后的部分
    for part in parts:
        # 检查是否包含数字和字母或者纯数字
        if pattern_alphanumeric.match(part) or pattern_at_least_two_digits.match(part):
            aa.append(part)
    return aa

def set_bing(set_a):    # 替换一些易错字符
    resu =set()
    for j in set_a:
        jj = j.replace('0', 'O').replace('o', 'O').replace('s', '5').replace('S', '5').replace('I', '1').replace('L', '1').replace('v','V').replace('B','8').replace('p','P')
        resu.add(jj)
    return resu

def hide_label_and_send_cmd(label,ser=None):   # 隐藏警告符号，并停止报警
    label.setVisible(False)  # 隐藏警告符号
    sendCmdToDevice(BUZZ_CMD_CLOSE, ser)

def In_which(text, hun):
    a = 0
    for i in hun:
        if text in i:
            a += 1
    return a

def are(i):    # 计算字符面积
    zs = i[0][0]
    ys = i[0][1]
    yx = i[0][2]
    zx = i[0][3]

    # 计算宽度为左上角到右上角的距离
    width_A = np.sqrt(((zs[0] - ys[0]) ** 2) + ((zs[1] - ys[1]) ** 2))
    # 计算宽度为左下角到右下角的距离
    width_B = np.sqrt(((zx[0] - yx[0]) ** 2) + ((zx[1] - yx[1]) ** 2))
    # 计算高度为左上角到左下角的距离
    height_A = np.sqrt(((zs[0] - zx[0]) ** 2) + ((zs[1] - zx[1]) ** 2))
    # 计算高度为右上角到右下角的距离
    height_B = np.sqrt(((ys[0] - yx[0]) ** 2) + ((ys[1] - yx[1]) ** 2))
    # 取平均值作为宽度和高度
    width = (width_A + width_B) / 2
    height = (height_A + height_B) / 2
    # 计算面积
    area = width * height
    return area

ocr = PaddleOCR(use_angle_cls=True,use_gpu=True, lang='en')
ocr2 = PaddleOCR(use_angle_cls=False, use_gpu=True, lang='en')

class PyQtMainEntry(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        self.ser1 = serial.Serial(opt.SERIAL_PORT1, 9600, timeout=2.5)
        self.ser2 = serial.Serial(opt.SERIAL_PORT2, 9600, timeout=2.5)
        # self.ser3 = serial.Serial(opt.SERIAL_PORT3, 9600, timeout=2.5)


        self.label_4.setVisible(False)
        self.label_5.setVisible(False)
        self.label_6.setVisible(False)
        self.list_zong1 = []
        self.list_zong2 = []
        self.list_zong3 = []
        self.set_zong1 = set()
        self.set_zong2 = set()
        self.set_zong3 = set()
        self.set_12hun = set()
        self.guo = []

        self.list1 = []
        self.list2 = []
        self.list3 = []

        self.daan1 = ''
        self.daan2 = ''

        # self.showMaximized()
        # 第一个摄像头（海康 GigE）
        self.camera1 = HKCamera(CameraIp=opt.camera1_ip)
        self.camera1.set_Value(param_type="enum_value", node_name="PixelFormat",
                               node_value='BayerGB8')
        self.camera1.set_Value(param_type="enum_value", node_name="GainAuto",
                               node_value='Continuous')
        self.camera1.set_Value(param_type="float_value", node_name="AcquisitionFrameRate",
                               node_value='15.0000')
        # self.camera1.set_Value(param_type="enum_value", node_name="ExposureAuto",
        #                        node_value='Continuous')  # 自动曝光
        self.camera1.start_camera()

        # 第二个摄像头（海康 GigE）
        self.camera2 = HKCamera(CameraIp=opt.camera2_ip)
        self.camera2.set_Value(param_type="enum_value", node_name="PixelFormat",
                               node_value='BayerGB8')
        self.camera2.set_Value(param_type="enum_value", node_name="GainAuto",
                               node_value='Continuous')
        self.camera2.set_Value(param_type="float_value", node_name="AcquisitionFrameRate",
                               node_value='15.0000')
        # self.camera2.set_Value(param_type="enum_value", node_name="ExposureAuto",
        #                        node_value='Continuous')   #自动曝光
        # self.camera2.set_Value(param_type="enum_value", node_name="DecimationHorizontal",
        #                        node_value='2')
        # self.camera2.set_Value(param_type="enum_value", node_name="DecimationVertical",
        #                        node_value='2')
        self.camera2.start_camera()

        self.camera3 = cv2.VideoCapture(opt.cap_numb3)

        # 启动后台线程来定期释放第三个摄像头的资源
        release_thread2 = threading.Thread(target=release_capture3, args=(self.camera3,))
        release_thread2.daemon = True  # 设置为守护线程，随主线程结束而结束
        release_thread2.start()

        self.is_camera_opened = False
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._queryFrame)
        self._timer.setInterval(opt.frame_delay)

        self.frame_counter = 0    # 统计画面的帧数

        # 按钮事件绑定
        self.pushButton_4.clicked.connect(self.openvideo)
        self.pushButton_reset1.clicked.connect(self.clearSet1)
        self.pushButton_reset2.clicked.connect(self.clearSet2)
        self.pushButton_openlog.clicked.connect(self.open_folder)

        # self.pushButton_4.click()

    def openvideo(self):
        self.is_camera_opened = not self.is_camera_opened
        if self.is_camera_opened:
            self.pushButton_4.setText("关闭")
            self._timer.start()
        else:
            self.pushButton_4.setText("打开")
            self._timer.stop()
            sendCmdToDevice(BUZZ_CMD_CLOSE, self.ser1)
            sendCmdToDevice(BUZZ_CMD_CLOSE, self.ser2)
            # sendCmdToDevice(BUZZ_CMD_CLOSE, self.ser3)
            self.label_4.setVisible(False)
            self.label_5.setVisible(False)
            self.label_6.setVisible(False)

    def open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(opt.baojing_dir))

    def clearSet1(self):     # 复位按钮一
        self.set_zong1.clear()
        # self.list_zong1.clear()
        self.list1.clear()
        sendCmdToDevice(BUZZ_CMD_CLOSE, self.ser1)
        self.label_4.setVisible(False)

    def clearSet2(self):      # 复位按钮二
        self.set_zong2.clear()
        # self.list_zong2.clear()
        self.list2.clear()
        sendCmdToDevice(BUZZ_CMD_CLOSE, self.ser2)
        self.label_5.setVisible(False)

    def execute_after_n_calls(n, w2set):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                wrapper.count += 1
                result = func(self, *args, **kwargs)
                if wrapper.count % n == 0:
                    w2set(self)
                return result
            wrapper.count = 0
            return wrapper
        return decorator

    @QtCore.pyqtSlot()
    def _queryFrame(self):
        try:
            if not self.camera3.grab():
                print("No frame grabbed.")
                self.camera3.release()
                self.close()
            else:
                self.frame1: ndarray = self.camera1.get_image()
                self.frame2: ndarray = self.camera2.get_image()
                ret3, self.frame3 = self.camera3.read()

                if not ret3:
                    print("No frame retrieved.")
                    # self.camera1.release()
                    self.camera3.release()
                    self.close()
                else:

                    self.frame11 = cv2.resize(self.frame1, (640, 480))
                    self.frame22 = cv2.resize(self.frame2, (640, 480))
                    self.frame33 = cv2.resize(self.frame3, (640, 480))

                    if ret3:
                        qimage = cv2.cvtColor(self.frame11.copy(), cv2.COLOR_BGR2RGB)
                        qimage = QtGui.QImage(qimage.data, qimage.shape[1], qimage.shape[0], QtGui.QImage.Format_RGB888)
                        pixmap = QtGui.QPixmap.fromImage(qimage)

                        qimage2 = cv2.cvtColor(self.frame22.copy(), cv2.COLOR_BGR2RGB)
                        qimage2 = QtGui.QImage(qimage2.data, qimage2.shape[1], qimage2.shape[0], QtGui.QImage.Format_RGB888)
                        pixmap2 = QtGui.QPixmap.fromImage(qimage2)

                        qimage3 = cv2.cvtColor(self.frame33.copy(), cv2.COLOR_BGR2RGB)
                        qimage3 = QtGui.QImage(qimage3.data, qimage3.shape[1], qimage3.shape[0], QtGui.QImage.Format_RGB888)
                        pixmap3 = QtGui.QPixmap.fromImage(qimage3)

                        self.label.setPixmap(pixmap)
                        self.label_3.setPixmap(pixmap2)
                        self.label_2.setPixmap(pixmap3)

                        # 每隔一定帧数执行一次OCR
                        self.frame_counter += 1
                        if self.frame_counter % 5 == 0:
                            self._performOCR1()
                        if self.frame_counter % 3 == 0:
                            self._performOCR2()

                        # self._performOCR1()
                        # self._performOCR2()
                        # self._performOCR3()
                        if self.frame_counter % 3 == 0:
                            self._performOCR3()
        except:
            pass

    def w2set1(self):
        if self.list_zong1:
            try:
                for i in self.list_zong1:
                    if self.list_zong1.count(i) > 1:
                        self.set_zong1.add(i)
                set_len1 = set_bing(self.set_zong1)   # 当前检测的结果

                self.list1.extend(list(set_len1))
                self.daan1 = most_common_element(self.list1)  # 标准答案

                if self.frame_counter % 16 == 0:  # 约每 10 秒刷新一下
                    self.list1.clear()

                text = ','.join(set_len1)
                self.lineEdit.setText(text)
                #   "做判断"
                if (not self.daan1) or (not set_len1):
                    pass
                elif len(set_len1) == 1 and (list(set_len1)[0] == self.daan1):
                    pass
                else:
                    print('一')
                    print(set_len1, self.daan1)

                    tu1 = cv2.putText(self.frame1.copy(), text, (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5,
                                      cv2.LINE_AA)

                    nam = time.strftime("%Y_%m_%d_%H_%M", time.localtime())
                    path = str(BAOJING_ROOT / '镜头一' / f'{nam}-{self.daan1}.jpg')
                    cv2.imencode('.jpg', tu1)[1].tofile(path)

                    self.label_4.setVisible(True)   # 显示⚠符号
                    # sendCmdToDevice(LIGHT_BUZZ1, self.ser1)
                    sendCmdToDevice(LIGHT, self.ser1)
                    QtCore.QTimer.singleShot(5000, lambda: hide_label_and_send_cmd(self.label_4,self.ser1)) # 相当于格外线程，计时5s后隐藏⚠，并停止报警

                    # self.list_zong1.clear()
                    # self.set_zong1.clear()
                    self.frame_counter = 0
            except Exception as e:
                print(e)
            self.list_zong1.clear()
            self.set_zong1.clear()

    @execute_after_n_calls(3, w2set1)
    def _performOCR1(self):
        result = ocr2.ocr(self.frame1, cls=False)
        if result and not None in result:
            try:
                for i in result[0]:
                    # print(i)
                    mianji = are(i)
                    # print('yi',i,mianji)
                    ma = process_string(i[1][0])
                    # if i[1][1] > 0.92 and ma and 80<i[0][0][0]<550 and mianji>1000:
                    if i[1][1] > 0.92 and ma and 320 < i[0][0][0]< 1060 and mianji > 1000:
                        self.list_zong1.extend(ma)
                        # print(i[1][0], are(i))
                # print('******************')
            except:
                pass
    def w2set2(self):
        if self.list_zong2:
            try:
                for i in self.list_zong2:
                    if self.list_zong2.count(i) > 1:
                        self.set_zong2.add(i)

                set_len2 = set_bing(self.set_zong2)

                self.list2.extend(list(set_len2))

                self.daan2 = most_common_element(self.list2)
                if self.frame_counter % 25 == 0:  # 约每 10 秒刷新一下
                    self.list2.clear()

                text2 = ','.join(set_len2)
                self.lineEdit_2.setText(text2)

                if (not self.daan2) or (not set_len2):
                    pass
                elif len(set_len2)==1 and (list(set_len2)[0] == self.daan2):
                    pass
                else:
                    print('二')
                    print(set_len2, self.daan2)

                    tu2 = cv2.putText(self.frame2.copy(), text2, (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 6,
                                      cv2.LINE_AA)

                    nam2 = time.strftime("%Y_%m_%d_%H_%M", time.localtime())
                    path = str(BAOJING_ROOT / '镜头二' / f'{nam2}-{self.daan2}.jpg')
                    cv2.imencode('.jpg', tu2)[1].tofile(path)

                    self.label_5.setVisible(True)
                    # sendCmdToDevice(LIGHT_BUZZ1, self.ser2)
                    sendCmdToDevice(LIGHT, self.ser2)
                    QtCore.QTimer.singleShot(5000, lambda: hide_label_and_send_cmd(self.label_5, self.ser2))

                    # self.list_zong2.clear()
                    # self.set_zong2.clear()

                    self.frame_counter = 0
            except Exception as e:
                print(e)
            self.list_zong2.clear()
            self.set_zong2.clear()

        # self.set_12hun.add(self.daan1)
        # self.set_12hun.add(self.daan2)
        self.set_12hun=set([self.daan1,self.daan2])

        print('1:', self.daan1)
        print('2:', self.daan2)
        print('合:', self.set_12hun)


    @execute_after_n_calls(3, w2set2)
    def _performOCR2(self):
        # 执行OCR操作
        result2 = ocr2.ocr(self.frame2, cls=False)
        if result2 and not None in result2:
            try:
                for i in result2[0]:
                    mianji=are(i)
                    # print('er',mianji,i)
                    ma=process_string(i[1][0])
                    if i[1][1] > 0.84 and ma and mianji>1600 and (350<i[0][0][0]<1060):  #25000

                        self.list_zong2.extend(ma)
                        # print(i,are(i),xie(i))

            except:
                pass
        elif None in result2:
            self.daan2=''
            self.set_12hun = set([self.daan1, self.daan2])

            print('1:', self.daan1)
            print('2:', self.daan2)
            print('合:', self.set_12hun)

    def w2set3(self):
        maxx = 0
        if self.list_zong3:
            try:
                for i in self.list_zong3:
                    self.guo.append(i[1][0])
                for ii in self.guo:
                    if self.guo.count(ii) > 1:
                        self.set_zong3.add(ii)
                # print('YYYY',self.set_zong3)
                for j in self.list_zong3:
                    if (j[1][0] in self.set_zong3) and (are(j) > maxx):
                        aa = j
                        maxx = are(j)
                text3 = aa[1][0].replace('0', 'O').replace('o', 'O').replace('S', '5').replace('I', '1').replace('L','1').replace('v','V').replace('B','8').replace('p','P')
                self.lineEdit_3.setText(text3)

                if (not text3) or self.set_12hun==set() or self.set_12hun=={''}:
                    pass
                elif self.set_12hun and In_which(text3,self.set_12hun):
                    pass
                else:
                    print('三')
                    print(text3)
                    print(self.set_12hun)

                    tu3 = cv2.putText(self.frame3.copy(), text3, (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5,
                                      cv2.LINE_AA)

                    nam3 = time.strftime("%Y_%m_%d_%H_%M", time.localtime())
                    path = str(BAOJING_ROOT / '镜头三' / f'{nam3}-{self.set_12hun}.jpg')
                    cv2.imencode('.jpg', tu3)[1].tofile(path)

                    self.set_12hun.clear()

                    self.label_6.setVisible(True)
                    # sendCmdToDevice(LIGHT_BUZZ1, self.ser3)
                    sendCmdToDevice(LIGHT, self.ser2)
                    QtCore.QTimer.singleShot(5000, lambda: hide_label_and_send_cmd(self.label_6, self.ser2))

                # self.list_zong3.clear()

            except:
                pass
            self.guo.clear()
            self.list_zong3.clear()
            self.set_zong3.clear()

    @execute_after_n_calls(3, w2set3)
    def _performOCR3(self):
        global text3
        # result2 = ocr2.ocr(self.frame3, cls=False)
        try:
            # 将图像从BGR转换为HSV颜色空间
            hsv_image = cv2.cvtColor(self.frame3, cv2.COLOR_BGR2HSV)
            # 定义牛皮纸颜色的范围
            lower_brown = np.array([10, 30, 30])  # 最小颜色值
            upper_brown = np.array([30, 255, 255])  # 最大颜色值
            # 使用颜色范围进行颜色检测
            mask = cv2.inRange(hsv_image, lower_brown, upper_brown)
            # 计算掩码中白色像素（检测到的颜色）的数量
            white_pixels = np.sum(mask == 255)
            # 计算图像的总像素数
            total_pixels = mask.shape[0] * mask.shape[1]
            # 计算特定颜色的占比
            color_percentage = (white_pixels / total_pixels) * 100
            if color_percentage >= 20:   # 20
                # resul = []
                result2 = ocr2.ocr(self.frame3, cls=False)
                if result2 and not None in result2:
                    for j in result2[0]:
                        # print('san',j,are(j))
                        if j[1][1] > 0.93 and process_string(j[1][0]):
                            self.list_zong3.append(j)
                else:
                    text3 = ''
        except:
            text3 = ''

            # self.lineEdit_3.setText(text3)
            # self.label_5.setVisible(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PyQtMainEntry()
    window.show()
    sys.exit(app.exec_())
