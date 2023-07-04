import sys
from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton
from PySide6.QtCore import Slot
from ui_app import Ui_MainWindow

class Model:
    def __init__(self):
        self.current_index = 0

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.home_btn_1.toggled.connect(lambda: self.on_button_toggled(0))
        self.view.home_btn_2.toggled.connect(lambda: self.on_button_toggled(0))
        self.view.cam_btn_1.toggled.connect(lambda: self.on_button_toggled(1))
        self.view.cam_btn_2.toggled.connect(lambda: self.on_button_toggled(1))
        self.view.edit_btn_1.toggled.connect(lambda: self.on_button_toggled(2))
        self.view.edit_btn_2.toggled.connect(lambda: self.on_button_toggled(2))

        self.view.user_btn.clicked.connect(self.user_btn_clicked)
        self.view.search_btn.clicked.connect(self.search_btn_clicked)

    @Slot()
    def search_btn_clicked(self):
        self.view.stackedWidget.setCurrentIndex(4)
        search_text = self.view.search_input.text().strip()
        if search_text:
            self.view.search_string_label.setText(search_text)

    @Slot()
    def user_btn_clicked(self):
        self.view.stackedWidget.setCurrentIndex(3)

    @Slot(int)
    def on_button_toggled(self, index):
        if index >= 0 and index < self.view.stackedWidget.count():
            self.view.stackedWidget.setCurrentIndex(index)
            self.model.current_index = index

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

        self.model = Model()
        self.controller = Controller(self.model, self.ui)

        self.model.current_index = 0
        self.ui.stackedWidget.setCurrentIndex(self.model.current_index)

        self.ui.stackedWidget.currentChanged.connect(self.on_stackedWidget_currentChanged)

    @Slot(int)
    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.icon_only_widget.findChildren(QPushButton) \
                   + self.ui.full_menu_widget.findChildren(QPushButton)
        
        for btn in btn_list:
            if index in [3, 4]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # loading stylesheet
    with open("style.qss", "r") as stylesheet:
        stylesheet = stylesheet.read()

    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
