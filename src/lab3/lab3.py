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
        return
    
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
        return

    # --- KROK C: Pobieramy q3 i q4 (Zakres wynikowy) ---
    # Tu histogram nie jest potrzebny, więc używamy prostego simpledialog
    q3 = get_number_input(globals_var.root, "Rozciąganie", "Podaj q3 (Zakres wynikowy od):")
    if q3 is None:
        messagebox.showerror("Błąd", "Należy wybrać wartość q3!")
        return

    q4 = get_number_input(globals_var.root, "Rozciąganie", "Podaj q4 (Zakres wynikowy do):", 255, q3)
    if q4 is None:
        messagebox.showerror("Błąd", "Należy wybrać wartość q4!")
        return

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

    if t1 == None:
        return

    dialog_t2 = Toplevel(globals_var.root)
    t2 = threshold(
        dialog_t2, 
        "Progowanie: Wybierz próg t2", 
        return_value_wrapper, 
        "", 
        show_result=False
    )

    if t2 == None:
        return

    # Tworzymy kopię obrazu, aby nie modyfikować oryginału
    result = cv2.inRange(image, t1, t2)
    
    show_image(result, new_file_name(Path(img_info["filename"]), f"_threshold_preserve_gray_{t1}-{t2}"))

# zad 2 p.2

def otsu():
    """
    Implementacja progowanie z progiem wyznaczonym metodą Otsu
    """

    img_info, image = get_focused_mono_image()
    if image is None:
        return None
    
    # Wywołanie cv2.threshold z flagą THRESH_OTSU
    # Wartość progu (drugi argument) ustawiamy na 0, bo Otsu i tak ją wyliczy sam
    calculated_threshold, binary_image = cv2.threshold(
        image, 
        0, 
        255, 
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    if binary_image is None:
        messagebox.showerror("Błąd", calculated_threshold)
        return
    
    # pokaż obliczony próg do akceptacji
    dialog = Toplevel(globals_var.root)
    user_value = threshold(
        dialog, 
        "Próg otsu czeka do akceptacji...", 
        return_value_wrapper, 
        "", 
        show_result=False,
        initial_value=calculated_threshold
    )

    if user_value is None:
        return

    #jeżeli użytkownik wymyśli coś innego
    if user_value != calculated_threshold:
        _, binary_image = cv2.threshold(image, user_value, 255, cv2.THRESH_BINARY)
        calculated_threshold = user_value

    # 4. Wyświetl wynik
    show_image(binary_image, new_file_name(Path(img_info["filename"]), f"_Otsu_{int(calculated_threshold)}"))

# zad 2 p.3
def run_adaptive_threshold():
    """
    Implementacja progowania adaptacyjnego (adaptive threshold). Używa metody gaussowskiej w wersji domyślnej
    """
    img_info, image = get_focused_mono_image()
    if image is None:
        return None

    # 2. Pobierz parametry od użytkownika
    # A. Block Size (Wielkość sąsiedztwa)
    # OpenCV wymaga, aby Block Size był liczbą NIEPARZYSTĄ > 1
    block_size = get_number_input(globals_var.root, 
                                   "Adaptive Threshold", 
                                   "Podaj wielkość bloku (musi być nieparzysta, np. 11):", 
                                   11, 3, 999)
    if block_size is None:
        messagebox.showerror("Błąd", "Należy podać wielkość bloku!")
        return

    # Zabezpieczenie: jeśli użytkownik poda parzystą, dodajemy 1
    if block_size % 2 == 0:
        block_size += 1
        messagebox.showinfo("Info", f"Zmieniono wielkość bloku na nieparzystą: {block_size}")

    # B. Stała C (Odejmowana od średniej)
    # Wykład mówi, że C pozwala "skalować wartości", standardowo np. 2
    c_const = get_number_input(globals_var.root, 
                               "Adaptive Threshold",
                                 "Podaj stałą C (np. 2):",
                                    2, -100, 100)
    if c_const is None:
        messagebox.showerror("Błąd", "Należy podać stałą C!")
        return

    # 3. Wykonanie operacji cv2.adaptiveThreshold
    try:
        result_img = cv2.adaptiveThreshold(
            src=image,
            maxValue=255, # Wartość dla pikseli "białych"
            adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C, # Metoda Gaussa
            thresholdType=cv2.THRESH_BINARY, # Typ binarny
            blockSize=block_size, # Wielkość otoczenia 
            C=c_const # Stała odejmowana 
        )
        
        # 4. Wyświetlenie wyniku
        suffix = f"_adapt_G_B{block_size}_C{c_const}"
        show_image(result_img, new_file_name(Path(img_info["filename"]), suffix))

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd OpenCV: {e}")

# zad 3
def run_morphological_operations():
    """
    operacje morfologii matematycznej
    1. Erozja
    2. Dylacja
    3. Otwarcie
    4. Zamknięcie
    """
    # 1. Pobranie obrazu (morfologia działa na szaro-odcieniowych lub binarnych)
    img_info, image = get_focused_mono_image()
    if image is None: return

    # Tworzymy okno konfiguracji
    dialog = Toplevel(globals_var.root)
    dialog.title("Morfologia Matematyczna")
    dialog.geometry("300x350")

    # === WYBÓR KSZTAŁTU ELEMENTU STRUKTURALNEGO ===
    # Zgodnie z wymogiem: rozróżnienie Krzyża i Prostokąta dla 3x3
    lbl_shape = tk.Label(dialog, text="Kształt elementu (3x3):", font=("Arial", 10, "bold"))
    lbl_shape.pack(pady=(10, 5))

    shape_var = tk.StringVar(value="RECT") # Domyślnie prostokąt

    tk.Radiobutton(dialog, text="Prostokąt (Pełny)", variable=shape_var, value="RECT").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Krzyż (Plus)", variable=shape_var, value="CROSS").pack(anchor="w", padx=20)

    # === WYBÓR OPERACJI ===
    # Wykład wymienia te 4 podstawowe operacje
    lbl_op = tk.Label(dialog, text="Operacja:", font=("Arial", 10, "bold"))
    lbl_op.pack(pady=(15, 5))

    op_var = tk.StringVar(value="ERODE") # Domyślnie Erozja

    tk.Radiobutton(dialog, text="Erozja", variable=op_var, value="ERODE").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Dylacja", variable=op_var, value="DILATE").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Otwarcie", variable=op_var, value="OPEN").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Zamknięcie", variable=op_var, value="CLOSE").pack(anchor="w", padx=20)

    # === FUNKCJA WYKONAWCZA ===
    def apply_morphology():
        try:
            # 1. Ustalenie kształtu (Kernel)
            # cv2.getStructuringElement generuje macierz elementu
            selected_shape = cv2.MORPH_RECT if shape_var.get() == "RECT" else cv2.MORPH_CROSS
            kernel = cv2.getStructuringElement(selected_shape, (3, 3))

            # 2. Ustalenie typu operacji
            op_str = op_var.get()
            if op_str == "ERODE":
                op_type = cv2.MORPH_ERODE
            elif op_str == "DILATE":
                op_type = cv2.MORPH_DILATE
            elif op_str == "OPEN":
                op_type = cv2.MORPH_OPEN
            elif op_str == "CLOSE":
                op_type = cv2.MORPH_CLOSE
            
            # 3. Wykonanie operacji (Używamy morphologyEx jako ogólnej funkcji)
            # funkcja morphologyEx przyjmuje typ operacji i kernel
            # Wykład wspomina też o borderType=BORDER_CONSTANT, co jest domyślne w OpenCV
            result_image = cv2.morphologyEx(image, op_type, kernel)

            # 4. Wyświetlenie wyniku
            shape_name = "Rect" if shape_var.get() == "RECT" else "Cross"
            title_suffix = f"_Morph_{op_str}_{shape_name}3x3"
            
            show_image(result_image, new_file_name(Path(img_info["filename"]), title_suffix))
            
            # zamknij okno po wykonaniu
            dialog.destroy()

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd OpenCV: {e}")

    # Przycisk uruchamiający
    btn_apply = tk.Button(dialog, text="Wykonaj", command=apply_morphology, bg="#dddddd", width=15)
    btn_apply.pack(pady=20)

    tk.Button(dialog, text="Zamknij", command=dialog.destroy).pack()

