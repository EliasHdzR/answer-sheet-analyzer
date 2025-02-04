from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QGridLayout, QWidget, QTextEdit, QFileDialog
import cv2
import image_processor

class ImageFrame(QLabel):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("border: 1px solid black;")

class AnswersFrame(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("border: 1px solid black; background-color: white;")
        self.setPlaceholderText("Answers will be displayed here")

class Window(QWidget):
    def __init__(self):
        # variables
        self.originalImage = None
        self.processedImage = None

        super().__init__()
        self.showMaximized()
        self.setWindowTitle("Answers Analyzer")

        self.buttonOpen = QPushButton("Open Image")
        BUTTON_SIZE = QSize(200, 50)
        self.buttonOpen.setMinimumSize(BUTTON_SIZE)
        self.buttonOpen.clicked.connect(self.HandleOpen)

        self.buttonProcess = QPushButton("Analyze Image")
        self.buttonProcess.setMinimumSize(BUTTON_SIZE)
        self.buttonProcess.clicked.connect(self.ProcessImage)

        self.originalImageFrame = ImageFrame()
        self.processedImageFrame = ImageFrame()
        self.answers = AnswersFrame()

        layout = QGridLayout(self)
        layout.addWidget(self.buttonOpen, 0, 0, 1, 1)
        layout.addWidget(self.buttonProcess, 0, 1, 1, 1)
        layout.addWidget(self.originalImageFrame, 1, 0, 1, 2)
        layout.addWidget(self.processedImageFrame, 1, 2, 1, 2)
        layout.addWidget(self.answers, 1, 4, 1, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 0)

    def HandleOpen(self):
        start = "./fotos"
        path = QFileDialog.getOpenFileName(self, "Choose File", start, "Images(*.jpg *.png)")[0]
        if path == "": return
        self.UpdateImage(path)

    def UpdateImage(self, filepath):
        self.originalImageFrame.clear()
        self.processedImageFrame.clear()
        self.answers.setText("Answers will be displayed here")

        # pa poder reescalar la imagen en el contenedor pero manteniendo un factor de escalado pa que no se vea feo
        self.originalImage = cv2.imread(filepath)
        frame_width = self.originalImageFrame.size().width()
        scale_factor = frame_width / self.originalImage.shape[1]
        self.originalImage = cv2.resize(self.originalImage, None, fx= scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

        pixmap = image_processor.CvToPixmap(self.originalImage)
        self.originalImageFrame.setPixmap(pixmap)

    def ProcessImage(self):
        self.processedImage = image_processor.ProcessImage(self.originalImage)
        pixmap = image_processor.CvToPixmap(self.processedImage)
        self.processedImageFrame.setPixmap(pixmap)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())