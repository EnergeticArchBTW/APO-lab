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

"""funkcje zrobione na labach 2"""

# zad 1
def add_images_without_saturation():
    """funkcja dodająca od 2 do 5 obrazów BEZ WYSYCENIA (z zawijaniem) z GUI
    wyświetla wynikowy obraz lub nic nie robi w przypadku błędu
    """

    images = select_images_window()
    ilosc = len(images)

    if not images or ilosc < 2:
        messagebox.showerror("Błąd", "Potrzebne są co najmniej 2 obrazy!")
        return
    
    if ilosc > 5:
        messagebox.showerror("Błąd", "Maksymalnie 5 obrazów!")
        return
    
    # Porównaj wszystkie obrazy z pierwszym
    first_img = images[0]
    for i, img in enumerate(images[1:], 1):
        if not compare_images(first_img, img):
            messagebox.showerror("Błąd", f"Obraz {i+1} nie pasuje do pierwszego!")
            return

    # Kompresja jasności: dzielenie każdego obrazu przez 'ilosc', a następnie sumowanie.
    # 1. Tworzymy "płótno" na wynikową sumę. Musi być typu float,
    #    aby móc przechowywać wartości ułamkowe.
    #    Używamy np.float64 dla maksymalnej precyzji.
    sum_images = np.zeros_like(images[0], dtype=np.float64)
    # 2. Iterujemy przez WSZYSTKIE obrazy
    for img in images:
        # 3. Konwertujemy obraz na float, DZIELIMY przez liczbę obrazów
        #    i dodajemy do naszej sumy.
        sum_images += img.astype(np.float64) / ilosc
    # 4. Na końcu, sum_images zawiera już obliczoną średnią.
    #    Musimy ją tylko zaokrąglić do najbliższej liczby całkowitej
    #    i przekonwertować z powrotem na typ uint8 (0-255).
    result = np.round(sum_images).astype(np.uint8)
    
    show_image(result, f"without_sat")
    #globals_var.current_id += 1

def add_images_with_saturation():
    """funkcja dodająca od 2 do 5 obrazów Z WYSYCENIEM (saturacją, czyli obcinaniem) z GUI
    wyświetla wynikowy obraz lub nic nie robi w przypadku błędu
    """

    images = select_images_window()

    if not images or len(images) < 2:
        messagebox.showerror("Błąd", "Potrzebne są co najmniej 2 obrazy!")
        return
    
    if len(images) > 5:
        messagebox.showerror("Błąd", "Maksymalnie 5 obrazów!")
        return
    
    # Porównaj wszystkie obrazy z pierwszym
    first_img = images[0]
    for i, img in enumerate(images[1:], 1):
        if not compare_images(first_img, img):
            messagebox.showerror("Błąd", f"Obraz {i+1} nie pasuje do pierwszego!")
            return
    
    # Dodawanie Z WYSYCENIEM - OpenCV obcina wartości do 255 (np. 200 + 100 = 255)
    result = images[0].copy()
    for img in images[1:]:
        # cv2.add() wykonuje dodawanie z saturacją
        result = cv2.add(result, img) 
    
    show_image(result, f"with_sat")

def add_number_with_stauration():
    """funkcja dodająca skalar do obrazu Z WYSYCENIEM (saturacją, czyli obcinaniem) z GUI"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być jednokanałowy (czarno-biały)!")
            return
        image = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    value = get_integer_input(globals_var.root, "Dodawanie z wysyceniem - podaj wartość całkowitą")
    if value is None:
        return  # Użytkownik anulował
    
    result = operation_on_scalar(image, 'add', value, saturation=True)
    if result is not None:
        show_image(result, f"add_num_with_sat")

def add_number_without_stauration():
    """funkcja dodająca skalar do obrazu BEZ WYSYCENIA (z zawijaniem) z GUI"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być jednokanałowy (czarno-biały)!")
            return
        image = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    value = get_integer_input(globals_var.root, "Dodawanie bez wysyceniem - podaj wartość całkowitą")
    if value is None:
        return  # Użytkownik anulował
    
    result = operation_on_scalar(image, 'add', value, saturation=False)
    if result is not None:
        show_image(result, f"add_num_without_sat")

