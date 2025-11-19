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
from lab1.lab1add import * 

"""funkcje zrobione na labach 3"""

# zad 1 - rozciąganie histogramu z zadanym przez użytkownika zakresie
def get_bounds_from_current_image():
    """
    Pobiera histogram (zliczenia) i wylicza domyślne p1 i p2
    dla sfocusowanych obrazów monochromatycznych (a dla kolorowych nic nie zwraca).
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
        return None, None
        """
        # Obraz Kolorowy: musimy znaleźć globalne min/max dla wszystkich kanałów.
        # Sumujemy histogramy R, G, B w jeden "łączny", żeby znaleźć
        # pierwszy i ostatni piksel występujący w JAKIMKOLWIEK kanale.
        lut_r, lut_g, lut_b = hist_data["lut"]
        
        # Sumujemy listy element po elemencie
        combined_lut = [r + g + b for r, g, b in zip(lut_r, lut_g, lut_b)]
        
        p1, p2 = min_max_lut(combined_lut)
        """

    return p1, p2

def return_value_wrapper(image, value):
    """
    Ta funkcja 'oszukuje' funkcję threshold(). Zamiast zwracać obraz,
    zwraca samą wartość liczbową z suwaka.
    """
    return value

# --- GŁÓWNA FUNKCJA: Rozciąganie Histogramu ---
def stretch_histogram_operation():
    # 1. Pobieramy domyślne zakresy z obrazu (Lmin, Lmax)
    default_p1, default_p2 = get_bounds_from_current_image()
    
    # Aplikacja na obrazie
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        img_data = img_info["image"]
        #jeżeli kolorowy
        if len(img_data.shape) != 2:
            messagebox.showerror("Błąd", "Operacja rozciągania histogramu działa tylko na obrazach monochromatycznych!")
            return
    else:
        return
    
    # --- KROK A: Pobieramy p1 (Patrząc na histogram) ---
    # Tworzymy nowe okno dialogowe dla funkcji threshold
    dialog_p1 = Toplevel(globals_var.root)

    # Wywołujemy funkcję threshold w trybie "zwracania wartości"
    # Przekazujemy naszą 'fałszywą' funkcję return_value_wrapper
    p1 = threshold(
        dialog_p1, 
        "Rozciąganie: Wybierz p1 (Początek histogramu)", 
        return_value_wrapper, 
        "", 
        show_result=False,
        initial_value=default_p1
    )
    
    # Jeśli użytkownik anulował, p1 będzie None
    if p1 is None:
        messagebox.showerror("Błąd", "Należy wybrać wartość p1!")
    
    dialog_p2 = Toplevel(globals_var.root)
    
    # Wywołujemy ponownie dla p2
    p2 = threshold(
        dialog_p2, 
        "Rozciąganie: Wybierz p2 (Koniec histogramu)", 
        return_value_wrapper, 
        "", 
        show_result=False,
        initial_value=default_p2
    )
    
    if p2 is None:
        messagebox.showerror("Błąd", "Należy wybrać wartość p2!")

    # --- KROK C: Pobieramy q3 i q4 (Zakres wynikowy) ---
    # Tu histogram nie jest potrzebny, więc używamy prostego simpledialog
    q3 = get_integer_input(globals_var.root, "Rozciąganie", "Podaj q3 (Zakres wynikowy od):")
    if q3 is None:
        messagebox.showerror("Błąd", "Należy wybrać wartość q3!")

    q4 = get_integer_input(globals_var.root, "Rozciąganie", "Podaj q4 (Zakres wynikowy do):", 255, q3)
    if q4 is None:
        messagebox.showerror("Błąd", "Należy wybrać wartość q4!")

    # --- KROK D: Obliczenia (Algorytm z wykładu) ---
    # Teraz mamy wszystkie 4 zmienne: p1, p2, q3, q4
    
    transform_lut = np.zeros((256,), dtype='uint8')

    # Zabezpieczenie dzielenia przez zero
    if p2 == p1:
        scale = 0
    else:
        scale = (q4 - q3) / (p2 - p1)

    for x in range(256):
        if x < p1:
            new_val = q3
        elif x > p2:
            new_val = q4
        else:
            val = (x - p1) * scale + q3
            new_val = np.clip(round(val), 0, 255)
        
        transform_lut[x] = new_val
        
    # Aplikacja LUT
    result_img = cv2.LUT(img_data, transform_lut)
        
    # Wyświetlenie wyniku
    title_suffix = f"_stretch_{p1}-{p2}_to_{q3}-{q4}"
    show_image(result_img, new_file_name(Path(img_info["filename"]), title_suffix))

# zad 2 p.1

#Implementacja progowanie z dwoma progami wyznaczonymi przez użytkownika
def threshold_preserve_gray_user():
    """
    Funkcja progowania z zachowaniem poziomów szarości.
    Piksele poniżej t1 ustawiane są na 0,
    piksele powyżej t2 ustawiane są na 255,
    a piksele pomiędzy t1 i t2 pozostają bez zmian.
    """

    img_info, image = get_focused_mono_image()
    if image is None:
        return None

    dialog_t1 = Toplevel(globals_var.root)
    t1 = threshold(
        dialog_t1, 
        "Progowanie: Wybierz próg t1", 
        return_value_wrapper, 
        "", 
        show_result=False
    )

    dialog_t2 = Toplevel(globals_var.root)
    t2 = threshold(
        dialog_t2, 
        "Progowanie: Wybierz próg t2", 
        return_value_wrapper, 
        "", 
        show_result=False
    )

    # Tworzymy kopię obrazu, aby nie modyfikować oryginału
    result = cv2.inRange(image, t1, t2)
    
    show_image(result, new_file_name(Path(img_info["filename"]), f"_threshold_preserve_gray_{t1}-{t2}"))