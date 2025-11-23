import cv2
from tkinter import messagebox # do błędów

""" osobny plik oddzielony od całego programu, który przerabia kolorowy obraz na monochromatyczny """

def convert_to_grayscale(image):
    # Konwersja do skali szarości, jeśli trzeba
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 2:
        image_gray = image.copy()
    else:
        messagebox.showerror("Błąd", "Nie udało się zamienić obrazu.")

    return image_gray