def divide_number_with_stauration():
    """funkcja dzieląca obraz przez skalar Z WYSYCENIEM (saturacją, czyli obcinaniem) z GUI"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być jednokanałowy (czarno-biały)!")
            return
        image = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    value = get_integer_input(globals_var.root, "Dzielenie z wysyceniem - podaj wartość całkowitą")
    if value is None:
        return  # Użytkownik anulował
    
    result = operation_on_scalar(image, 'divide', value, saturation=True)
    if result is not None:
        show_image(result, f"divide_num_with_sat")

def divide_number_without_stauration():
    """funkcja dzieląca obraz przez skalar BEZ WYSYCENIA (z zawijaniem) z GUI"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być jednokanałowy (czarno-biały)!")
            return
        image = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    value = get_integer_input(globals_var.root, "Dzielenie bez wysyceniem - podaj wartość całkowitą")
    if value is None:
        return  # Użytkownik anulował
    
    result = operation_on_scalar(image, 'divide', value, saturation=False)
    if result is not None:
        show_image(result, f"divide_num_without_sat")

def multiply_number_with_stauration():
    """funkcja mnożąca obraz przez skalar Z WYSYCENIEM (saturacją, czyli obcinaniem) z GUI"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być jednokanałowy (czarno-biały)!")
            return
        image = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    value = get_integer_input(globals_var.root, "Mnożenie z wysyceniem - podaj wartość całkowitą")
    if value is None:
        return  # Użytkownik anulował
    
    result = operation_on_scalar(image, 'multiply', value, saturation=True)
    if result is not None:
        show_image(result, f"multiply_num_with_sat")

def multiply_number_without_stauration():
    """funkcja mnożąca obraz przez skalar BEZ WYSYCENIA (z zawijaniem) z GUI"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być jednokanałowy (czarno-biały)!")
            return
        image = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    value = get_integer_input(globals_var.root, "Mnożenie bez wysyceniem - podaj wartość całkowitą")
    if value is None:
        return  # Użytkownik anulował
    
    result = operation_on_scalar(image, 'multiply', value, saturation=False)
    if result is not None:
        show_image(result, f"multiply_num_without_sat")

def subtract_images_absolute():
    """
    Oblicza różnicę bezwzględną (absolute difference) dwóch obrazów 
    wybranych przez użytkownika z GUI.
    Wyświetla wynikowy obraz lub nic nie robi w przypadku błędu.
    """

    images = select_images_window()

    # 1. Walidacja - do tej operacji potrzebujemy DOKŁADNIE dwóch obrazów
    if not images or len(images) != 2:
        messagebox.showerror("Błąd", "Potrzebne są dokładnie 2 obrazy do obliczenia różnicy bezwzględnej!")
        return
    
    img1 = images[0]
    img2 = images[1]

    if len(img1.shape) != 2 and len(img2.shape) != 2:
            messagebox.showerror("Błąd", "Obrazy muszą być jednokanałowe (czarno-białe)!")
            return
    
    # 2. Porównanie obrazów (czy mają ten sam rozmiar, typ itp.)
    if not compare_images(img1, img2):
        messagebox.showerror("Błąd", "Obrazy nie są zgodne (np. mają różne rozmiary).")
        return
    
    # 3. Obliczenie różnicy bezwzględnej
    # Funkcja cv2.absdiff jest zoptymalizowana i bezpieczna,
    # oblicza |img1 - img2| dla każdego piksela.
    result = cv2.absdiff(img1, img2)
    
    # 4. Wyświetlenie wyniku
    show_image(result, f"abs_diff")

# zad 2
def convert_grayscale_to_binary_mask():
    """
    Pobiera sfocusowany obraz (8-bit w skali szarości) i konwertuje go
    na maskę binarną (0/255) na podstawie progu podanego przez użytkownika.
    zakładam że threshold zawsze jest 128.
    """
    
    # 1. Pobranie aktywnego obrazu i walidacja
    img_info, image = get_focused_image_data()
    if image is None:
        return # Błąd został już wyświetlony przez get_focused_image_data

    # 2. Sprawdzenie, czy obraz jest monochromatyczny
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacja działa tylko na obrazach monochromatycznych (w skali szarości).")
        return
        
    # 3. wartość progu
    threshold_value = 128
        
    # 4. ALGORYTM: Progowanie (Thresholding)
    # Funkcja cv2.threshold zwraca próg oraz obraz
    _ , binary_mask = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
    
    # 5. Wyświetlenie wyniku
    title = new_file_name(Path(img_info["filename"]), f"_binary_mask_{threshold_value}")
    show_image(binary_mask, title=title)

