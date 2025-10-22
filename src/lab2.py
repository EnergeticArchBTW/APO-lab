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

def get_integer_input(root, title="Podaj liczbę", inside="Wprowadź wartość:", init=0, min=0, max=255):
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
        inside,  # Tekst wewnątrz okna (prompt)
        parent=root,  # Okno nadrzędne (dzięki temu jest modalne)
        initialvalue=init, minvalue=min, maxvalue=max
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

def convert_grayscale_to_binary_mask():
    """
    Pobiera sfocusowany obraz (8-bit w skali szarości) i konwertuje go
    na maskę binarną (0/255) na podstawie progu podanego przez użytkownika.
    zakłądam że threshold zawsze jest 128.
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

def and_or_xor_check(images):
    """funkcja zawierająca powtarzające sprawdzenia dla and, or, xor"""
    if len(images) !=2:
        messagebox.showerror("Błąd", "Musisz wybrać dokładnie 2 obrazy")
        return False

    for image in images:
        if len(image.shape) == 3:
            messagebox.showerror("Błąd", "Operacja działa tylko na obrazach monochromatycznych lub binarnych.")
            return False
    
    if compare_images(images[0], images[1]) == False:
        return False
    return True

def and_logic():
    """operacja AND jednopunktowa dwuargumentowa wyświetla przetworzony obraz"""
    images = select_images_window()
    
    if and_or_xor_check(images) == False:
        return
    
    # Ta funkcja realizuje logikę ze slajdu (1 AND 1=1, 1 AND 0=0, itd.)
    # dla każdego bitu w odpowiadających sobie pikselach.
    result_image = cv2.bitwise_and(images[0], images[1])

    show_image(result_image, f"and_logic[{globals_var.current_id}]")

def or_logic():
    """operacja OR jednopunktowa dwuargumentowa wyświetla przetworzony obraz"""
    images = select_images_window()

    if and_or_xor_check(images) == False:
        return
    
    # Ta funkcja realizuje logikę ze slajdu
    # dla każdego bitu w odpowiadających sobie pikselach.
    result_image = cv2.bitwise_or(images[0], images[1])
    
    show_image(result_image, f"or_logic[{globals_var.current_id}]")

def xor_logic():
    """operacja XOR jednopunktowa dwuargumentowa wyświetla przetworzony obraz"""
    images = select_images_window()

    if and_or_xor_check(images) == False:
        return
    
    # Ta funkcja realizuje logikę ze slajdu
    # dla każdego bitu w odpowiadających sobie pikselach.
    result_image = cv2.bitwise_xor(images[0], images[1])
    
    show_image(result_image, f"xor_logic[{globals_var.current_id}]")

# Zad 3

def apply_opencv_filter(image, kernel, border_type, border_value=0):
    """
    Uniwersalna funkcja do filtrowania obrazu.
    
    Obsługuje BORDER_REFLECT bezpośrednio przez filter2D.
    Obsługuje BORDER_CONSTANT (z wartością 'n') przez ręczne dodanie
    ramki (copyMakeBorder), filtrowanie i przycięcie wyniku.

    Args:
        image (np.array): Obraz wejściowy.
        kernel (np.array): Maska (kernel) splotu (np. z globals_var).
        border_type (int): Typ ramki z OpenCV (np. cv2.BORDER_CONSTANT).
        border_value (int): Wartość do użycia, jeśli border_type to BORDER_CONSTANT[cite: 87, 96].
    
    Returns:
        np.array: Obraz po filtracji lub None w przypadku błędu.
    """
    
    try:
        result_image = None
        
        if border_type == cv2.BORDER_CONSTANT:
            # PRZYPADEK 1: Użytkownik chce stałą wartość 'n'
            # cv2.filter2D nie przyjmuje borderValue, musimy to zrobić ręcznie.
            
            # Zakładamy maskę 3x3, więc potrzebujemy 1px ramki
            pad_size = 1 
            
            # 1. Stwórz ręcznie obraz z ramką o wartości 'border_value'
            padded_image = cv2.copyMakeBorder(
                image, 
                pad_size, pad_size, pad_size, pad_size, 
                cv2.BORDER_CONSTANT, 
                value=border_value  # <-- cv2.copyMakeBorder AKCEPTUJE tę wartość
            )
            
            # 2. Filtruj obraz z ramką. Użyj BORDER_ISOLATED,
            #    aby filtr nie próbował "patrzeć" poza ramkę, którą już dodaliśmy.
            filtered_padded = cv2.filter2D(
                src=padded_image, 
                ddepth=-1, 
                kernel=kernel,
                borderType=cv2.BORDER_ISOLATED 
            )
            
            # 3. Wytnij środek (usuń ramkę), aby wrócić do oryginalnego rozmiaru
            h, w = image.shape[:2]
            result_image = filtered_padded[pad_size : pad_size + h, pad_size : pad_size + w]

        else:
            # PRZYPADEK 2: Inne typy brzegów (np. BORDER_REFLECT)
            # Wywołujemy funkcję w prosty sposób, BEZ 'borderValue'
            result_image = cv2.filter2D(
                src=image, 
                ddepth=-1, 
                kernel=kernel, 
                borderType=border_type
            )
            
        return result_image
        
    except cv2.error as e:
        messagebox.showerror("Błąd OpenCV", f"Błąd podczas operacji filtrowania:\n{e}")
        return None

def apply_custom_border_filter(image, kernel, value_n):
    """
    Stosuje filtr (konwolucję) i nadpisuje 1-pikselową ramkę wartością stałą 'value_n' 
    *po* zakończeniu obliczeń.
    
    Jest to implementacja niestandardowej obsługi brzegu: 
    "wypełnienie wyniku wybraną wartością stałą n".
    
    Używa apply_opencv_filter do obliczenia wnętrza obrazu.

    Args:
        image (np.array): Obraz wejściowy.
        kernel (np.array): Maska (kernel) splotu.
        value_n (int): Wartość stała (0-255) do wypełnienia ramki.

    Returns:
        np.array: Obraz po filtracji z nadpisaną ramką lub None w przypadku błędu.
    """
    
    # 1. Wykonujemy konwolucję używając funkcji z Kroku 2.
    #    Wybieramy cv2.BORDER_REFLECT jako domyślny sposób obliczenia
    #    pikseli brzegowych, zanim je nadpiszemy.
    #    To najlepsze podejście, aby uniknąć artefaktów.
    
    # --- UŻYCIE IMPLEMENTACJI POPRZEDNIEJ FUNKCJI ---
    filtered_image = apply_opencv_filter(image, kernel, cv2.BORDER_REFLECT)
    
    if filtered_image is None:
        # Błąd został już zgłoszony w apply_opencv_filter
        return None

    # 2. Ręcznie nadpisujemy ramkę 1px wartością 'value_n'
    #    Wykład precyzował, że ta operacja ma nastąpić na obrazie wynikowym.
    
    # Tworzymy kopię, aby nie modyfikować oryginalnych danych w locie
    result_image = filtered_image.copy()
    
    # Zabezpieczamy wartość, aby pasowała do typu obrazu (np. uint8)
    safe_value = np.clip(value_n, 0, 255).astype(image.dtype)

    try:
        # Górna ramka
        result_image[0, :] = safe_value
        # Dolna ramka
        result_image[-1, :] = safe_value
        # Lewa ramka
        result_image[:, 0] = safe_value
        # Prawa ramka
        result_image[:, -1] = safe_value
        
        return result_image

    except Exception as e:
        messagebox.showerror("Błąd ramki", f"Nie udało się nadpisać ramki obrazu:\n{e}")
        return None
    
def get_border_options():
    """
    Wyświetla modalne okno dialogowe do wyboru trybu uzupełniania brzegów.
    
    Pyta użytkownika o 3 opcje, a jeśli to konieczne, pyta również 
    o wartość stałej 'n'.
    
    [cite_start]Zgodnie z wykładem[cite: 86, 87, 94]:
    1. BORDER_REFLECT
    2. BORDER_CONSTANT (OpenCV)
    3. Wypełnienie ramki wyniku stałą (Niestandardowe)

    Returns:
        dict: Słownik z wyborem, np. {"mode": "REFLECT", "value": 0}
              lub {"mode": "CONSTANT", "value": 128},
              lub None, jeśli użytkownik anulował.
    """
    
    # Używamy prostego Toplevel, jak wspomniano w poleceniu (przez globals_var.root)
    dialog = Toplevel(globals_var.root)
    dialog.title("Wybierz Opcje Brzegów")
    
    # --- Zmienne do przechowywania wyników ---
    # Używamy słownika, aby łatwo go zwrócić
    result = {"mode": None, "value": 0}
    
    # Zmienna Tkinter do śledzenia wyboru radio
    choice_var = tk.StringVar(value="REFLECT")

    # --- GUI ---
    frame = ttk.Frame(dialog, padding="10")
    frame.pack()
    
    ttk.Label(frame, text="Wybierz sposób uzupełnienia marginesów:").pack(anchor='w', pady=5)

    # [cite_start]Opcje zgodne z zadaniem i wykładem [cite: 86, 87, 94, 95]
    ttk.Radiobutton(frame, text="Odbicie lustrzane (BORDER_REFLECT)", 
                    variable=choice_var, value="REFLECT").pack(anchor='w')
                    
    ttk.Radiobutton(frame, text="Stała wartość OpenCV (BORDER_CONSTANT)", 
                    variable=choice_var, value="CONSTANT").pack(anchor='w')
                    
    ttk.Radiobutton(frame, text="Wypełnij ramkę wyniku stałą 'n' (Niestandardowe)", 
                    variable=choice_var, value="CUSTOM_BORDER").pack(anchor='w')

    # --- Przyciski OK / Anuluj ---
    def on_ok():
        mode = choice_var.get()
        value_n = 0
        
        # [cite_start]Zapytaj o wartość 'n' TYLKO, gdy jest potrzebna [cite: 86]
        if mode in ["CONSTANT", "CUSTOM_BORDER"]:
            # Ważne: ten dialog jest "dzieckiem" okna 'dialog'
            get_integer_input(dialog, "Wartość stałej 'n'", "Podaj wartość stałą 'n' (0-255):")
            
            if value_n is None:
                # Użytkownik anulował wpisywanie liczby - traktujemy to jak "Anuluj"
                result["mode"] = None # Sygnalizuje anulowanie
                dialog.destroy()
                return

        # Zapisz poprawne wyniki
        result["mode"] = mode
        result["value"] = value_n
        dialog.destroy()

    def on_cancel():
        result["mode"] = None # Sygnalizuje anulowanie
        dialog.destroy()

    # Ramka na przyciski
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=(15, 5), fill='x')
    
    ttk.Button(button_frame, text="OK", command=on_ok).pack(side='right', padx=5)
    ttk.Button(button_frame, text="Anuluj", command=on_cancel).pack(side='right')
    
    dialog.protocol("WM_DELETE_WINDOW", on_cancel) # Obsługa 'X'

    # --- Logika modalna (blokująca) ---
    dialog.transient(globals_var.root) # Trzymaj na wierzchu
    dialog.grab_set()                  # Zablokuj inne okna
    globals_var.root.wait_window(dialog) # Czekaj, aż okno 'dialog' zostanie zniszczone

    # Zwróć wynik (albo słownik, albo None)
    return result if result["mode"] is not None else None

def run_generic_filter(kernel, filter_name_suffix):
    """
    Funkcja-Wrapper: Pobiera aktywny obraz, pyta o opcje brzegów,
    stosuje wybrany filtr (kernel) i wyświetla wynik.
    
    Obsługuje filtry wygładzające, wyostrzające i kierunkowe Prewitta,
    które używają ogólnej funkcji filter2D.

    Params:
        kernel: zmienna kernela z globals_var
        filter_name_suffix: nazwa tego filtru
    """
    
    # 1. Pobierz aktywny obraz (użycie twojej funkcji)
    img_info, image = get_focused_image_data()
    if image is None:
        return # Błąd został już wyświetlony

    # [cite_start]2. Walidacja (zgodnie z wykładem [cite: 5, 16])
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacje sąsiedztwa działają tylko na obrazach monochromatycznych (jednokanałowych).")
        return

    # 3. Pobierz opcje brzegów od użytkownika (Krok 4)
    options = get_border_options()
    if options is None:
        print("Operacja filtrowania anulowana przez użytkownika.")
        return # Użytkownik kliknął "Anuluj"

    # 4. Wykonaj filtrowanie na podstawie wyboru
    
    result_image = None
    border_mode = options["mode"]
    border_value = options.get("value", 0) # Bezpieczne pobranie wartości

    if border_mode == "REFLECT":
        # Użyj funkcji z Kroku 2
        result_image = apply_opencv_filter(image, kernel, cv2.BORDER_REFLECT)
        
    elif border_mode == "CONSTANT":
        # Użyj funkcji z Kroku 2
        result_image = apply_opencv_filter(image, kernel, cv2.BORDER_CONSTANT, border_value)
        
    elif border_mode == "CUSTOM_BORDER":
        # Użyj funkcji z Kroku 3
        result_image = apply_custom_border_filter(image, kernel, border_value)

    # 5. Wyświetl wynik
    if result_image is not None:
        # Wygeneruj nową nazwę
        title = new_file_name(Path(img_info["filename"]), f"_{filter_name_suffix}[{globals_var.current_id}]")
        
        # Użyj twojej funkcji
        show_image(result_image, title=title)

# Te funkcje są "końcówkami" podłączanymi bezpośrednio do menu GUI.

# 1. Wygładzanie liniowe

def menu_smooth_avg():
    """Wywołuje filtr uśredniający (wszystkie wagi 1/9)."""
    print("Wybrano: Wygładzanie uśredniające")
    run_generic_filter(globals_var.KERNEL_AVG, "smooth_avg")

def menu_smooth_weighted():
    """
    Wywołuje filtr uśredniający ważony.
    Zgodnie z wykładem jest to filtr "krzyż".
    """
    print("Wybrano: Wygładzanie ważone (krzyż)")
    run_generic_filter(globals_var.KERNEL_WEIGHTED_AVG, "smooth_weighted")

# 2. Wyostrzanie liniowe (Laplasjany)

def menu_sharpen_lap1():
    """Wywołuje pierwszą maskę laplasjanową."""
    print("Wybrano: Wyostrzanie - Laplasjan 1")
    run_generic_filter(globals_var.KERNEL_LAPLACIAN_1, "sharpen_lap1")

def menu_sharpen_lap2():
    """Wywołuje drugą maskę laplasjanową."""
    print("Wybrano: Wyostrzanie - Laplasjan 2")
    run_generic_filter(globals_var.KERNEL_LAPLACIAN_2, "sharpen_lap2")

def menu_sharpen_lap3():
    """Wywołuje trzecią maskę laplasjanową."""
    print("Wybrano: Wyostrzanie - Laplasjan 3")
    run_generic_filter(globals_var.KERNEL_LAPLACIAN_3, "sharpen_lap3")

# 3. Kierunkowa detekcja krawędzi (Prewitt)

def menu_prewitt_e():
    """Detekcja krawędzi Prewitta - kierunek Wschód (E)."""
    print("Wybrano: Prewitt Kierunek E")
    run_generic_filter(globals_var.KERNEL_PREWITT_E, "prewitt_E")

def menu_prewitt_ne():
    """Detekcja krawędzi Prewitta - kierunek Północny-Wschód (NE)."""
    print("Wybrano: Prewitt Kierunek NE")
    run_generic_filter(globals_var.KERNEL_PREWITT_NE, "prewitt_NE")

def menu_prewitt_n():
    """Detekcja krawędzi Prewitta - kierunek Północ (N)."""
    print("Wybrano: Prewitt Kierunek N")
    run_generic_filter(globals_var.KERNEL_PREWITT_N, "prewitt_N")

def menu_prewitt_nw():
    """Detekcja krawędzi Prewitta - kierunek Północny-Zachód (NW)."""
    print("Wybrano: Prewitt Kierunek NW")
    run_generic_filter(globals_var.KERNEL_PREWITT_NW, "prewitt_NW")

def menu_prewitt_w():
    """Detekcja krawędzi Prewitta - kierunek Zachód (W)."""
    print("Wybrano: Prewitt Kierunek W")
    run_generic_filter(globals_var.KERNEL_PREWITT_W, "prewitt_W")

def menu_prewitt_sw():
    """Detekcja krawędzi Prewitta - kierunek Południowy-Zachód (SW)."""
    print("Wybrano: Prewitt Kierunek SW")
    run_generic_filter(globals_var.KERNEL_PREWITT_SW, "prewitt_SW")

def menu_prewitt_s():
    """Detekcja krawędzi Prewitta - kierunek Południe (S)."""
    print("Wybrano: Prewitt Kierunek S")
    run_generic_filter(globals_var.KERNEL_PREWITT_S, "prewitt_S")

def menu_prewitt_se():
    """Detekcja krawędzi Prewitta - kierunek Południowy-Wschód (SE)."""
    print("Wybrano: Prewitt Kierunek SE")
    run_generic_filter(globals_var.KERNEL_PREWITT_SE, "prewitt_SE")

def show_filter_selection_window():
    """
    Wyświetla proste okno do wyboru filtra
    z podglądem maski 3x3.
    Używa FILTER_MAP z globals_var.
    """
    
    # 1. Stwórz okno
    win = Toplevel(globals_var.root)
    win.title("Wybór Filtra 3x3 (Konwolucja)")
    
    frame = ttk.Frame(win, padding="15")
    frame.pack()

    # 2. Lista rozwijana (Combobox)
    ttk.Label(frame, text="Wybierz filtr do uruchomienia:").pack(anchor='w')
    
    combo = ttk.Combobox(frame, width=35, state="readonly")
    # Pobierz nazwy z naszego słownika
    filter_names = list(globals_var.FILTER_MAP.keys())
    combo['values'] = filter_names
    combo.current(0) # Ustaw domyślną wartość
    combo.pack(fill='x', pady=(0, 10))

    # 3. Pole tekstowe do podglądu maski
    ttk.Label(frame, text="Podgląd maski (kernela) 3x3:").pack(anchor='w')
    
    # Używamy czcionki o stałej szerokości dla ładnego formatowania macierzy
    kernel_display = tk.Text(frame, height=5, width=35, font=("Courier New", 10))
    kernel_display.pack(pady=(0, 10))

    # 4. Funkcja aktualizująca podgląd maski
    def on_filter_select(event=None):
        """Wywoływana przy zmianie w Combobox."""
        selected_name = combo.get()
        # Znajdź kernel w słowniku
        kernel_data = globals_var.FILTER_MAP[selected_name]["kernel"]
        
        # Sformatuj kernel (zaokrąglamy dla czytelności filtrów uśredniających)
        kernel_str = str(np.round(kernel_data, 3))
        
        # Wstaw tekst do pola (najpierw włącz, potem wyłącz edycję)
        kernel_display.config(state='normal')
        kernel_display.delete('1.0', tk.END)  # Wyczyść pole
        kernel_display.insert(tk.END, kernel_str) # Wstaw nowy tekst
        kernel_display.config(state='disabled') # Zablokuj edycję przez użytkownika

    # 5. Funkcja uruchamiająca
    def on_run_filter():
        """Wywoływana przez przycisk 'Uruchom'."""
        selected_name = combo.get()
        # Znajdź funkcję (z Kroku 6) w słowniku
        function_to_run = globals_var.FILTER_MAP[selected_name]["func"]
        
        win.destroy() # Zamknij to okno
        
        # Uruchom wybraną funkcję z Kroku 6
        function_to_run() 

    # 6. Podpięcie zdarzeń i przycisk
    
    # Podepnij funkcję 'on_filter_select' pod zdarzenie zmiany w Combobox
    combo.bind("<<ComboboxSelected>>", on_filter_select)
    
    # Uruchom funkcję raz na starcie, aby pokazać domyślną maskę
    on_filter_select() 

    # Przycisk "Uruchom"
    run_button = ttk.Button(frame, text="Uruchom wybrany filtr", command=on_run_filter)
    run_button.pack(fill='x')

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
        print("Operacja Gaussa anulowana przez użytkownika.")
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
        print("Operacja Sobela anulowana przez użytkownika.")
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
        print("Operacja medianowa anulowana.")
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
            title = new_file_name(Path(img_info["filename"]), f"_median_{ksize}x{ksize}[{globals_var.current_id}]")
            show_image(result_image, title=title)
            
    except Exception as e:
        # Obsługa błędów, np. brak pamięci lub błąd OpenCV
        messagebox.showerror("Błąd filtru medianowego", f"Nie udało się zastosować filtru:\n{e}")