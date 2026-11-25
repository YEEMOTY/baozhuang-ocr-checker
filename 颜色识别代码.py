import cv2
import numpy as np

cap=cv2.VideoCapture(0)
while True:
    try:
        ret, frame3 = cap.read()
        hsv_image = cv2.cvtColor(frame3, cv2.COLOR_BGR2HSV)
        # 定义牛皮纸颜色的范围
        lower_brown = np.array([10, 30, 30])  # 最小颜色值
        upper_brown = np.array([30, 255, 255]) # 最大颜色值
        # 使用颜色范围进行颜色检测 符合条件的像素被设为255（白色），不符合条件的像素被设为0（黑色）
        mask = cv2.inRange(hsv_image, lower_brown, upper_brown)
        cv2.imshow('mask',mask)
        # 计算掩码中白色像素（检测到的颜色）的数量
        white_pixels = np.sum(mask == 255)
        # 计算图像的总像素数
        total_pixels = mask.shape[0] * mask.shape[1]
        # 计算特定颜色的占比
        color_percentage = (white_pixels / total_pixels) * 100
        if color_percentage >= 20:
            print("检测到牛皮纸箱") # ocr
        cv2.imshow('Filtered Image1', frame3)
        # 通过按下键盘上的'q'键来退出
        if cv2.waitKey(1) == 27:
            break
    except:
        pass

# 释放摄像头资源及关闭窗口
cap.release()
cv2.destroyAllWindows()