def convert_binary_to_grayscale_mask():
    """
    Pobiera sfocusowaną maskę binarną i konwertuje ją na maskę 8-bitową
    (w skali szarości) poprzez rozmycie krawędzi (tzw. "feathering").
    """

    # 1. Pobranie aktywnego obrazu i walidacja
    img_info, image = get_focused_image_data()
    if image is None:
        return

    # 2. Sprawdzenie, czy obraz jest monochromatyczny
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacja działa tylko na obrazach monochromatycznych (binarnych).")
        return
        
    # 3. Zapytanie użytkownika o siłę rozmycia
    blur_strength = get_integer_input(globals_var.root, "Podaj siłę rozmycia (Im wyższa, tym miększe przejście.):")
    
    if blur_strength is None: # Użytkownik kliknął "Anuluj"
        return
        
    # 4. ALGORYTM: Rozmycie Gaussa
    # Upewniamy się, że wartość jest nieparzysta (wymóg Gaussa)
    if blur_strength % 2 == 0:
        blur_strength += 1
        
    # Stosujemy silne rozmycie, aby zamienić ostre krawędzie w gradient
    gray_mask = cv2.GaussianBlur(image, (blur_strength, blur_strength), 0)
    
    # 5. Wyświetlenie wyniku
    title = new_file_name(Path(img_info["filename"]), f"_gray_mask_{blur_strength}")
    show_image(gray_mask, title=title)

def not_logic():
    """
    Wykonuje operację logiczną NOT (negację bitową) na aktywnym obrazie,
    zgodnie z definicją ze slajdu (NOT(1)=0, NOT(0)=1).
    Wymagany jest obraz monochromatyczny lub binarny.
    """
    
    # 1. Operacja NOT jest JEDNOARGUMENTOWA.
    # Działamy na aktywnym (sfocusowanym) obrazie.
    img_info, image = get_focused_image_data()
    if image is None:
        return
    
    # 3. Walidacja (dla obrazów monochromatycznych i binarnych)
    if len(image.shape) == 3:
        messagebox.showerror("Błąd", "Operacja NOT działa tylko na obrazach monochromatycznych lub binarnych.")
        return

    # 4. ALGORYTM: Wykonanie operacji NOT (zgodnie ze slajdem)
    #
    # Funkcja cv2.bitwise_not() idealnie realizuje definicję ze slajdu.
    # Odwraca każdy bit w każdym pikselu obrazu.
    #
    # Na przykład dla obrazu 8-bitowego (uint8):
    # Piksel 0 (bity 00000000) -> NOT -> 255 (bity 11111111)
    # Piksel 255 (bity 11111111) -> NOT -> 0 (bity 00000000)
    # Piksel 100 (bity 01100100) -> NOT -> 155 (bity 10011011)
    
    result_image = cv2.bitwise_not(image)

    # 5. Wyświetlenie wyniku
    title = new_file_name(Path(img_info["filename"]), "_NOT")
    show_image(result_image, title=title)

def and_logic():
    """operacja AND jednopunktowa dwuargumentowa wyświetla przetworzony obraz"""
    images = select_images_window()
    
    if and_or_xor_check(images) == False:
        return
    
    # Ta funkcja realizuje logikę ze slajdu (1 AND 1=1, 1 AND 0=0, itd.)
    # dla każdego bitu w odpowiadających sobie pikselach.
    result_image = cv2.bitwise_and(images[0], images[1])

    show_image(result_image, f"and_logic")

def or_logic():
    """operacja OR jednopunktowa dwuargumentowa wyświetla przetworzony obraz"""
    images = select_images_window()

    if and_or_xor_check(images) == False:
        return
    
    # Ta funkcja realizuje logikę ze slajdu
    # dla każdego bitu w odpowiadających sobie pikselach.
    result_image = cv2.bitwise_or(images[0], images[1])
    
    show_image(result_image, f"or_logic")

def xor_logic():
    """operacja XOR jednopunktowa dwuargumentowa wyświetla przetworzony obraz"""
    images = select_images_window()

    if and_or_xor_check(images) == False:
        return
    
    # Ta funkcja realizuje logikę ze slajdu
    # dla każdego bitu w odpowiadających sobie pikselach.
    result_image = cv2.bitwise_xor(images[0], images[1])
    
    show_image(result_image, f"xor_logic")

