# -*- coding: utf-8 -*-
# 此文件为 PyQt5 Designer 风格的 UI 生成代码（手写补全）。
# 主程序 jinzhai(全).py 通过 from 金寨窗口0 import Ui_MainWindow 使用。
# 界面布局：上方三摄像头画面并排，下方对应的识别结果文本框，底部操作按钮。

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName('MainWindow')
        MainWindow.resize(1400, 900)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')

        # ========== 顶部三摄像头画面区域 ==========
        # label: camera1(海康192.168.20.20)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 20, 440, 330))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet('background-color: #1a1a1a; color: #888; border: 1px solid #444;')
        self.label.setObjectName('label')

        # label_3: camera2(海康192.168.20.60)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(490, 20, 440, 330))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setStyleSheet('background-color: #1a1a1a; color: #888; border: 1px solid #444;')
        self.label_3.setObjectName('label_3')

        # label_2: camera3(USB)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(960, 20, 440, 330))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setStyleSheet('background-color: #1a1a1a; color: #888; border: 1px solid #444;')
        self.label_2.setObjectName('label_2')

        # 三个画面标题
        lbl_title1 = QtWidgets.QLabel(self.centralwidget)
        lbl_title1.setGeometry(QtCore.QRect(20, 355, 440, 24))
        lbl_title1.setAlignment(QtCore.Qt.AlignCenter)
        lbl_title1.setText('镜头一 (海康 GigE)')
        lbl_title1.setStyleSheet('font-weight: bold; color: #ddd;')

        lbl_title2 = QtWidgets.QLabel(self.centralwidget)
        lbl_title2.setGeometry(QtCore.QRect(490, 355, 440, 24))
        lbl_title2.setAlignment(QtCore.Qt.AlignCenter)
        lbl_title2.setText('镜头二 (海康 GigE)')
        lbl_title2.setStyleSheet('font-weight: bold; color: #ddd;')

        lbl_title3 = QtWidgets.QLabel(self.centralwidget)
        lbl_title3.setGeometry(QtCore.QRect(960, 355, 440, 24))
        lbl_title3.setAlignment(QtCore.Qt.AlignCenter)
        lbl_title3.setText('镜头三 (USB 摄像头)')
        lbl_title3.setStyleSheet('font-weight: bold; color: #ddd;')

        # ========== 警告标签（⚠符号，覆盖在画面上） ==========
        # label_4: 镜头一警告
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(200, 155, 80, 80))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setText(QtCore.QCoreApplication.translate('MainWindow', '⚠', None))
        self.label_4.setStyleSheet(
            'font-size: 56px; color: red; font-weight: bold; '
            'background-color: rgba(0,0,0,128); border-radius: 16px;'
        )
        self.label_4.setVisible(False)
        self.label_4.setObjectName('label_4')

        # label_5: 镜头二警告
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(670, 155, 80, 80))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setText(QtCore.QCoreApplication.translate('MainWindow', '⚠', None))
        self.label_5.setStyleSheet(
            'font-size: 56px; color: red; font-weight: bold; '
            'background-color: rgba(0,0,0,128); border-radius: 16px;'
        )
        self.label_5.setVisible(False)
        self.label_5.setObjectName('label_5')

        # label_6: 镜头三警告
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(1140, 155, 80, 80))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setText(QtCore.QCoreApplication.translate('MainWindow', '⚠', None))
        self.label_6.setStyleSheet(
            'font-size: 56px; color: red; font-weight: bold; '
            'background-color: rgba(0,0,0,128); border-radius: 16px;'
        )
        self.label_6.setVisible(False)
        self.label_6.setObjectName('label_6')

        # ========== 识别结果文本框区域 ==========
        lbl_res1 = QtWidgets.QLabel(self.centralwidget)
        lbl_res1.setGeometry(QtCore.QRect(20, 400, 120, 24))
        lbl_res1.setText('镜头一识别结果')
        lbl_res1.setStyleSheet('color: #aaa;')

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(140, 400, 320, 28))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.lineEdit.setObjectName('lineEdit')

        lbl_res2 = QtWidgets.QLabel(self.centralwidget)
        lbl_res2.setGeometry(QtCore.QRect(490, 400, 120, 24))
        lbl_res2.setText('镜头二识别结果')
        lbl_res2.setStyleSheet('color: #aaa;')

        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(610, 400, 320, 28))
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.lineEdit_2.setObjectName('lineEdit_2')

        lbl_res3 = QtWidgets.QLabel(self.centralwidget)
        lbl_res3.setGeometry(QtCore.QRect(960, 400, 120, 24))
        lbl_res3.setText('镜头三识别结果')
        lbl_res3.setStyleSheet('color: #aaa;')

        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(1080, 400, 320, 28))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setStyleSheet('font-size: 16px; font-weight: bold;')
        self.lineEdit_3.setObjectName('lineEdit_3')

        # ========== 底部操作按钮 ==========
        # pushButton_4: 开/关识别
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(620, 520, 160, 48))
        self.pushButton_4.setText('打开')
        self.pushButton_4.setStyleSheet(
            'QPushButton { font-size: 18px; padding: 6px 20px; background-color: #3a7d44; '
            'color: white; border-radius: 6px; } QPushButton:hover { background-color: #2d6a36; }'
        )
        self.pushButton_4.setObjectName('pushButton_4')

        # 复位按钮一：镜头一
        self.pushButton_reset1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_reset1.setGeometry(QtCore.QRect(20, 520, 140, 48))
        self.pushButton_reset1.setText('复位镜头一')
        self.pushButton_reset1.setStyleSheet(
            'QPushButton { font-size: 16px; padding: 6px 14px; background-color: #b87333; '
            'color: white; border-radius: 6px; } QPushButton:hover { background-color: #996028; }'
        )
        self.pushButton_reset1.setObjectName('pushButton_reset1')

        # 复位按钮二：镜头二
        self.pushButton_reset2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_reset2.setGeometry(QtCore.QRect(180, 520, 140, 48))
        self.pushButton_reset2.setText('复位镜头二')
        self.pushButton_reset2.setStyleSheet(
            'QPushButton { font-size: 16px; padding: 6px 14px; background-color: #b87333; '
            'color: white; border-radius: 6px; } QPushButton:hover { background-color: #996028; }'
        )
        self.pushButton_reset2.setObjectName('pushButton_reset2')

        # 打开报警文件夹按钮
        self.pushButton_openlog = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_openlog.setGeometry(QtCore.QRect(1080, 520, 160, 48))
        self.pushButton_openlog.setText('打开报警记录')
        self.pushButton_openlog.setStyleSheet(
            'QPushButton { font-size: 16px; padding: 6px 14px; background-color: #4a6fa5; '
            'color: white; border-radius: 6px; } QPushButton:hover { background-color: #3d5d8e; }'
        )
        self.pushButton_openlog.setObjectName('pushButton_openlog')

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate('MainWindow', '包装盒检测', None))
        self.label.setText(_translate('MainWindow', '镜头一 未启动', None))
        self.label_2.setText(_translate('MainWindow', '镜头三 未启动', None))
        self.label_3.setText(_translate('MainWindow', '镜头二 未启动', None))
