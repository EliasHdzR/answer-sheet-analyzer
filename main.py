from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QGridLayout, QWidget, QTextEdit, QFileDialog
from PyQt6 import QtGui
import cv2
import numpy as np

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
        self.buttonOpen.clicked.connect(self.handleOpen)

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

    def handleOpen(self):
        start = "."

        path = QFileDialog.getOpenFileName(self, "Choose File", start, "Images(*.jpg *.png)")[0]
        if path == "": return

        self.ActualizarImagen(path)

    def ActualizarImagen(self, filepath):
        self.originalImageFrame.clear()
        self.processedImageFrame.clear()
        self.originalImage = cv2.imread(filepath)

        # pa poder reescalar la imagen en el contenedor pero manteniendo un factor de escalado pa que no se vea feo
        frame_width = self.originalImageFrame.size().width()
        scale_factor = frame_width / self.originalImage.shape[1]
        self.originalImage = cv2.resize(self.originalImage, None, fx= scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)


        pixmap = CvToPixmap(self.originalImage)
        self.originalImageFrame.setPixmap(pixmap)

    def ProcessImage(self):
        #image = cv2.blur(self.originalImage, (5, 5)) # normal
        #image = cv2.GaussianBlur(self.originalImage, (5, 5), 0) # normal
        image = cv2.medianBlur(self.originalImage, 15)                               # este está bien culero jajaja
        #image = cv2.bilateralFilter(self.originalImage, 5, 21, 8)       # de los mejores
        th, im = cv2.threshold(image, 77, 255, cv2.THRESH_BINARY)

        # Default values of parameters are tuned to extract dark circular blobs.
        params = cv2.SimpleBlobDetector_Params()

        params.filterByArea = True
        params.maxArea = 100000

        params.filterByCircularity = True
        params.minCircularity = 0.5

        params.filterByConvexity = True
        params.minConvexity = 0.5

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(im)

        im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0, 0, 255),
                                              cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        imx = self.originalImage.copy()
        for keypoint in keypoints:
            print(keypoint)
            x = int(keypoint.pt[0])
            y = int(keypoint.pt[1])
            s = keypoint.size / 2
            if s > 7:
                imx = cv2.circle(imx, (int(x), int(y)), int(s), (0, 255), 2)

        cv2.imshow("Image", im_with_keypoints)
        pixmap = CvToPixmap(imx)
        self.processedImageFrame.setPixmap(pixmap)

def CvToPixmap(cv_image):
    # al parecer tienes que traducir(?) los pixeles de RGB a BGR (?????) pa mostrar la imagen en pyqt(?????????)
    image_temp = QtGui.QImage(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB), cv_image.shape[1], cv_image.shape[0], cv_image.shape[1] * 3, QtGui.QImage.Format.Format_RGB888)
    return QPixmap(image_temp)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())