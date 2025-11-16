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

"""
Udoskonalenie oprogramowania przygotowanego na zajęciach przez dołożenie operacji zmniejszenia
udziału szumu przez uśredniania kilku obrazów zebranych w takich samych warunkach oraz operacji
logicznych na zaszumionych obrazach binarnych. 
"""

def averaging_photos():
    images = select_images_window()

    # 1. Wczesna walidacja (czy w ogóle mamy co robić)
    if not images or len(images) < 2:
        messagebox.showerror("Błąd", "Należy wybrać co najmniej dwa obrazy!")
        return

    # 2. Ujednolicona walidacja wymiarów i typu
    first_shape = images[0].shape
    first_dims = len(first_shape)

    # Sprawdzamy, czy pierwszy obraz jest poprawny (mono lub RGB)
    if not (first_dims == 2 or (first_dims == 3 and first_shape[2] == 3)):
        messagebox.showerror("Błąd", "Pierwszy obraz nie jest ani monochromatyczny, ani kolorowy (RGB)!")
        return

    # Sprawdzamy, czy wszystkie kolejne obrazy są DOKŁADNIE takie same jak pierwszy
    for img in images[1:]:
        if img.shape != first_shape:
            messagebox.showerror("Błąd", "Wszystkie obrazy muszą mieć te same wymiary i typ (mono/kolor)!")
            return

    # --- 3. Uniwersalny blok obliczeniowy ---
    # Ta część zadziała identycznie dla obrazów (H, W) i (H, W, 3)

    try:
        # Używamy np.float64 dla maksymalnej precyzji, aby uniknąć błędów zaokrągleń
        sum_images = np.zeros_like(images[0], dtype=np.float64)
        ilosc = len(images)

        for img in images:
            # dodawanie i dzielenie na bieżąco
            sum_images += img.astype(np.float64) / ilosc

        # Konwersja z powrotem na uint8 (0-255)
        # np.clip upewnia się, że minimalne błędy float nie wyjdą poza zakres
        result = np.clip(np.round(sum_images), 0, 255).astype(np.uint8)

        # 4. Wyświetlanie wyniku
        # Wynik 'result' będzie miał ten sam kształt (mono lub kolor) co obrazy wejściowe
        show_image(result, f"Average_{ilosc}_images")

        # --- pokazanie różnicy bezwzględnej między pierwszym obrazem a wynikiem ---
        img_oryginal_float = images[0].astype(np.float64)
        img_result_float = result.astype(np.float64)

        abs_diff = cv2.absdiff(img_oryginal_float, img_result_float)
        # wzmocnienie
        SCALING_FACTOR = 100 
        scaled_diff = abs_diff * SCALING_FACTOR

        #obcięcie do 0-255
        clipped_diff = np.clip(scaled_diff, 0, 255)

        # konwersja do uint8
        final_diff_image = clipped_diff.astype(np.uint8)
        show_image(final_diff_image, "Absolute_Difference_First_Image_and_Resultx100")

    except Exception as e:
        messagebox.showerror("Błąd obliczeń", f"Wystąpił błąd: {e}")