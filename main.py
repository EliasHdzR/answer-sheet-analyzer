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
        """
        Abre el dialogo para seleccionar una imagen
        """

        start = "./fotos"
        path = QFileDialog.getOpenFileName(self, "Choose File", start, "Images(*.jpg *.png)")[0]
        if path == "": return
        self.UpdateImage(path)

    def UpdateImage(self, filepath):
        """
        Actualiza la imagen en el contenedor con la imagen seleccionada en la ventana de dialogo
        :param filepath: str
        """

        self.originalImageFrame.clear()
        self.processedImageFrame.clear()
        self.answers.setText("Answers will be displayed here")

        # pa poder reescalar la imagen en el contenedor pero manteniendo un factor de escalado pa que no se vea feo
        self.originalImage = cv2.imread(filepath)
        guiImage = self.originalImage.copy()

        # estoy bien idiota jaja la imagen con la que estabamos trabajando se deformaba segun la forma de la ventana
        # por eso el tamaño de la gui afectaba a los resultados, ya lo puse a un tamaño fijo de 815x612 que es el bueno
        frame_width = self.originalImageFrame.size().width()
        scale_factor = frame_width / self.originalImage.shape[1]
        self.originalImage = cv2.resize(self.originalImage, (815,612), interpolation=cv2.INTER_AREA)
        guiImage = cv2.resize(guiImage, None, fx= scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

        pixmap = image_processor.CvToPixmap(guiImage)
        self.originalImageFrame.setPixmap(pixmap)

    def ProcessImage(self):
        """
        Procesa la imagen seleccionada y muestra las respuestas en el QTextEdit
        """

        self.processedImage, question_answers = image_processor.ProcessImage(self.originalImage)
        
        # Convertir la lista de respuestas a un string formateado
        self.answers.setStyleSheet("background-color: white; color: black;")
        question_answers = "".join([f"{answer}" for i, answer in enumerate(question_answers)])
        # Mostrar en el QTextEdit
        self.answers.setText(str(question_answers))
        pixmap = image_processor.CvToPixmap(self.processedImage)
        self.processedImageFrame.setPixmap(pixmap)
        
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