# zad 4
def run_skeletonization():
    """
    szkieletyzacja obiektu na mapie binarnej
    Implementacja algorytmu szkieletyzacji metodą erozji i dylacji.
    """
    # 1. Pobierz obraz (musi być mono)
    img_info, image = get_focused_image_data()
    if image is None: return

    if is_binary_image(image) == False:
        return

    # 2. Binaryzacja (Wymóg: "szkieletyzacja obiektu na mapie binarnej")
    # Upewniamy się, że mamy tylko 0 i 255
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # 3. Przygotowanie zmiennych
    skeleton = np.zeros(binary.shape, np.uint8) # Pusty obraz na wynik
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)) # Element strukturalny (Krzyż jest dobry do szkieletów)
    
    # Kopia robocza obrazu
    temp_img = binary.copy()

    # 4. Pętla iteracyjna (zgodnie z wykładem)
    while True:
        # Erozja (zdejmowanie warstwy)
        eroded = cv2.erode(temp_img, element)
        
        # Otwarcie (Erozja -> Dylacja) - próba odtworzenia kształtu z erozji
        temp = cv2.dilate(eroded, element)
        
        # Różnica: to, co zniknęło podczas otwarcia, to są "cienkie linie" (szkielet)
        temp = cv2.subtract(temp_img, temp)
        
        # Dodanie znalezionych fragmentów do głównego szkieletu
        skeleton = cv2.bitwise_or(skeleton, temp)
        
        # Przygotowanie do następnego kroku
        temp_img = eroded.copy()

        # Warunek stopu: jeśli po erozji nie zostało nic (same zera), kończymy
        if cv2.countNonZero(temp_img) == 0:
            break

    # 5. Wyświetlenie wyniku
    show_image(skeleton, new_file_name(Path(img_info["filename"]), "_Skeleton"))