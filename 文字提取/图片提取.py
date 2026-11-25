from pathlib import Path

from paddleocr import PaddleOCR
# 参数含义参考：
# https://blog.csdn.net/qq_41273999/article/details/135868038?ops_request_misc=%257B%2522request%255Fid%2522%253A%
ocr = PaddleOCR(use_angle_cls=False, use_gpu=True, show_log=False, lang='en')  # 'ch'就是识别中文
# ocr2 = PaddleOCR(use_angle_cls=False, use_gpu=True, lang='en', use_mp=True, total_process_num=8)
# 如果报路径错误，使用以下代码，指定模型下载路径：
# ocr = PaddleOCR(use_angle_cls=True, use_gpu=True,
#                 det_model_dir='ch_PP-OCRv3_det_infer',# 文本检测
#                 rec_model_dir='ch_PP-OCRv3_rec_infer',# 文本识别
#                 cls_model_dir='ch_ppocr_mobile_v2.0_cls_slim_infer',# 旋转文本（通用）
#                 lang="ch")
# ocr = PaddleOCR(use_angle_cls=True, use_gpu=False, show_log=False, # 关闭日志
#                 det_model_dir='en_PP-OCRv3_det_infer', # 文本检测
#                 rec_model_dir='en_PP-OCRv3_rec_infer', # 文本识别
#                 cls_model_dir='ch_ppocr_mobile_v2.0_cls_slim_infer', # 旋转文本（通用）
#                 lang="en")

img_path = str(Path(__file__).with_name('shii.jpg'))
result = ocr.ocr(img_path, cls=False)
print(result)
for line in result[0]:
    print(line[1][0])
