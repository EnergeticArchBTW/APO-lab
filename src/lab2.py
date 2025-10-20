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

"""funkcje zrobione na labach 2"""

def compare_images(image1, image2):
    """funkcja porównująca 2 obrazy, czy się nadają do operacji logicznych
    Returns:
        True, jeśli się nadają, False w przeciwnym wypadku"""
    # czy są obrazami jednokanałowymi?
    if len(image1.shape) != 2 or len(image2.shape) != 2:
        messagebox.showerror("Błąd", "Obrazy muszą być jednokanałowe (czarno-białe)!")
        return False
    # czy mają ten sam rozmiar?
    if image1.shape != image2.shape:
        messagebox.showerror("Błąd", "Obrazy muszą mieć ten sam rozmiar!")
        return False
    return True

def select_images_window():
    """
    Otwiera podrzędne okno Tkinter z listą Checkbuttonów bazujących na
    nazwach plików w global_vars.opened_images. Po wybraniu i kliknięciu
    'Wybierz', zwraca listę obiektów zdjęć ("image") dla zaznaczonych elementów.

    :return: Lista obiektów obrazów ("image") z zaznaczonych elementów.
             Zwraca None, jeśli nie ma obrazów do wyboru lub okno jest zamknięte.
    """

    # 1. Sprawdzenie, czy są jakiekolwiek obrazy do wyboru
    if not globals_var.opened_images:
        messagebox.showinfo("Brak obrazów", "Brak otwartych obrazów do wyboru.")
        return []

    # 2. Przygotowanie danych do wyświetlenia
    image_data = []
    
    for key, data in globals_var.opened_images.items():
        image_obj = data.get("image")
        data_id = data.get("id")
                
        image_data.append((key, data.get("filename", "Brak Nazwy"), image_obj, data_id))

    if not image_data:
        messagebox.showinfo("Brak danych", "Brak danych obrazów do przetworzenia.")
        selection_window.destroy() # Zamknij okno, jeśli zostało otwarte
        return []

    # 3. Utworzenie okna podrzędnego (Toplevel)
    # 'main_app_root' to główne okno Twojej aplikacji, przekazane jako argument
    selection_window = tk.Toplevel(globals_var.root)
    selection_window.title("Wybierz Obrazy")
    selection_window.geometry("450x300")
   
    # Powiązanie okna z rodzicem (dobre praktyki)
    selection_window.transient(globals_var.root) 
   
    # Zabezpieczenie przed wielokrotnym otwieraniem (opcjonalne, ale zalecane)
    selection_window.grab_set()

    # Słownik do przechowywania zmiennych Checkbuttonów (StringVar lub IntVar)
    # Klucz: klucz słownika z opened_images (np. 'okno_1'), Wartość: IntVar
    check_vars = {}
    
    # Lista na finalnie wybrane obiekty zdjęć
    selected_images = []

    def on_select_button_click():
        """Obsługuje kliknięcie przycisku 'Wybierz'."""
        nonlocal selected_images
        selected_images.clear()

        for checked_id, var in check_vars.items():
        
            if var.get() == 1:  # Jeśli Checkbutton jest zaznaczony
            
                found_image = None
            
                for okno_key, data_dict in globals_var.opened_images.items():
                    if data_dict.get("id") == checked_id:
                        found_image = data_dict.get("image")
                        break 
                
                # Musimy użyć 'is not None', aby poprawnie obsługiwać
                # tablice NumPy
                
                if found_image is not None: 
                    selected_images.append(found_image)
        
        # Zamykamy okno i zwalniamy focus
        selection_window.grab_release()
        selection_window.destroy()

    # 4. Sekcja wyświetlania (Canvas + Frame dla przewijania)
    canvas = tk.Canvas(selection_window)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(selection_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

    # Frame, w którym będą umieszczone Checkbuttony
    check_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=check_frame, anchor="nw")

    # 5. Generowanie Checkbuttonów
    for key, filename, image_obj, id in image_data:
        # Używamy IntVara, żeby sprawdzić, czy Checkbutton jest zaznaczony (0 lub 1)
        var = tk.IntVar(value=0) 
        check_vars[id] = var

        # Checkbutton wyświetla nazwę pliku, a jego stan jest powiązany z var
        cb = tk.Checkbutton(check_frame, text=filename, variable=var, 
                            anchor="w", justify="left")
        cb.pack(fill="x", padx=10, pady=2)

    # 6. Dodanie przycisku "Wybierz"
    select_button = tk.Button(selection_window, text="Wybierz", command=on_select_button_click)
    select_button.pack(side="bottom", fill="x", pady=10)

    # Uruchomienie pętli zdarzeń okna podrzędnego, czekając na jego zamknięcie
    # Musimy użyć wait_window, żeby funkcja mogła zwrócić wynik po zamknięciu okna.
    def on_cancel():
        """Obsługuje zamknięcie okna przyciskiem 'X'."""
        selection_window.grab_release()
        selection_window.destroy()
        # Funkcja główna 'select_images_window' po prostu zwróci pustą listę

    selection_window.protocol("WM_DELETE_WINDOW", on_cancel)
    selection_window.wait_window(selection_window)
    
    # 7. Zwrócenie wyniku po zamknięciu okna
    return selected_images


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
    
    show_image(result, f"without_sat[{globals_var.current_id}]")
    globals_var.current_id += 1

