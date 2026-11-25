import os
import cv2
from numpy import ndarray
import sys
import logging
import numpy as np
# from paddleocr import PaddleOCR

sys.path.append(r"E:\MVS\Development\Samples\Python\MvImport")
from HKCamera_class import HKCamera

# logging.disable(logging.DEBUG)
# ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, lang='en')

'''169.254.172.69
169.254.183.69
169.254.180.69'''
if __name__ == '__main__':
    # camera1 = HKCamera(CameraIp='169.254.79.254')       #当前 ip 地址
    # camera2 = HKCamera(CameraIp='169.254.183.69')
    camera3 = HKCamera(CameraIp='169.254.180.69')

    # 对摄像头配置进行设置
    try:                            #  枚举
        camera1.set_Value(param_type="enum_value", node_name="PixelFormat",
                         node_value='BayerGB8')   #RGB8Packed
        camera1.set_Value(param_type="enum_value", node_name="GainAuto",  #自动增益
                               node_value='Continuous')
        # camera2.set_Value(param_type="enum_value", node_name="PixelFormat",   #像素格式
        #                  node_value='RGB8Packed')
        # camera3.set_Value(param_type="enum_value", node_name="PixelFormat",   #像素格式
        #                  node_value='RGB8Packed')
        # camera.set_Value(param_type="enum_value", node_name="ExposureAuto",  #自动曝光
        #                  node_value='On')
        # camera.set_Value(param_type="float_value", node_name="ExposureTime",  #曝光时间
        #                  node_value='115000')

    except Exception as e:
        print(e)
        os._exit(0)
    camera1.start_camera()
    # camera2.start_camera()
    # camera3.start_camera()
# cap=cv2.VideoCapture(0)
    while True:
        try:
            # _,frame=cap.read()
            image1: ndarray = camera1.get_image()    #声明一个名为image的变量，并且指定它的类型为ndarray
            # image2: ndarray = camera2.get_image()
            # image3: ndarray = camera3.get_image()
            if image1 is not None:
                # 这里拿到图片的ndarray数据后，可以转Image、可以保存图片....等等操作
                cv2.namedWindow('result1', cv2.WINDOW_NORMAL)
                # cv2.namedWindow('result2', cv2.WINDOW_NORMAL)
                # cv2.namedWindow('result3', cv2.WINDOW_NORMAL)
                # cv2.resizeWindow('result', 640, 480)
                image1=cv2.resize(image1,(640,480))
                # image2=cv2.resize(image2,(640,480))
                # image3=cv2.resize(image3,(640,480))
                cv2.imshow('result1', image1)
                # cv2.imshow('result2', image2)
                # cv2.imshow('result3', image3)
                # 创建窗口
                # print(image.shape)
            key = cv2.waitKey(50)
            if key == 27:
                cv2.destroyAllWindows()
                break
        except Exception as e:
            print(e)
