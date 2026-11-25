import sys

import cv2
import numpy as np
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=False, use_gpu=True, show_log=False, lang='en')  # 'ch'就是识别中文

# 视频来源：电脑摄像头编号（0 为默认摄像头，多个摄像头依次为 1、2...），或视频文件路径
# 不传参数时默认使用摄像头 0
source = sys.argv[1] if len(sys.argv) > 1 else '0'
cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
if not cap.isOpened():
    raise SystemExit(f"打开摄像头/视频失败，请确认摄像头可用或文件存在: {source}")

frame_index = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    result = ocr.ocr(frame, cls=False)
    if result and result[0]:
        texts = [line[1][0] for line in result[0]]
        print(f"第 {frame_index} 帧: {texts}")
        for line in result[0]:
            # 转换为整数坐标
            pts_int = np.array(line[0], dtype=np.int32)
            # 确保坐标数组的形状是 (n, 1, 2) 以符合 OpenCV 函数的要求
            pts = pts_int.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=(147, 20, 255), thickness=2)
            cv2.putText(frame, line[1][0], tuple(pts_int[0]), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 3)

    cv2.imshow('result', frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # 按 ESC 提前退出
        break
    frame_index += 1

cap.release()
cv2.destroyAllWindows()