def add_images_with_saturation():
    """funkcja dodająca od 2 do 5 obrazów Z WYSYCENIEM (saturacją, czyli obcinaniem) z GUI
    wyświetla wynikowy obraz lub nic nie robi w przypadku błędu
    """

    images = select_images_window()
    print(images)

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
    
    show_image(result, f"with_sat[{globals_var.current_id}]")

def operation_on_scalar(image, operation, value, saturation=True):
    """
    Wykonuje operacje arytmetyczne (dodawanie, mnożenie, dzielenie)
    na obrazie (tablica NumPy) i liczbie całkowitej.

    Params:
        image: Źródłowy obraz (tablica NumPy, np. uint8).
        operation: Rodzaj operacji jako string: 'add', 'multiply', 'divide'.
        value: Liczba całkowita, przez którą ma być wykonana operacja.
        saturation: Boolean.
                       True = tryb Z WYSYCENIEM (wyniki obcinane do 0-255).
                       False = tryb BEZ WYSYCENIA (wyniki zawijane, modulo 256).
    Returns:
        Nowy obraz (tablica NumPy) po operacji lub None w przypadku błędu.
    """
    
    # --- Walidacja danych wejściowych ---
    if image is None:
        messagebox.showerror("Błąd operacji", "Obraz wejściowy ma wartość None.")
        return None
        
    operation = operation.lower().strip()
    
    try:
        # Upewnij się, że 'value' jest liczbą
        value = float(value) 
    except ValueError:
        messagebox.showerror("Błąd wartości", f"Wartość '{value}' nie jest poprawną liczbą.")
        return None

    if operation == 'divide' and value == 0:
        messagebox.showerror("Błąd operacji", "Dzielenie przez zero jest niedozwolone.")
        return None

    # --- Logika operacji ---
    
    if saturation:
        # ==================================
        # === TRYB Z WYSYCENIEM (obcinanie) ===
        # ==================================
        
        # Używamy tymczasowo float64, aby uniknąć błędów przepełnienia
        # przed ostatecznym obcięciem.
        temp_image = image.astype(np.float64)

        if operation == 'add':
            result_float = temp_image + value
        elif operation == 'multiply':
            result_float = temp_image * value
        elif operation == 'divide':
            result_float = temp_image / value
        else:
            messagebox.showerror("Błąd operacji", f"Nieznana operacja: '{operation}'.")
            return None
        
        # Obcinamy wynik do bezpiecznego zakresu 0-255
        # Zaokrąglamy przed rzutowaniem na liczbę całkowitą
        result_clipped = np.clip(np.round(result_float), 0, 255)
        
        # Konwertujemy z powrotem do uint8
        result = result_clipped.astype(np.uint8)

    else:
        # =====================================
        # === TRYB BEZ WYSYCENIA (zawijanie) ===
        # =====================================
        
        # Celowo rzutujemy na uint8 na końcu, aby wymusić arytmetykę modulo 256
        
        if operation == 'add':
            # Używamy int32, aby (200 + 100) dało 300, 
            # a dopiero potem rzutowanie (300 % 256 = 44)
            result = (image.astype(np.int32) + int(value)).astype(np.uint8)
            
        elif operation == 'multiply':
            # Używamy int32, aby (200 * 2) dało 400,
            # a dopiero potem rzutowanie (400 % 256 = 144)
            result = (image.astype(np.int32) * int(value)).astype(np.uint8)
            
        elif operation == 'divide':
            # Dzielenie z natury nie "zawija się" w ten sam sposób.
            # Najbliższą analogią jest wykonanie dzielenia na floatach
            # i rzutowanie wyniku na uint8, co zawinie wartości > 255
            # (np. dzielenie przez 0.5 da mnożenie * 2)
            result_float = image.astype(np.float64) / value
            result = np.round(result_float).astype(np.uint8)
            
        else:
            messagebox.showerror("Błąd operacji", f"Nieznana operacja: '{operation}'.")
            return None

    return result

def get_integer_input(root, title="Podaj liczbę"):
    """
    Wyświetla proste, modalne okno dialogowe proszące o liczbę całkowitą.
    Funkcja czeka na odpowiedź użytkownika.
    
    Params:
        root: Główne okno aplikacji (tk.Tk() lub Toplevel).
        title: Tytuł okienka.
    Returns:
        return: Wprowadzona liczba (int) lub None, jeśli użytkownik anulował.
    """
    
    value = simpledialog.askinteger(
        title,  # Tytuł okna
        "Wprowadź wartość:",  # Tekst wewnątrz okna (prompt)
        parent=root  # Okno nadrzędne (dzięki temu jest modalne)
    )
    
    return value

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
        show_image(result, f"add_num_with_sat[{globals_var.current_id}]")

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
        show_image(result, f"add_num_without_sat[{globals_var.current_id}]")

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
        show_image(result, f"divide_num_with_sat[{globals_var.current_id}]")

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
        show_image(result, f"divide_num_without_sat[{globals_var.current_id}]")

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
        show_image(result, f"multiply_num_with_sat[{globals_var.current_id}]")

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
        show_image(result, f"multiply_num_without_sat[{globals_var.current_id}]")

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
    show_image(result, f"abs_diff[{globals_var.current_id}]")