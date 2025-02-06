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
    
    # Obtener las respuestas detectadas
    question_answers = DelimitateAnswersRows(original_image)  # Ahora devuelve los datos

    return selected_answers_image, question_answers

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

            non_selected_answers_image = cv2.circle(non_selected_answers_image, (x, y), 2, (0, 0, 255), -1)

    return non_selected_answers_image

def DelimitateAnswersRows(original_image):
    img_gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    th, thresholded_image = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(image=thresholded_image, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

    question_answers = []  # Lista para almacenar preguntas y respuestas seleccionadas
    num_pregunta = 0
    a=0
    for c in contours:
        area = cv2.contourArea(c)
        if 10000 < area < 100000:
            a=a+1
            if a!=1:
                num_pregunta += 1
                print(a)
                print(num_pregunta)
                original_image = cv2.drawContours(original_image, [c], -1, (0, 255, 0), 2)
    
                # Obtener el bounding box del rectángulo
                x, y, w, h = cv2.boundingRect(c)   

                # Dibujar el número de la pregunta arriba del rectángulo
                cv2.putText(original_image, f"Columna {num_pregunta}", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2) 

                # Dividir en 20 partes iguales
                num_divisiones = 20
                altura_division = h // num_divisiones  # Altura de cada pregunta    
                espacios = w // 4  # Dividir en 4 opciones (A, B, C, D)sdf

                # Dibujar las líneas horizontales dentro del rectángulo
                for i in range(1, num_divisiones):
                    if i == 1:
                        y = y + ((i * altura_division)//3)
                    y_inicio = (y + i * altura_division) - ((i * altura_division)//20) - altura_division
                    y_fin = (y + (i + 1) * altura_division) - ((i * altura_division)//20) - altura_division
                    y_actual = (y + i * altura_division) - ((i * altura_division)//20)
                    cv2.line(original_image, (x, y_actual), (x + w, y_actual), (0, 255, 255), 2)  # Líneas amarillas
                
                    # Dibujar puntos en el centro de cada opción (A, B, C, D)
                    for j in range(4):  # 4 opciones
                        cx = x + j * ((espacios//4)*3) + ((espacios//2)*3)  # Centro de la opción
                        cy = (y_inicio + y_fin) // 2  # Centro vertical de la fila
                       #cv2.circle(original_image, (cx, cy), 5, (255, 0, 0), -1)  # Puntos azules


                    # Verificar qué opción se seleccionó en esta pregunta
                    seleccionada = None
                    opciones = ["A", "B", "C", "D"]
                    columna = 0
                    for (cX, cY, color) in centroids:
                        if num_pregunta == 1:
                            columna += 1
                        if y_inicio <= cY < y_fin and color == "red":  # Si está dentro de la fila
                            seleccionada = None  # Valor por defecto en caso de no encontrar coincidencia

                            for j in range(4):  # 4 opciones
                                cx = x + j * ((espacios // 4) * 3) + ((espacios // 2) * 3)  # Centro de la opción
                                if (cx-(espacios//4)) <= cX <=(cx+(espacios//4)):
                                   cv2.circle(original_image, (cx, cY), 2, (255,0, 0), -1)  # Opciones
                                   cv2.circle(original_image, (cX, cY), 2, (0, 0, 255), -1)  #Opción elegida
                                   seleccionada = opciones[j]
                                   print("Columna: " + str(a) + "| Pregunta: " + str(num_pregunta + (i-2)) + "| Opción: " + str(seleccionada))
                                   question_answers.append((a, num_pregunta + (i-2), seleccionada))
                                   break


    # Imprimir en consola
    print("\nRespuestas detectadas:")
    for columna, pregunta, respuesta in question_answers:
        print(f"Pregunta {pregunta}: Opción {respuesta}")
        
    cv2.imshow("contourrsss", original_image)

    return question_answers



def CvToPixmap(cv_image):
    # al parecer tienes que traducir(?) los pixeles de RGB a BGR (?????) pa mostrar la imagen en pyqt(?????????)
    image_temp = QtGui.QImage(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB), cv_image.shape[1], cv_image.shape[0], cv_image.shape[1] * 3, QtGui.QImage.Format.Format_RGB888)
    return QPixmap(image_temp)
