from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        loader = QUiLoader()
        self.ui = loader.load("assets/ui_files/mainwindow.ui")

        # Set the central widget of the main window
        self.setCentralWidget(self.ui)

        # Connect any necessary signals and slots


if __name__ == "__main__":
    # Construct the QApplication
    app = QApplication([])

    # Set the required attributes
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    # Rest of your code...
    window = MainWindow()
    window.show()
    app.exec()