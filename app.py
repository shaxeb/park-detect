from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        loader = QUiLoader()
        self.ui = loader.load("assets/ui_files/mainwindow.ui")


        
        # Find the buttons in the UI file
        homeButton = self.ui.findChild(QPushButton,"homeButton")
        cameraButton = self.ui.findChild(QPushButton, "cameraButton")
        editButton = self.ui.findChild(QPushButton, "editButton")
        userButton = self.ui.findChild(QPushButton, "userButton")
        logoLabel = self.ui.findChild(QLabel, "logoLabel")
        

        # Load the icon files
        homeIcon = QIcon("assets/ui_files/media/home.png")
        camIcon = QIcon("assets/ui_files/media/casino-cctv.png")
        editIcon = QIcon("assets/ui_files/media/edit.png")
        userIcon = QIcon("assets/ui_files/media/user.png")
        logoLabelPixmap = QPixmap("assets/ui_files/media/wiselens-logo-full.png")

        # Set the icons for the widgets
        homeButton.setIcon(homeIcon)
        cameraButton.setIcon(camIcon)
        editButton.setIcon(editIcon)
        userButton.setIcon(userIcon)
        logoLabel.setPixmap(logoLabelPixmap)
        

        # Set the central widget of the main window
        self.setCentralWidget(self.ui)

        # Connect any necessary signals and slots


if __name__ == "__main__":
   # Set the required attributes
   QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
   QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

   # Construct the QApplication
   app = QApplication([])

   # Rest of your code...
   window = MainWindow()
   window.show()
   app.exec()