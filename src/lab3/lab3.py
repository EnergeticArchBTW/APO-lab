import cv2  # biblioteka do wczytywania/zapisu obrazów
from pathlib import Path  # do pracy ze ścieżkami
from tkinter import filedialog  # do okna wyboru pliku
from tkinter import Toplevel, Canvas #do okna z obrazem
from tkinter import messagebox # do błędów
import tkinter as tk # do tablicy LUT
from tkinter import ttk # do tablicy LUT
from tkinter import simpledialog # do pobierania wartości od użytkownika
from PIL import Image, ImageTk  # do konwersji obrazów do formatu Tkinter
import numpy as np # do operacji na tablicach
import globals_var  # zmienne globalne
from win_thread import win_thread
from basic import *
from lab2.lab2add import *

"""funkcje zrobione na labach 3"""

# zad 1 - rozciąganie histogramu z zadanym przez użytkownika zakresie
def get_bounds_from_current_image():
    """
    Pobiera histogram (zliczenia) i wylicza domyślne p1 i p2
    dla sfocusowanych obrazów monochromatycznych i kolorowych.
    """
    # 1. Generujemy statystykę (używamy Twojej funkcji z poprzedniego pytania)
    # Zakładam, że funkcja generate_lut jest dostępna w tym pliku lub zaimportowana
    hist_data = generate_lut() 
    
    if hist_data is None:
        return None, None

    # 2. Wyznaczamy p1 i p2 w zależności od typu obrazu
    if not hist_data["color"]:
        # Obraz Monochromatyczny: proste użycie Twojej funkcji
        p1, p2 = min_max_lut(hist_data["lut"])
    else:
        # Obraz Kolorowy: musimy znaleźć globalne min/max dla wszystkich kanałów.
        # Sumujemy histogramy R, G, B w jeden "łączny", żeby znaleźć
        # pierwszy i ostatni piksel występujący w JAKIMKOLWIEK kanale.
        lut_r, lut_g, lut_b = hist_data["lut"]
        
        # Sumujemy listy element po elemencie
        combined_lut = [r + g + b for r, g, b in zip(lut_r, lut_g, lut_b)]
        
        p1, p2 = min_max_lut(combined_lut)

    return p1, p2