# Zad 3
def run_gaussian_filter():
    """
    Wykonuje filtrację Gaussa (funkcja specjalna).
    
    Używa dedykowanej funkcji cv2.GaussianBlur i implementuje 
    wymagane 3 tryby obsługi brzegów.
    """
    
    # 1. Pobierz aktywny obraz (użycie twojej funkcji)
    img_info, image = get_focused_image_data()
    if image is None:
        return # Błąd został już wyświetlony

    # 2. Walidacja (zgodnie z wykładem)
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacja Gaussa działa tylko na obrazach monochromatycznych.")
        return

    # 3. Pobierz opcje brzegów od użytkownika (Krok 4)
    options = get_border_options()
    if options is None:
        return # Użytkownik kliknął "Anuluj"

    # 4. Wykonaj filtrowanie na podstawie wyboru
    
    result_image = None
    border_mode = options["mode"]
    border_value = options.get("value", 0)
    
    # [cite_start]Zgodnie z planem i wykładem, używamy maski 3x3 [cite: 33, 35]
    ksize = (3, 3) 
    # Ustawienie sigmaX=0 sprawia, że OpenCV obliczy ją automatycznie z ksize
    sigmaX = 0 

    try:
        if border_mode == "REFLECT":
            # Najprostszy przypadek: cv2.GaussianBlur obsługuje BORDER_REFLECT
            result_image = cv2.GaussianBlur(image, ksize, sigmaX, 
                                            borderType=cv2.BORDER_REFLECT)
        
        elif border_mode == "CONSTANT":
            # Przypadek 2: Wymaga ręcznego dodania ramki (jak w Kroku 2)
            pad_size = 1 # Dla maski 3x3
            h, w = image.shape[:2]
            
            # 1. Dodaj ramkę o wartości 'n'
            padded_image = cv2.copyMakeBorder(image, 
                                              pad_size, pad_size, pad_size, pad_size, 
                                              cv2.BORDER_CONSTANT, 
                                              value=border_value)
            
            # 2. Filtruj z BORDER_ISOLATED
            filtered_padded = cv2.GaussianBlur(padded_image, ksize, sigmaX, 
                                               borderType=cv2.BORDER_ISOLATED)
            
            # 3. Wytnij środek (usuń ramkę)
            result_image = filtered_padded[pad_size : pad_size + h, pad_size : pad_size + w]

        elif border_mode == "CUSTOM_BORDER":
            # Przypadek 3: Wypełnij ramkę *po* obliczeniach (jak w Kroku 3)
            
            # 1. Oblicz filtr, używając bezpiecznego BORDER_REFLECT
            temp_blurred_image = cv2.GaussianBlur(image, ksize, sigmaX, 
                                                  borderType=cv2.BORDER_REFLECT)
            
            # 2. Skopiuj i ręcznie nadpisz 1px ramki
            result_image = temp_blurred_image.copy()
            safe_value = np.clip(border_value, 0, 255).astype(image.dtype)
            
            result_image[0, :] = safe_value  # Góra
            result_image[-1, :] = safe_value # Dół
            result_image[:, 0] = safe_value  # Lewo
            result_image[:, -1] = safe_value # Prawo

        # 5. Wyświetl wynik
        if result_image is not None:
            title = new_file_name(Path(img_info["filename"]), "_gaussian_blur")
            # Użyj twojej funkcji
            show_image(result_image, title=title)
            
    except Exception as e:
        messagebox.showerror("Błąd Gaussa", f"Nie udało się zastosować filtru Gaussa:\n{e}")

