# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QStackedWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(992, 550)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.icon_only_widget = QWidget(self.centralwidget)
        self.icon_only_widget.setObjectName(u"icon_only_widget")
        self.icon_only_widget.setMinimumSize(QSize(0, 0))
        self.icon_only_widget.setMaximumSize(QSize(71, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.icon_only_widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(18, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.logo_label_1 = QLabel(self.icon_only_widget)
        self.logo_label_1.setObjectName(u"logo_label_1")
        self.logo_label_1.setMaximumSize(QSize(52, 50))
        self.logo_label_1.setPixmap(QPixmap(u":/media/media/wiselens-logo.png"))
        self.logo_label_1.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.logo_label_1)

        self.horizontalSpacer_4 = QSpacerItem(18, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.home_btn_1 = QPushButton(self.icon_only_widget)
        self.home_btn_1.setObjectName(u"home_btn_1")
        icon = QIcon()
        icon.addFile(u":/media/media/home.png", QSize(), QIcon.Normal, QIcon.Off)
        self.home_btn_1.setIcon(icon)
        self.home_btn_1.setIconSize(QSize(30, 30))
        self.home_btn_1.setCheckable(True)
        self.home_btn_1.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.home_btn_1)

        self.cam_btn_1 = QPushButton(self.icon_only_widget)
        self.cam_btn_1.setObjectName(u"cam_btn_1")
        icon1 = QIcon()
        icon1.addFile(u":/media/media/casino-cctv.png", QSize(), QIcon.Normal, QIcon.Off)
        self.cam_btn_1.setIcon(icon1)
        self.cam_btn_1.setIconSize(QSize(30, 30))
        self.cam_btn_1.setCheckable(True)
        self.cam_btn_1.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.cam_btn_1)

        self.edit_btn_1 = QPushButton(self.icon_only_widget)
        self.edit_btn_1.setObjectName(u"edit_btn_1")
        icon2 = QIcon()
        icon2.addFile(u":/media/media/edit.png", QSize(), QIcon.Normal, QIcon.Off)
        self.edit_btn_1.setIcon(icon2)
        self.edit_btn_1.setIconSize(QSize(24, 24))
        self.edit_btn_1.setCheckable(True)
        self.edit_btn_1.setAutoExclusive(True)

        self.verticalLayout.addWidget(self.edit_btn_1)


        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 290, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.exit_btn_1 = QPushButton(self.icon_only_widget)
        self.exit_btn_1.setObjectName(u"exit_btn_1")
        icon3 = QIcon()
        icon3.addFile(u":/media/media/close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.exit_btn_1.setIcon(icon3)
        self.exit_btn_1.setIconSize(QSize(24, 24))
        self.exit_btn_1.setCheckable(True)
        self.exit_btn_1.setAutoExclusive(True)

        self.verticalLayout_3.addWidget(self.exit_btn_1)


        self.gridLayout.addWidget(self.icon_only_widget, 0, 0, 1, 1)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_5 = QVBoxLayout(self.widget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.header_widget = QWidget(self.widget)
        self.header_widget.setObjectName(u"header_widget")
        self.header_widget.setMinimumSize(QSize(0, 40))
        self.horizontalLayout_3 = QHBoxLayout(self.header_widget)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 9, 0)
        self.menu_btn = QPushButton(self.header_widget)
        self.menu_btn.setObjectName(u"menu_btn")
        self.menu_btn.setMaximumSize(QSize(193, 16777215))
        icon4 = QIcon()
        icon4.addFile(u":/media/media/menu.png", QSize(), QIcon.Normal, QIcon.Off)
        self.menu_btn.setIcon(icon4)
        self.menu_btn.setIconSize(QSize(20, 20))
        self.menu_btn.setCheckable(True)

        self.horizontalLayout_3.addWidget(self.menu_btn)

        self.horizontalSpacer = QSpacerItem(168, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.search_input = QLineEdit(self.header_widget)
        self.search_input.setObjectName(u"search_input")

        self.horizontalLayout.addWidget(self.search_input)

        self.search_btn = QPushButton(self.header_widget)
        self.search_btn.setObjectName(u"search_btn")
        icon5 = QIcon()
        icon5.addFile(u":/media/media/search.png", QSize(), QIcon.Normal, QIcon.Off)
        self.search_btn.setIcon(icon5)
        self.search_btn.setIconSize(QSize(18, 18))

        self.horizontalLayout.addWidget(self.search_btn)


        self.horizontalLayout_3.addLayout(self.horizontalLayout)

        self.horizontalSpacer_2 = QSpacerItem(168, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.user_btn = QPushButton(self.header_widget)
        self.user_btn.setObjectName(u"user_btn")
        icon6 = QIcon()
        icon6.addFile(u"media/user.png", QSize(), QIcon.Normal, QIcon.Off)
        self.user_btn.setIcon(icon6)
        self.user_btn.setIconSize(QSize(20, 20))

        self.horizontalLayout_3.addWidget(self.user_btn)


        self.verticalLayout_5.addWidget(self.header_widget)

        self.stackedWidget = QStackedWidget(self.widget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.home_page = QWidget()
        self.home_page.setObjectName(u"home_page")
        self.gridLayout_6 = QGridLayout(self.home_page)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_7 = QLabel(self.home_page)
        self.label_7.setObjectName(u"label_7")
        font = QFont()
        font.setPointSize(12)
        self.label_7.setFont(font)

        self.gridLayout_6.addWidget(self.label_7, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.home_page)
        self.camera_page = QWidget()
        self.camera_page.setObjectName(u"camera_page")
        self.gridLayout_3 = QGridLayout(self.camera_page)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_3 = QLabel(self.camera_page)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.verticalLayout_8.addWidget(self.label_3)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_5 = QLabel(self.camera_page)
        self.label_5.setObjectName(u"label_5")
        font1 = QFont()
        font1.setPointSize(10)
        self.label_5.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_5)

        self.camnameLineEdit = QLineEdit(self.camera_page)
        self.camnameLineEdit.setObjectName(u"camnameLineEdit")

        self.horizontalLayout_4.addWidget(self.camnameLineEdit)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(self.camera_page)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_4)

        self.camipLineEdit = QLineEdit(self.camera_page)
        self.camipLineEdit.setObjectName(u"camipLineEdit")

        self.horizontalLayout_5.addWidget(self.camipLineEdit)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_5)

        self.addCameraButton = QPushButton(self.camera_page)
        self.addCameraButton.setObjectName(u"addCameraButton")
        self.addCameraButton.setStyleSheet(u"")
        icon7 = QIcon()
        icon7.addFile(u"media/check.png", QSize(), QIcon.Normal, QIcon.Off)
        self.addCameraButton.setIcon(icon7)
        self.addCameraButton.setIconSize(QSize(32, 32))

        self.horizontalLayout_7.addWidget(self.addCameraButton)


        self.verticalLayout_7.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.tableWidget = QTableWidget(self.camera_page)
        self.tableWidget.setObjectName(u"tableWidget")

        self.horizontalLayout_6.addWidget(self.tableWidget)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.removeCamButton = QPushButton(self.camera_page)
        self.removeCamButton.setObjectName(u"removeCamButton")
        self.removeCamButton.setStyleSheet(u"")
        icon8 = QIcon()
        icon8.addFile(u"media/close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.removeCamButton.setIcon(icon8)
        self.removeCamButton.setIconSize(QSize(22, 22))

        self.verticalLayout_6.addWidget(self.removeCamButton)

        self.removeCamButton_2 = QPushButton(self.camera_page)
        self.removeCamButton_2.setObjectName(u"removeCamButton_2")
        self.removeCamButton_2.setStyleSheet(u"")
        self.removeCamButton_2.setIconSize(QSize(22, 22))

        self.verticalLayout_6.addWidget(self.removeCamButton_2)


        self.horizontalLayout_6.addLayout(self.verticalLayout_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_6)


        self.verticalLayout_8.addLayout(self.verticalLayout_7)


        self.gridLayout_3.addLayout(self.verticalLayout_8, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.camera_page)
        self.edit_page = QWidget()
        self.edit_page.setObjectName(u"edit_page")
        self.gridLayout_2 = QGridLayout(self.edit_page)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.edit_page)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setFont(font)

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.edit_page)
        self.user_page = QWidget()
        self.user_page.setObjectName(u"user_page")
        self.gridLayout_4 = QGridLayout(self.user_page)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_9 = QLabel(self.user_page)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setFont(font)

        self.gridLayout_4.addWidget(self.label_9, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.user_page)
        self.search_page = QWidget()
        self.search_page.setObjectName(u"search_page")
        self.gridLayout_5 = QGridLayout(self.search_page)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.search_string_label = QLabel(self.search_page)
        self.search_string_label.setObjectName(u"search_string_label")
        self.search_string_label.setFont(font)

        self.gridLayout_5.addWidget(self.search_string_label, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.search_page)

        self.verticalLayout_5.addWidget(self.stackedWidget)

        self.stackedWidget.raise_()
        self.header_widget.raise_()

        self.gridLayout.addWidget(self.widget, 0, 2, 1, 1)

        self.full_menu_widget = QWidget(self.centralwidget)
        self.full_menu_widget.setObjectName(u"full_menu_widget")
        self.full_menu_widget.setMinimumSize(QSize(191, 0))
        self.verticalLayout_4 = QVBoxLayout(self.full_menu_widget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.logo_label_2 = QLabel(self.full_menu_widget)
        self.logo_label_2.setObjectName(u"logo_label_2")
        self.logo_label_2.setMaximumSize(QSize(193, 50))
        self.logo_label_2.setPixmap(QPixmap(u":/media/media/wiselens-logo-full.png"))
        self.logo_label_2.setScaledContents(True)

        self.verticalLayout_4.addWidget(self.logo_label_2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.home_btn_2 = QPushButton(self.full_menu_widget)
        self.home_btn_2.setObjectName(u"home_btn_2")
        self.home_btn_2.setIcon(icon)
        self.home_btn_2.setIconSize(QSize(30, 30))
        self.home_btn_2.setCheckable(True)
        self.home_btn_2.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.home_btn_2)

        self.cam_btn_2 = QPushButton(self.full_menu_widget)
        self.cam_btn_2.setObjectName(u"cam_btn_2")
        self.cam_btn_2.setIcon(icon1)
        self.cam_btn_2.setIconSize(QSize(30, 30))
        self.cam_btn_2.setCheckable(True)
        self.cam_btn_2.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.cam_btn_2)

        self.edit_btn_2 = QPushButton(self.full_menu_widget)
        self.edit_btn_2.setObjectName(u"edit_btn_2")
        self.edit_btn_2.setMaximumSize(QSize(16777215, 50))
        self.edit_btn_2.setIcon(icon2)
        self.edit_btn_2.setIconSize(QSize(24, 24))
        self.edit_btn_2.setCheckable(True)
        self.edit_btn_2.setAutoExclusive(True)

        self.verticalLayout_2.addWidget(self.edit_btn_2)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)

        self.verticalSpacer_2 = QSpacerItem(20, 291, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.exit_btn_2 = QPushButton(self.full_menu_widget)
        self.exit_btn_2.setObjectName(u"exit_btn_2")
        self.exit_btn_2.setIcon(icon3)
        self.exit_btn_2.setIconSize(QSize(24, 24))
        self.exit_btn_2.setCheckable(True)
        self.exit_btn_2.setAutoExclusive(True)

        self.verticalLayout_4.addWidget(self.exit_btn_2)


        self.gridLayout.addWidget(self.full_menu_widget, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.menu_btn.toggled.connect(self.icon_only_widget.setVisible)
        self.menu_btn.toggled.connect(self.full_menu_widget.setHidden)
        self.cam_btn_1.toggled.connect(self.cam_btn_2.setChecked)
        self.edit_btn_1.toggled.connect(self.edit_btn_2.setChecked)
        self.edit_btn_2.toggled.connect(self.edit_btn_1.setChecked)
        self.cam_btn_2.toggled.connect(self.cam_btn_1.setChecked)
        self.home_btn_1.toggled.connect(self.home_btn_2.setChecked)
        self.home_btn_2.toggled.connect(self.home_btn_1.setChecked)
        self.exit_btn_2.clicked.connect(MainWindow.close)
        self.exit_btn_1.clicked.connect(MainWindow.close)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.logo_label_1.setText("")
        self.home_btn_1.setText("")
        self.cam_btn_1.setText("")
        self.edit_btn_1.setText("")
        self.exit_btn_1.setText("")
        self.menu_btn.setText("")
        self.search_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.search_btn.setText("")
        self.user_btn.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">This is a 7 day free trail.</p><p align=\"center\">Click on the User button on the top left to register a license.</p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">To add a camera, </p><p align=\"center\">enter camera name and it's IP address</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enter your camera name below.<br/>eg. Cam-1</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Camera Name:", None))
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enter your camera IP address below in this format.</p><p>https://ipaddress:port/video</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.label_4.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Camera IP Address:", None))
#if QT_CONFIG(whatsthis)
        self.camipLineEdit.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Enter your camera IP address in this format. </p><p>https://ipaddress:port/video</p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.camipLineEdit.setText("")
#if QT_CONFIG(tooltip)
        self.addCameraButton.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add Camera</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.addCameraButton.setText("")
#if QT_CONFIG(tooltip)
        self.removeCamButton.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Remove Camera</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.removeCamButton.setText(QCoreApplication.translate("MainWindow", u" Delete camera", None))
#if QT_CONFIG(tooltip)
        self.removeCamButton_2.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Annotate Camera</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.removeCamButton_2.setText(QCoreApplication.translate("MainWindow", u"Select camera\n"
" for Annotation", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Here you can Annotate your selected camera feed.</p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">This page is for user authentication</p></body></html>", None))
        self.search_string_label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Search Page</p></body></html>", None))
        self.logo_label_2.setText("")
        self.home_btn_2.setText(QCoreApplication.translate("MainWindow", u" Home", None))
        self.cam_btn_2.setText(QCoreApplication.translate("MainWindow", u" Add Camera", None))
        self.edit_btn_2.setText(QCoreApplication.translate("MainWindow", u" Annotate Camera", None))
        self.exit_btn_2.setText(QCoreApplication.translate("MainWindow", u" Exit", None))
    # retranslateUi

