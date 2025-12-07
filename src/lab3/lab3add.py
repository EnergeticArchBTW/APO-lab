import cv2  # biblioteka do wczytywania/zapisu obrazów
from pathlib import Path  # do pracy ze ścieżkami
from tkinter import filedialog  # do okna wyboru pliku
from tkinter import Toplevel, Canvas #do okna z obrazem
from tkinter import messagebox # do błędów
import tkinter as tk # do tablicy LUT
from tkinter import ttk # do tablicy LUT
from PIL import Image, ImageTk  # do konwersji obrazów do formatu Tkinter
import numpy as np # do operacji na tablicach
import globals_var  # zmienne globalne
from win_thread import win_thread
from basic import *

"""funkcje do labów 3, które wewnętrznie coś robią i nie są bezpośrednio wywoływane"""

# zad 1
def return_value_wrapper(image, value):
    """
    Ta funkcja 'oszukuje' funkcję threshold(). Zamiast zwracać obraz,
    zwraca samą wartość liczbową z suwaka.
    """
    return value