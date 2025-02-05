import cv2
import numpy as np
from PyQt6 import QtGui
from PyQt6.QtGui import QPixmap

# aqui almacenamos los centros de TODAS las figuras y contornos y eso
# [coordenada x, coordenada y, valores rgb de ese pixel]
# green = respuestas seleccionadas, red = respuestas no seleccionadas
centroids = []

def ProcessImage(original_image):
    selected_answers_image = RecognizeSelectedAnswers(original_image)  # pa poner en verde las que sí son

    # modificar imagen para reconocer solo respuestas seleccionadas
    non_selected_answers_image = RecognizeNotSelectedAnswers(original_image)
    cv2.imshow("cosa",non_selected_answers_image)

    # delimitar filas de respuestas
    DelimitateAnswersRows(original_image)

    return selected_answers_image

def RecognizeSelectedAnswers(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # edge detection
    edges = cv2.Canny(blurred_image, 212, 255)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    selected_answers_image = original_image.copy()

    hierarchy = hierarchy[0]

    for i,c in enumerate(contours):
        area = cv2.contourArea(c)

        # los contornos se generan en la imagen de arriba a abajo, de derecha a izquierda
        # jerarquia de nodos [sig, anterior, hijo, padre] (checar consola)
        # agarramos los que no tienen hijos ni padres
        # esta jalada no agarra bien los que quiero ptm
        # TODOS TIENEN QUE SER CIRCULOS CERRRADOS PARA QUE NO SE ARRUINE LA JERARQUIA (mover el threshold de area?)
        if 120 < area < 500 and hierarchy[i][2] == -1:
            # pa calcular el centroide de cada contorno
            moment = cv2.moments(c)
            x = int(moment["m10"] / moment["m00"])
            y = int(moment["m01"] / moment["m00"])
            centroids.append((x, y, "green"))
            #print("x:", x, " y:", y, " color:", "green")

            selected_answers_image = cv2.drawContours(selected_answers_image, [c], 0, (0, 255, 0), 2)

    print(hierarchy)
    cv2.imshow("edges", edges)
    #cv2.imshow("selected answers", selected_answers_image)
    return selected_answers_image


# fuck blob detection, i'm now edging
def RecognizeNotSelectedAnswers(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # edge detection
    edges = cv2.Canny(blurred_image, 225, 255)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    non_selected_answers_image = original_image.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if 90 < area < 180:
            # pa calcular el centroide de cada contorno
            moment = cv2.moments(c)

            x = int(moment["m10"] / moment["m00"])
            y = int(moment["m01"] / moment["m00"])
            centroids.append((x, y, "red"))

            #print("x:", x, " y:", y, " color:", "red")

            non_selected_answers_image = cv2.circle(non_selected_answers_image, (x, y), 5, (0, 0, 255), -1)

    return non_selected_answers_image

def DelimitateAnswersRows(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    th, thresholded_image = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(image=thresholded_image, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    for c in contours:
        # calculate centroids for each contour
        area = cv2.contourArea(c)
        if 10000 < area < 100000:
            original_image = cv2.drawContours(original_image, [c], -1, (0, 255, 0), 2)

    cv2.imshow("contourrsss", original_image)

def CvToPixmap(cv_image):
    # al parecer tienes que traducir(?) los pixeles de RGB a BGR (?????) pa mostrar la imagen en pyqt(?????????)
    image_temp = QtGui.QImage(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB), cv_image.shape[1], cv_image.shape[0], cv_image.shape[1] * 3, QtGui.QImage.Format.Format_RGB888)
    return QPixmap(image_temp)