import sqlite3
import json
import cv2
import numpy as np
import sys

from functools import partial
from PySide6 import QtCore, QtGui
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtCore import Slot, QObject, QThread, Signal
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QStackedWidget, QTableWidget, QTableWidgetItem, QWidget, QMessageBox, QLabel)

from app_ui import Ui_MainWindow


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

        self.setWindowTitle("WiseLens AI")

        self.ui.icon_only_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.home_btn_2.setChecked(True)

        self.model = Model()
        self.controller = Controller(self.model, self.ui)

        self.model.current_index = 0
        self.ui.stackedWidget.setCurrentIndex(self.model.current_index)

        self.ui.stackedWidget.currentChanged.connect(
            self.on_stackedWidget_currentChanged)

        self.ui.addCamButton.clicked.connect(self.add_data)
        self.ui.removeCamButton.clicked.connect(self.delete_data)

        # Connect the camTableWidget cellClicked signal to on_table_cell_clicked slot
        self.ui.camTableWidget.cellClicked.connect(self.on_table_cell_clicked)

        # Create a SQLite3 database and a table to store camera data
        self.conn = sqlite3.connect("database.db")
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS cameras (name TEXT UNIQUE, ip TEXT PRIMARY KEY UNIQUE, polygons TEXT, labels TEXT)")

        # Create an instance of the EditPage and add it to the stackedWidget
        self.ui.stackedWidget.addWidget(self.ui.editPage)

    def on_table_cell_clicked(self, row, column):
        self.ui.camnameLineEdit.setText(self.ui.camTableWidget.item(row, 0).text())
        self.ui.camipLineEdit.setText(self.ui.camTableWidget.item(row, 1).text())

    def load_table_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, ip FROM cameras")
        data = cursor.fetchall()

        self.ui.camTableWidget.setRowCount(len(data))
        self.ui.camTableWidget.setColumnCount(2)

        for row, items in enumerate(data):
            for col, item in enumerate(items[:2]):
                table_item = QTableWidgetItem(str(item))
                self.ui.camTableWidget.setItem(row, col, table_item)

    @Slot()
    def add_data(self):
        value1 = self.ui.camnameLineEdit.text()
        value2 = self.ui.camipLineEdit.text()

        if value1 and value2:
            try:
                cursor = self.conn.cursor()
                # Check if the IP or camera name already exists in the database
                cursor.execute("SELECT COUNT(*) FROM cameras WHERE ip = ? OR name = ?", (value2, value1))
                result = cursor.fetchone()[0]
                if result > 0:
                    QMessageBox.warning(self, "Duplicate Entry",
                                        "The IP address or camera name already exists in the database.")
                else:
                    cursor.execute("INSERT INTO cameras (name, ip) VALUES (?, ?)", (value1, value2))
                    self.conn.commit()
                    self.load_table_data()
                    self.clear_input_fields()
            except Exception as e:
                print("Error inserting data:", e)
        else:
            QMessageBox.warning(self, "Missing Values", "Please enter both Name and IP.")

    @Slot()
    def delete_data(self):
        selected_row = self.ui.camTableWidget.currentRow()
        if selected_row >= 0:
            ip = self.ui.camTableWidget.item(selected_row, 1).text()
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM cameras WHERE ip = ?", (ip,))
                self.conn.commit()
                self.load_table_data()
                self.clear_input_fields()
            except Exception as e:
                print("Error deleting row:", e)
        else:
            QMessageBox.warning(self, "No Row Selected", "Please select a row to delete.")

    def clear_input_fields(self):
        self.ui.camnameLineEdit.clear()
        self.ui.camipLineEdit.clear()

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
    window.load_table_data()
    window.show()

    sys.exit(app.exec())
