import sys

import cv2
import numpy as np
from paddleocr import PaddleOCR
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from 正则判断 import process_string


def frame_to_qimage(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb_frame.shape
    image = QImage(
        rgb_frame.data,
        width,
        height,
        channels * width,
        QImage.Format_RGB888,
    )
    return image.copy()


class OcrThread(QThread):
    frame_ready = pyqtSignal(QImage)
    results_ready = pyqtSignal(list, list)
    error = pyqtSignal(str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._running = False

    def run(self):
        self._running = True
        capture = None
        try:
            ocr = PaddleOCR(
                use_angle_cls=False,
                use_gpu=True,
                show_log=False,
                lang='en',
            )
            capture = cv2.VideoCapture(self.camera_index)
            if not capture.isOpened():
                self.error.emit(f'无法打开电脑摄像头 {self.camera_index}')
                return

            while self._running:
                ret, frame = capture.read()
                if not ret:
                    self.error.emit('无法读取摄像头画面')
                    break

                result = ocr.ocr(frame, cls=False)
                lines = result[0] if result and result[0] else []
                texts = [line[1][0] for line in lines]
                models = process_string(' '.join(texts))

                for line in lines:
                    points = np.array(line[0], dtype=np.int32)
                    polygon = points.reshape((-1, 1, 2))
                    cv2.polylines(
                        frame,
                        [polygon],
                        isClosed=True,
                        color=(147, 20, 255),
                        thickness=2,
                    )
                    cv2.putText(
                        frame,
                        line[1][0],
                        tuple(points[0]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3,
                    )

                self.results_ready.emit(models, texts)
                self.frame_ready.emit(frame_to_qimage(frame))
        except Exception as exc:
            self.error.emit(f'识别出错：{exc}')
        finally:
            if capture is not None:
                capture.release()
            self._running = False

    def stop(self):
        self._running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('包装型号识别')
        self.resize(1100, 720)

        self.video_label = QLabel('点击“开始识别”打开电脑摄像头')
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(720, 540)
        self.video_label.setStyleSheet('background-color: #202124; color: white;')

        self.start_button = QPushButton('开始识别')
        self.stop_button = QPushButton('停止识别')
        self.stop_button.setEnabled(False)
        self.status_label = QLabel('状态：未启动')
        self.status_label.setWordWrap(True)

        self.model_label = QLabel('未识别到型号')
        self.model_label.setWordWrap(True)
        self.model_label.setStyleSheet('font-size: 22px; font-weight: bold;')
        self.text_output = QPlainTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText('摄像头画面中识别到的文字会显示在这里')

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        panel_layout = QVBoxLayout()
        panel_layout.addLayout(button_layout)
        panel_layout.addWidget(self.status_label)
        panel_layout.addWidget(QLabel('包装型号'))
        panel_layout.addWidget(self.model_label)
        panel_layout.addWidget(QLabel('原始识别文字'))
        panel_layout.addWidget(self.text_output, 1)

        panel = QWidget()
        panel.setLayout(panel_layout)
        panel.setFixedWidth(320)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 1)
        main_layout.addWidget(panel)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.ocr_thread = OcrThread(camera_index=0, parent=self)
        self.ocr_thread.frame_ready.connect(self.update_frame)
        self.ocr_thread.results_ready.connect(self.update_results)
        self.ocr_thread.error.connect(self.show_error)
        self.ocr_thread.finished.connect(self.recognition_finished)

        self.start_button.clicked.connect(self.start_recognition)
        self.stop_button.clicked.connect(self.stop_recognition)

    def start_recognition(self):
        if self.ocr_thread.isRunning():
            return
        self.model_label.setText('未识别到型号')
        self.text_output.clear()
        self.status_label.setText('状态：正在加载识别模型...')
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.ocr_thread.start()

    def stop_recognition(self):
        if not self.ocr_thread.isRunning():
            return
        self.status_label.setText('状态：正在停止...')
        self.stop_button.setEnabled(False)
        self.ocr_thread.stop()

    def update_frame(self, image):
        pixmap = QPixmap.fromImage(image)
        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        self.status_label.setText('状态：正在识别')

    def update_results(self, models, texts):
        self.model_label.setText('\n'.join(models) if models else '未识别到型号')
        self.text_output.setPlainText('\n'.join(texts))

    def show_error(self, message):
        self.status_label.setText(f'状态：{message}')

    def recognition_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.status_label.text().startswith('状态：正在'):
            self.status_label.setText('状态：已停止')

    def closeEvent(self, event):
        if self.ocr_thread.isRunning():
            self.ocr_thread.stop()
            self.ocr_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
