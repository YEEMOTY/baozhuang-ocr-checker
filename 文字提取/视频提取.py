from pathlib import Path

from paddleocr import PaddleOCR
import cv2
import numpy as np

ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, show_log=False, lang='en')  # 'ch'就是识别中文
img_path = Path(__file__).with_name('P04476.bmp')
frame = cv2.imread(str(img_path))
if frame is None:
    raise SystemExit(f"读取图片失败，请确认文件存在: {img_path}")
result = ocr.ocr(frame, cls=True)
if result is not None:
    for line in result[0]:
        # 转换为整数坐标
        pts_int = np.array(line[0], dtype=np.int32)
        # 确保坐标数组的形状是 (n, 1, 2) 以符合 OpenCV 函数的要求
        pts = pts_int.reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(147, 20, 255), thickness=2)
        cv2.putText(frame, line[1][0], pts_int[0], cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 255), 3)

cv2.imshow('x', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
