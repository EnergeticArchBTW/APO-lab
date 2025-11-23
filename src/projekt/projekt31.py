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
from convert import *

"""
Udoskonalenie oprogramowania przygotowanego na zajęciach przez dołożenie operacji zmniejszenia
udziału szumu przez uśredniania kilku obrazów zebranych w takich samych warunkach oraz operacji
logicznych na zaszumionych obrazach binarnych. 
"""

def statistics(title, text):
    """ Pokazuje okno z podanym tytułem i tekstem """
    win = Toplevel(globals_var.root)
    win.title(title)
    
    text_widget = tk.Text(win)
    text_widget.pack(fill='both', expand=True)
    text_widget.insert('1.0', text)
    text_widget.config(state='disabled')  # tylko do odczytu

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
    
    # czy wszystkie obrazy są monochromatyczne?
    for img in images:
        if len(img.shape) != 2:
            messagebox.showerror("Błąd", "Wszystkie obrazy muszą być monochromatyczne!")
            return

    # --- 3. blok obliczeniowy ---
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
        # --------------------

        # --- pokazanie statystyk w osobnym oknie ---
        # średni błąd
        mean_error = np.mean(abs_diff)

        # procent zmienionych pikseli
        # count_nonzero() zlicza piksele, gdzie różnica jest większa od 0
        changed_pixels_count = np.count_nonzero(abs_diff)
        total_pixels = abs_diff.size
        percentage_changed = (changed_pixels_count / total_pixels) * 100

        # procent pikseli z błędem większym niż 5
        THRESHOLD = 5
        pixels_significant = np.count_nonzero(abs_diff > THRESHOLD)
        percent_sig = (pixels_significant / total_pixels) * 100
        # --------------------

        # --- pokazanie statystyk w oknie ---
        statistics(f"Statystyki dla obrazu Average_{ilosc}_images[{globals_var.current_id-2}].jpg",
            f"Średni błąd porównując pierwszy obraz z wynikowym: {mean_error:.2f}\nProcent zmienionych pikseli: {percentage_changed:.4f}%\nProcent pikseli z błędem > {THRESHOLD}: {percent_sig:.4f}%")

    except Exception as e:
        messagebox.showerror("Błąd obliczeń", f"Wystąpił błąd: {e}")

# --- operacje logiczne na zaszumionych obrazach binarnych ---

def logical_filter_remove_noise(binary_img):
    """
    Implementacja operacji logicznych do usuwania szumu 'sól' (pojedyncze białe piksele).
    Działa na zasadzie sprawdzania sąsiadów (góra-dół oraz lewo-prawo).
    """
    # Kopia obrazu roboczego
    cleaned = binary_img.copy()
    
    # --- KROK 1: LOGIKA PIONOWA (Góra-Dół) ---
    # Przesuwamy obraz o 1 piksel w górę i w dół, żeby mieć sąsiadów "pod ręką"
    img_up = np.roll(binary_img, -1, axis=0)   # Sąsiad dolny wchodzi na miejsce bieżącego
    img_down = np.roll(binary_img, 1, axis=0)  # Sąsiad górny wchodzi na miejsce bieżącego
    
    # WARUNEK LOGICZNY:
    # Piksel jest szumem (do usunięcia), jeśli:
    # JEST BIAŁY (255) ORAZ GÓRA JEST CZARNA (0) ORAZ DÓŁ JEST CZARNY (0)
    mask_vertical = (binary_img == 255) & (img_up == 0) & (img_down == 0)
    
    # Czyścimy znalezione piksele (ustawiamy na czarno)
    cleaned[mask_vertical] = 0

    # --- KROK 2: LOGIKA POZIOMA (Lewo-Prawo) ---
    # To samo dla sąsiadów bocznych
    # Operujemy już na obrazie 'cleaned' (wstępnie oczyszczonym w pionie)
    img_left = np.roll(cleaned, 1, axis=1)
    img_right = np.roll(cleaned, -1, axis=1)
    
    mask_horizontal = (cleaned == 255) & (img_left == 0) & (img_right == 0)
    
    cleaned[mask_horizontal] = 0
    
    return cleaned

# --- Funkcja główna do podpięcia pod przycisk ---
def run_logical_operations_project():
    # 1. Wybierz plik (jeden, zaszumiony obraz)
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # sprawdzanie czy monochromatyczny
        if len(img_info["image"].shape) != 2:
            messagebox.showerror("Błąd", "Obraz musi być monochromatyczny!")
            return
        img = img_info["image"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    # 2. Binaryzacja (wymóg projektu - obraz musi być binarny)
    # Treshold 127: wszystko poniżej -> czarne, powyżej -> białe
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    # Wyświetl przed
    show_image(binary, "Binary_Before_Logical_Filter")

    # 4. Uruchom filtr logiczny
    result = logical_filter_remove_noise(binary)

    # 5. Wyświetl po
    show_image(result, "Binary_After_Logical_Filter")
    
    # statystyka ile pikseli usunięto
    diff = cv2.absdiff(binary, result)
    removed_count = np.count_nonzero(diff)
    statistics(f"Statystyki dla obrazu Binary_After_Logical_Filter[{globals_var.current_id-1}].jpg",
            f"Usunięto punktów szumu: {removed_count}")

def convert_to_grayscale_and_show():
    """ Konwertuje aktualnie wyświetlany obraz do skali szarości i pokazuje go w nowym oknie """
    img_info, image = get_focused_image_data()
    if image is None:
        return
    show_image(convert_to_grayscale(image), new_file_name(Path(img_info["filename"]), "_grayscale"))