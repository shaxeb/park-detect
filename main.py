import sys
from typing import Optional
from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton
from PySide6.QtCore import Slot, QFile, QTextStream

from ui_app import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

        self.ui.home_btn_1.toggled.connect(lambda: self.on_button_toggled(0))
        self.ui.home_btn_2.toggled.connect(lambda: self.on_button_toggled(0))
        self.ui.cam_btn_1.toggled.connect(lambda: self.on_button_toggled(1))
        self.ui.cam_btn_2.toggled.connect(lambda: self.on_button_toggled(1))
        self.ui.edit_btn_1.toggled.connect(lambda: self.on_button_toggled(2))
        self.ui.edit_btn_2.toggled.connect(lambda: self.on_button_toggled(2))

        self.ui.user_btn.clicked.connect(self.user_btn_clicked)
        self.ui.search_btn.clicked.connect(self.search_btn_clicked)

    #functions to searching
    def search_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(4)
        search_text = self.ui.search_input.text().strip()
        if search_text:
            self.ui.search_string_label.setText(search_text)

    #function for changing to user page
    def user_btn_clicked(self):
        self.ui.stackedWidget.setCurrentIndex(3)
    
    #change QPushButton Checkable status when stackedWidget index changed 
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton) \
                    + self.ui.full_menu_widget.findChildren(QPushButton)
        
        for btn in btn_list:
            if index in [3,4]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)


    def on_button_toggled(self, index):
        if index >= 0 and index < self.ui.stackedWidget.count():
            self.ui.stackedWidget.setCurrentIndex(index)




if __name__ == "__main__":
    app = QApplication(sys.argv)

    # loading stylesheet

    with open("style.qss", "r") as stylesheet:
        stylesheet = stylesheet.read()

    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())