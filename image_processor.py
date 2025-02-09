import cv2
import numpy as np
from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap

# aqui almacenamos los centros de TODAS las figuras y contornos y eso
# [coordenada x, coordenada y, valores rgb de ese pixel]
# green = respuestas seleccionadas, red = respuestas no seleccionadas
centroids = []

def ProcessImage(original_image):
    centroids.clear()
    croppped_columns = GetSeparatedColumns(original_image)

    for i in range(1,len(croppped_columns)):
        column = croppped_columns[i]
        RecognizeSelectedAnswers(column)
        RecognizeNotSelectedAnswers(column)
        sorted(centroids, key=lambda ctr: ctr[0])

    question_answers = []
    num_question = 1
    switcher = {
        0: "D",
        1: "C",
        2: "B",
        3: "A",
    }

    img_mierda = original_image.copy()
    for i in range(0,len(centroids),4):
        group = centroids[i:i+4]
        found = False

        for j in range(0,len(group)):
            x, y, color = group[j]
            if color == "green":
                img_mierda = cv2.circle(img_mierda, (x, y), 5, (0, 255, 0), -1)
                img_mierda = cv2.putText(img_mierda, str(num_question), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                question_answers.append(f"Question {num_question}: {switcher[j]}\n")
                num_question += 1
                found = True

        #if not found: num_question += 1

    #cv2.imshow("selected answers", selected_answers_image)
    return img_mierda, question_answers

def RecognizeSelectedAnswers(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # edge detection
    edges = cv2.Canny(blurred_image, 255, 255)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # ordenar contornos de izquierda a derecha
    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])
    selected_answers_image = original_image.copy()

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)

        # agarramos solo los pequeños
        if 80 < area < 300:
            moment = cv2.moments(c)

            x = int(moment["m10"] / moment["m00"])
            y = int(moment["m01"] / moment["m00"])

            if not any((cy - 5 < y < cy + 5 and cx - 5 < x < cx + 5) for cx, cy, _ in centroids):
                centroids.append((int(x), int(y), "green"))
                selected_answers_image = cv2.circle(selected_answers_image, (x, y), 5,
                                                    (0, 255, 0), -1)

    #cv2.imshow("all circles", selected_answers_image)


# fuck blob detection, i'm now edging
def RecognizeNotSelectedAnswers(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # edge detection
    edges = cv2.Canny(blurred_image, 200, 255)
    cv2.imshow("edges", edges)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # ordenar contornos de izquierda a derecha y de arriba a abajo
    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])

    non_selected_answers_image = original_image.copy()

    for i,c in enumerate(contours):
        area = cv2.contourArea(c)
        if 90 < area < 180:
            # pa calcular el centroide de cada contorno
            moment = cv2.moments(c)

            x = int(moment["m10"] / moment["m00"])
            y = int(moment["m01"] / moment["m00"])

            # si aparece en centroid entonces lo cambiamos de color de "green" a "red"
            for j, (cx,cy,color)  in enumerate(centroids):
                if cx - 5 < x < cx + 5 and cy - 5 < y < cy + 5:
                    centroids[j] = (cx, cy, "red")
                    if centroids[j][2] == "green":
                        non_selected_answers_image = cv2.circle(non_selected_answers_image, (cx, cy), 5,
                                                                (0, 255, 0), -1)
                    else:
                        non_selected_answers_image = cv2.circle(non_selected_answers_image, (cx, cy), 5,
                                                                (0, 0, 255), -1)
                    break


    #cv2.imshow("non selected answers", non_selected_answers_image)

def GetSeparatedColumns(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    th, thresholded_image = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(image=thresholded_image, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    img_divided = original_image.copy()
    rectangles = []

    for c in contours:
        area = cv2.contourArea(c)
        if 10000 < area < 100000:
            x, y, w, h = cv2.boundingRect(c)
            rectangles.append((x, y, w, h))

    # ordenar rectangulos de izquierda a derecha
    rectangles = sorted(rectangles, key=lambda rect: rect[0])

    # dividismos las columnas de las preguntas
    test_number_column = cropImage(rectangles[0], original_image)
    first_column = cropImage(rectangles[1], original_image)
    second_column = cropImage(rectangles[2], original_image)
    third_column = cropImage(rectangles[3], original_image)
    fourth_column = cropImage(rectangles[4], original_image)

    return test_number_column, first_column, second_column, third_column, fourth_column

def cropImage(rect, image):
    # esto convierte a blanco lo que no esta dentro de la columna de interes, asi no modificamos el tamaño de la imagen
    x, y, w, h = rect
    white_background = np.ones_like(image, dtype=np.uint8) * 255
    white_background[y:y + h, x:x + w] = image[y:y + h, x:x + w]

    return white_background

def CvToPixmap(cv_image):
    # al parecer tienes que traducir(?) los pixeles de RGB a BGR (?????) pa mostrar la imagen en pyqt(?????????)
    image_temp = QtGui.QImage(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB), cv_image.shape[1], cv_image.shape[0], cv_image.shape[1] * 3, QtGui.QImage.Format.Format_RGB888)
    return QPixmap(image_temp)
