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

"""funkcje do labów 2, które wewnętrznie coś robią i nie są bezpośrednio wywoływane"""

# zad 1
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

# zad 2
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

# zad 3
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

    # 2. Walidacja (zgodnie z wykładem)
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacje sąsiedztwa działają tylko na obrazach monochromatycznych (jednokanałowych).")
        return

    # 3. Pobierz opcje brzegów od użytkownika (Krok 4)
    options = get_border_options()
    if options is None:
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
        title = new_file_name(Path(img_info["filename"]), f"_{filter_name_suffix}")
        
        # Użyj twojej funkcji
        show_image(result_image, title=title)

# Te funkcje są "końcówkami" podłączanymi bezpośrednio do menu GUI.

# 1. Wygładzanie liniowe

def menu_smooth_avg():
    """Wywołuje filtr uśredniający (wszystkie wagi 1/9)."""
    run_generic_filter(globals_var.KERNEL_AVG, "smooth_avg")

def menu_smooth_weighted():
    """
    Wywołuje filtr uśredniający ważony.
    Zgodnie z wykładem jest to filtr "krzyż".
    """
    run_generic_filter(globals_var.KERNEL_WEIGHTED_AVG, "smooth_weighted")

# 2. Wyostrzanie liniowe (Laplasjany)

def menu_sharpen_lap1():
    """Wywołuje pierwszą maskę laplasjanową."""
    run_generic_filter(globals_var.KERNEL_LAPLACIAN_1, "sharpen_lap1")

def menu_sharpen_lap2():
    """Wywołuje drugą maskę laplasjanową."""
    run_generic_filter(globals_var.KERNEL_LAPLACIAN_2, "sharpen_lap2")

def menu_sharpen_lap3():
    """Wywołuje trzecią maskę laplasjanową."""
    run_generic_filter(globals_var.KERNEL_LAPLACIAN_3, "sharpen_lap3")

# 3. Kierunkowa detekcja krawędzi (Prewitt)

def menu_prewitt_e():
    """Detekcja krawędzi Prewitta - kierunek Wschód (E)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_E, "prewitt_E")

def menu_prewitt_ne():
    """Detekcja krawędzi Prewitta - kierunek Północny-Wschód (NE)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_NE, "prewitt_NE")

def menu_prewitt_n():
    """Detekcja krawędzi Prewitta - kierunek Północ (N)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_N, "prewitt_N")

def menu_prewitt_nw():
    """Detekcja krawędzi Prewitta - kierunek Północny-Zachód (NW)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_NW, "prewitt_NW")

def menu_prewitt_w():
    """Detekcja krawędzi Prewitta - kierunek Zachód (W)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_W, "prewitt_W")

def menu_prewitt_sw():
    """Detekcja krawędzi Prewitta - kierunek Południowy-Zachód (SW)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_SW, "prewitt_SW")

def menu_prewitt_s():
    """Detekcja krawędzi Prewitta - kierunek Południe (S)."""
    run_generic_filter(globals_var.KERNEL_PREWITT_S, "prewitt_S")

def menu_prewitt_se():
    """Detekcja krawędzi Prewitta - kierunek Południowy-Wschód (SE)."""
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