def run_sobel_operator():
    """
    Wykonuje detekcję krawędzi operatorem Sobela.
    
    Łączy gradienty z dwóch prostopadłych kierunków (X i Y),
    zgodnie z wykładem.
    Implementuje 3 wymagane tryby obsługi brzegów.
    """
    
    # 1. Pobierz aktywny obraz
    img_info, image = get_focused_image_data()
    if image is None:
        return

    # 2. Walidacja
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operator Sobela działa tylko na obrazach monochromatycznych.")
        return

    # 3. Pobierz opcje brzegów
    options = get_border_options()
    if options is None:
        return

    # 4. Przygotuj parametry
    border_mode = options["mode"]
    border_value = options.get("value", 0)
    
    # Rozmiar maski (zgodnie z zadaniem 3x3)
    ksize = 3
    
    # Używamy głębi 64F (float), aby przechwycić ujemne wartości gradientu,
    # o czym wspomniano na wykładzie.
    ddepth = cv2.CV_64F
    
    # Zmienne na wyniki pośrednie
    sobel_x = None
    sobel_y = None

    try:
        # --- 5. Obliczanie gradientów X i Y z obsługą brzegów ---
        
        # Logika dla BORDER_CONSTANT (wymaga ręcznego dodania ramki)
        if border_mode == "CONSTANT":
            pad_size = 1 # Dla maski 3x3
            h, w = image.shape[:2]
            
            padded_image = cv2.copyMakeBorder(image, 
                                              pad_size, pad_size, pad_size, pad_size, 
                                              cv2.BORDER_CONSTANT, 
                                              value=border_value)
            
            # Oblicz X i Y na obrazie z ramką
            sobel_x_padded = cv2.Sobel(padded_image, ddepth, 1, 0, ksize, 
                                     borderType=cv2.BORDER_ISOLATED)
            sobel_y_padded = cv2.Sobel(padded_image, ddepth, 0, 1, ksize, 
                                     borderType=cv2.BORDER_ISOLATED)
            
            # Wytnij środek (usuń ramkę)
            sobel_x = sobel_x_padded[pad_size : pad_size + h, pad_size : pad_size + w]
            sobel_y = sobel_y_padded[pad_size : pad_size + h, pad_size : pad_size + w]
        
        # Logika dla BORDER_REFLECT i CUSTOM_BORDER (który liczy się jak REFLECT)
        else:
            # cv2.BORDER_REFLECT jest domyślnym bezpiecznym trybem
            sobel_x = cv2.Sobel(image, ddepth, 1, 0, ksize, 
                                borderType=cv2.BORDER_REFLECT)
            sobel_y = cv2.Sobel(image, ddepth, 0, 1, ksize, 
                                borderType=cv2.BORDER_REFLECT)
        
        # --- 6. Łączenie gradientów ---
        # Wykład opisuje to jako: pierwiastek z sumy kwadratów.
        # W OpenCV robi to funkcja cv2.magnitude:
        magnitude = cv2.magnitude(sobel_x, sobel_y)
        
        # Konwertujemy wynik (float) z powrotem na 8-bit (0-255)
        result_image = cv2.convertScaleAbs(magnitude)

        # --- 7. Obsługa niestandardowej ramki (jeśli wybrano) ---
        if border_mode == "CUSTOM_BORDER":
            # Malujemy ramkę na *końcowym* obrazie
            safe_value = np.clip(border_value, 0, 255).astype(image.dtype)
            result_image[0, :] = safe_value  # Góra
            result_image[-1, :] = safe_value # Dół
            result_image[:, 0] = safe_value  # Lewo
            result_image[:, -1] = safe_value # Prawo

        # --- 8. Wyświetlenie wyniku ---
        if result_image is not None:
            title = new_file_name(Path(img_info["filename"]), "_sobel_operator")
            show_image(result_image, title=title)
            
    except Exception as e:
        messagebox.showerror("Błąd Sobela", f"Nie udało się zastosować operatora Sobela:\n{e}")

# zad 4
def run_median_filter():
    """
    Zadanie 4: Wykonuje filtrację medianową.
    
    Pyta o rozmiar (3x3, 5x5, 7x7, 9x9) i stosuje 1 z 3 trybów brzegów.
    Używa cv2.medianBlur.
    """
    
    # 1. Pobierz aktywny obraz
    img_info, image = get_focused_image_data()
    if image is None:
        return

    # 2. Walidacja (zgodnie z wykładem) [cite: 111, 114]
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Filtr medianowy działa tylko na obrazach monochromatycznych.")
        return

    # 3. Zapytaj o rozmiar otoczenia (interaktywnie)
    ksize = get_integer_input(globals_var.root, "Zadanie 4: Filtr Medianowy", "Podaj rozmiar otoczenia (3, 5, 7 lub 9):", 3)
    
    if ksize is None:
        return # Anulowano
        
    # Walidacja rozmiaru [cite: 102]
    if ksize not in [3, 5, 7, 9]:
         messagebox.showerror("Błąd", "Nieprawidłowy rozmiar. Proszę wybrać 3, 5, 7 lub 9.")
         return

    # 4. Pobierz opcje brzegów (ponowne użycie funkcji z Kroku 4)
    options = get_border_options()
    if options is None:
        return

    # 5. Przygotuj parametry
    result_image = None
    border_mode = options["mode"]
    border_value = options.get("value", 0)
    
    # Oblicz, ile pikseli ramki potrzebujemy (np. 3x3 -> 1px, 5x5 -> 2px)
    pad_size = ksize // 2
    
    padded_image = None
    h, w = image.shape[:2]

    try:
        # 6. Ręczne dodanie ramki (padding)
        # cv2.medianBlur nie ma parametru borderType,
        # więc sami przygotowujemy obraz z ramką.
        
        if border_mode == "REFLECT":
            # Wypełnienie przez odbicie lustrzane
            padded_image = cv2.copyMakeBorder(image, 
                                              pad_size, pad_size, pad_size, pad_size, 
                                              cv2.BORDER_REFLECT)
                                              
        elif border_mode == "CONSTANT":
            # Wypełnienie stałą wartością 'n'
            padded_image = cv2.copyMakeBorder(image, 
                                              pad_size, pad_size, pad_size, pad_size, 
                                              cv2.BORDER_CONSTANT, 
                                              value=border_value)
                                              
        elif border_mode == "CUSTOM_BORDER":
            # Liczymy jak REFLECT, a ramkę domalujemy na końcu
            padded_image = cv2.copyMakeBorder(image, 
                                              pad_size, pad_size, pad_size, pad_size, 
                                              cv2.BORDER_REFLECT)
        
        # 7. Zastosuj filtr medianowy 
        if padded_image is not None:
            filtered_padded = cv2.medianBlur(padded_image, ksize)
            
            # 8. Wytnij środek (usuń ramkę), aby wrócić do oryginalnego rozmiaru
            result_image = filtered_padded[pad_size : pad_size + h, pad_size : pad_size + w]
        
        # 9. Obsługa niestandardowej ramki (jeśli wybrano)
        if border_mode == "CUSTOM_BORDER" and result_image is not None:
            # Wypełniamy ramkę *wyniku* wartością 'n'
            safe_value = np.clip(border_value, 0, 255).astype(image.dtype)
            
            result_image[0:pad_size, :] = safe_value  # Góra
            result_image[h-pad_size:h, :] = safe_value # Dół
            result_image[:, 0:pad_size] = safe_value  # Lewo
            result_image[:, w-pad_size:w] = safe_value # Prawo
        
        # 10. Wyświetl wynik
        if result_image is not None:
            title = new_file_name(Path(img_info["filename"]), f"_median_{ksize}x{ksize}")
            show_image(result_image, title=title)
            
    except Exception as e:
        # Obsługa błędów, np. brak pamięci lub błąd OpenCV
        messagebox.showerror("Błąd filtru medianowego", f"Nie udało się zastosować filtru:\n{e}")

# zad 5
def run_canny_detector():
    """
    Zadanie 5: Implementacja detekcji krawędzi operatorem Canny'ego.
    
    Wersja zmodyfikowana:
    1. Pyta o próg minimalny (wymagany).
    2. Pyta o próg maksymalny (opcjonalny).
    3. Jeśli użytkownik anuluje drugie okno, próg maksymalny = 3 * minimalny.
    """
    
    # 1. Pobierz aktywny obraz
    img_info, image = get_focused_image_data()
    if image is None:
        return

    # 2. Walidacja (Canny działa tylko na szaro-odcieniowych)
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operator Canny'ego działa tylko na obrazach monochromatycznych (szaro-odcieniowych).")
        return

    # 3. Pobierz dolny próg (Threshold1) - WYMAGANY
    threshold1 = get_integer_input(globals_var.root, "Zadanie 5: Operator Canny'ego (1/2)", "Podaj dolny próg (Threshold 1):", 50)
    
    if threshold1 is None:
        return # Użytkownik kliknął "Anuluj"

    # 4. Pobierz górny próg (Threshold2) - OPCJONALNY
    threshold2 = get_integer_input(globals_var.root, "Zadanie 5: Operator Canny'ego (2/2)", "Podaj górny próg (Threshold 2):\n\n(Kliknij 'Anuluj', aby automatycznie ustawić 3 x próg dolny)")

    # 5. Ustaw wartość Threshold2
    if threshold2 is None:
        # Użytkownik "nie musiał" podawać - kliknął Anuluj.
        # Stosujemy zasadę z wykładu.
        threshold2 = threshold1 * 3
        # Zabezpieczenie
        if threshold2 > 255:
            threshold2 = 255
        
    # 6. Zastosuj lekkie wygładzenie (wymóg Canny'ego)
    blurred_image = cv2.GaussianBlur(image, (3, 3), 0)

    try:
        # 7. Wywołaj procedurę OpenCV z ustalonymi progami
        edges = cv2.Canny(blurred_image, threshold1, threshold2)
        
        # 8. Wyświetl wynik
        title = new_file_name(Path(img_info["filename"]), f"_canny_{threshold1}-{threshold2}")
        show_image(edges, title=title)
        
    except Exception as e:
        messagebox.showerror("Błąd Canny'ego", f"Nie udało się zastosować operatora:\n{e}")