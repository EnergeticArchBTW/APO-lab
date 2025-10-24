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

"""funkcje zrobione na labach 1"""

# zad 1
def save_image():
    """Zapisuje sfocusowany obraz w wybranej przez użytkownika lokalizacji."""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        image = img_info["image"]
        # Prośba o lokalizację i nazwę pliku
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("Obrazy", "*.bmp;*.tif;*.png;*.jpg;*.jpeg")],
            initialdir=globals_var.OUTPUT_DIR, # <-- domyślny folder
            initialfile=img_info["filename"]
        )
        if file_path:
            # zapisz obraz z polską nazwą
            with open(file_path, "wb") as f:
                # Dobierz format zapisu na podstawie rozszerzenia
                ext = Path(file_path).suffix
                ret, buf = cv2.imencode(ext, image)
                # Zapisz tylko jeśli kodowanie się powiodło
                if ret:
                    buf.tofile(f)
                else:
                    messagebox.showerror("Błąd", "Błąd przy zapisie obrazu.")
                    return
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem do zapisu.")

def open_and_show_image():
    """Prosi użytkownika o wybór pliku i wyświetla obraz w nowym oknie."""
    file_path = filedialog.askopenfilename(
        title="Wybierz obraz",
        initialdir=globals_var.DATA_DIR, # <-- domyślny folder
        filetypes=[("Obrazy", "*.bmp;*.tif;*.png;*.jpg;*.jpeg")]
    )
    if file_path:
        # Wczytaj plik jako bajty, potem zdekoduj przez OpenCV (by polskie nazwy działały)
        file_path_obj = Path(file_path)
        with open(file_path_obj, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            # wczyta obraz taki jaki jest albo monochromatyczny albo kolorowy
            image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
        if image is not None:
            # Dodaj ID do nazwy pliku
            display_name = file_path_obj.name
            # Pokaz obraz
            show_image(image, title=display_name)
        else:
            messagebox.showerror("Błąd", "Nie udało się wczytać obrazu.")

def duplicate_focused_image():
    """Duplikuje aktualnie sfocusowany obraz i wyświetla w nowym oknie."""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        image_copy = img_info["image"].copy()
        # Dodaj _copy do nazwy pliku przed rozszerzeniem
        new_name = new_file_name(Path(img_info["filename"]), "_copy")
        show_image(image_copy, title=new_name)
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem do duplikacji.")

# zad 2
def show_lut():
    """Generuje i wyświetla tablicę LUT dla aktualnie sfocusowanego obrazu."""
    lut = generate_lut()
    if lut is not None: 
        # Tworzymy nowe okno
        okno = tk.Toplevel()
        okno.title(lut["title"])
        frame = tk.Frame(okno)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        #----szybsze przewijanie o 5, 10, 15------
        # Frame na przyciski nawigacji
        nav_frame = tk.Frame(frame)
        nav_frame.pack(side=tk.RIGHT, padx=5, fill=tk.Y)

        # Funkcje do przesuwania
        def scroll_up(rows):
            current = tree.yview()[0]
            tree.yview_moveto(max(0, current - rows/256))

        def scroll_down(rows):
            current = tree.yview()[0]
            tree.yview_moveto(min(1, current + rows/256))

        # Przyciski
        ttk.Button(nav_frame, text="↑ 15", command=lambda: scroll_up(15), width=6).pack(pady=2)
        ttk.Button(nav_frame, text="↑ 10", command=lambda: scroll_up(10), width=6).pack(pady=2)
        ttk.Button(nav_frame, text="↑ 5", command=lambda: scroll_up(5), width=6).pack(pady=2)
        ttk.Label(nav_frame, text="─────").pack(pady=5)
        ttk.Button(nav_frame, text="↓ 5", command=lambda: scroll_down(5), width=6).pack(pady=2)
        ttk.Button(nav_frame, text="↓ 10", command=lambda: scroll_down(10), width=6).pack(pady=2)
        ttk.Button(nav_frame, text="↓ 15", command=lambda: scroll_down(15), width=6).pack(pady=2)
        #----------

        if lut["color"]==False:
            # Scrollbar
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Treeview z dwiema kolumnami
            tree = ttk.Treeview(frame, columns=("Indeks", "Wartość"), show="headings", height=15, yscrollcommand=scrollbar.set)
            tree.heading("Indeks", text="Poziom jasności")
            tree.heading("Wartość", text="Wartość")
            tree.column("Indeks", width=120)
            tree.column("Wartość", width=120)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar.config(command=tree.yview)

            

            # Wypełniamy tabelę
            for i in range(256):
                tree.insert("", tk.END, values=(i, lut["lut"][i]))
        else:
            # Scrollbar
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Treeview z czterema kolumnami
            tree = ttk.Treeview(frame, columns=("Indeks", "R", "G", "B"), show="headings", height=15, yscrollcommand=scrollbar.set)
            tree.heading("Indeks", text="Poziom jasności")
            tree.heading("R", text="Red")
            tree.heading("G", text="Green")
            tree.heading("B", text="Blue")
            tree.column("Indeks", width=100)
            tree.column("R", width=80)
            tree.column("G", width=80)
            tree.column("B", width=80)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar.config(command=tree.yview)

            # Wypełniamy tabelę
            for i in range(256):
                tree.insert("", tk.END, values=(i, lut["lut"][0][i], lut["lut"][1][i], lut["lut"][2][i]))

# zad 3
def cal_mono_hist(mono_lut):
    """ oblicza monochromatyczny histogram (albo jeden kanał kolorowy) i zwraca norm, var_max, mean, std, median_value, total_pixels.
     mono_lut to już jest sama tablica "lut", dla której wiadomo, że ma tylko jedną listę """
    var_max = max(mono_lut) # do niej normowane wysokości słupków

    # normowanie przez podzielenie
    norm = mono_lut

    #running_count to licznik do mediany
    mean = std = median_value = total_pixels = brightness_sum = running_count = 0
    norm = [0] * len(mono_lut)
    # obliczenia tylko gdy nie ma samych zer
    if var_max != 0:
        #zakładam, że 230 pikseli to maksymalna wysokość słupka
        norm = [int((val / var_max) * 230) for val in mono_lut]

        #kumulowanie informacji
        total_pixels = sum(mono_lut)              #ilość pikseli w obrazie
        median_pixel = total_pixels // 2            # połowa — do mediany

        for level, count in enumerate(mono_lut):
            # brightness_sum to suma całkowitej jasności wszystkich pikseli w obrazie (suma jasności * ilość pikseli)
            brightness_sum += level * count

            # Szukanie mediany – kiedy licznik przekroczy połowę wszystkich pikseli
            running_count += count # dodawanie do licznika mediany
            # wynik mediany
            if median_value == 0 and running_count >= median_pixel:
                median_value = level

        # Obliczenie średniej
        mean = brightness_sum / total_pixels if total_pixels > 0 else 0

        # Obliczenie odchylenia standardowego
        variance_sum = sum(((level - mean) ** 2) * count for level, count in enumerate(mono_lut))
        std = (variance_sum / total_pixels) ** 0.5 if total_pixels > 0 else 0
    
    return norm, var_max, mean, std, median_value, total_pixels

def cal_hist(okno):
    """ obliczanie monochromatycznego/kolorowego histogramu i tworzenie pustego okna do rysowania histogramu"""
    main_frame = tk.Frame(okno, bg='white')
    main_frame.pack()
    lut = generate_lut()
    #sprawdzamy czy wogóle jakiś obrazek jest
    if lut is not None:

        #obliczanie grubości słupka (szerokość) / 256
        bar_width = int(round(450 / 256)) #zakładam, że chcę skalować słupki do wys 450 px

        #okno.geometry("450x350") #szerokość 450 wysokość 350
        #dla monochromatycznych
        if lut["color"] == False:

            norm, var_max, mean, std, median_value, total_pixels = cal_mono_hist(lut["lut"])

            #zwrócenie danych potrzebnych dla show_hist()
            data = {"main_frame": main_frame, "norm": norm, "var_max": var_max, "bar_width": bar_width,
                    "mean": mean, "std": std, "median_value": median_value, "total_pixels": total_pixels,
                    "color": "black"}
            show_hist(data)
        
        else:
            #dla kolorowych
            colors = ["red", "green", "blue"]

            for i, color in enumerate(colors):
                norm, var_max, mean, std, median_value, total_pixels = cal_mono_hist(lut["lut"][i])
                data = {
                    "main_frame": main_frame,
                    "norm": norm,
                    "var_max": var_max,
                    "bar_width": bar_width,
                    "mean": mean,
                    "std": std,
                    "median_value": median_value,
                    "total_pixels": total_pixels,
                    "color": color
                }
                show_hist(data)

def show_hist(data):
    """ Rysuje histogram w oknie.
    funkcja przyjmuje main_frame, norm, var_max, bar_width, mean, std, median_value, total_pixels, color (kolor histogramu) """

    # canvas = tk.Canvas(okno, width=570, height=580, bg='white')
    # canvas.pack()

    # Utwórz osobny Canvas dla każdego histogramu
    canvas = tk.Canvas(data["main_frame"], width=570, height=290, bg='white')
    canvas.pack()  # automatycznie układa pod spodem
    # ramka pokazująca obszar histogramu
    canvas.create_rectangle(0, 0, 570, 290, outline='lightgray', width=1)
            
    # rysowanie słupków (przesunięte o 50 w prawo i w górę by zrobić miejsce na opisy)
    for i, height in enumerate(data["norm"]):
        x = 50 + i * data["bar_width"]
        canvas.create_rectangle(x - 19, 305 - height -70, x + data["bar_width"] - 19, 305 - 70, fill=data["color"], outline='')
            
    # tekst z maksymalną wartością (góra po lewej)
    canvas.create_text(35 - 19, 3, text=str(data["var_max"]), anchor='n')
            
    # tekst "0" na dole po lewej
    canvas.create_text(45 - 19, 235, text='0', anchor='s')
            
    # tekst "0" na dole histogramu po lewej stronie
    canvas.create_text(51 - 19, 235, text='0', anchor='n')
            
    # tekst "255" na dole histogramu po prawej stronie
    canvas.create_text(50 - 19 + 255 * data["bar_width"], 235, text='255', anchor='n')

    # średnia jasność
    canvas.create_text(80, 260, text=f"Średnia jasność: {data["mean"]:.2f}", anchor='n')
    # odchylenie standardowe
    canvas.create_text(240, 260, text=f"Odchylenie standardowe: {data["std"]:.2f}", anchor='n')
    # mediana
    canvas.create_text(380, 260, text=f"Mediana: {data["median_value"]}", anchor='n')
    # liczba pikseli
    canvas.create_text(490, 260, text=f"Liczba pikseli: {data["total_pixels"]}", anchor='n')

def cal_and_show_hist():
    """ oblicza i pokazuje cały histogram dla monochromatycznych i kolorowych obrazów
    (najpierw sprawdza, czy jakiś obrazek jest sfocusowany)"""
    #sprawdzamy czy wogóle jakiś obrazek jest
    if globals_var.current_window in globals_var.opened_images:
        okno = tk.Toplevel()
        img_info = globals_var.opened_images[globals_var.current_window]
        filename = img_info["filename"]
        kolor = "Kolorowy" if len(img_info["image"].shape) == 3 and img_info["image"].shape[2] == 3 else "Monochromatyczny"
        okno.title(f"{filename} histogram {kolor}")
        cal_hist(okno)
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")

def cal_without_supersaturation_hist(image, lut):
    """ liniowe rozciągnięcie histogramu bez przesycenia (liczenie dla jednego kanału)"""
    # znajdź pierwszy i ostatni niepusty słupek histogramu
    # min_val to pierwsza niezerowa wartość w lut
    # max_val to ostatnia niezerowa wartość w lut
    min_val = next(i for i, v in enumerate(lut) if v > 0)
    max_val = max(i for i, v in enumerate(lut) if v > 0)

    Lmin = 0
    Lmax = 255

    hr = np.zeros(256, dtype=np.uint8)

    # obsługa przypadku min == max (obraz jednorodny w tym kanale)
    if min_val == max_val:
        hr[min_val] = 255
        return hr[image]
    
    # obliczanie tablicy przekształceń
    for Z in range(256):
        if Z < min_val:
            hr[Z] = Lmin
        elif Z > max_val:
            hr[Z] = Lmax
        else:
            hr[Z] = round(((Z - min_val) * (Lmax - Lmin)) / (max_val - min_val) + Lmin)

    image_stretched = hr[image]
    return image_stretched

def calandshow_without_supersaturation_hist():
    """ liniowe rozciągnięcie histogramu bez przesycenia i pokazanie obrazu"""

    image_stretched = None

    img_info = globals_var.opened_images[globals_var.current_window]
    image = img_info["image"]

    lut = generate_lut()
    if lut is not None:
        lut_values = lut["lut"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem lub nieobsługiwany obraz.")
        return

    image_stretched = apply_per_channel(image, lut, cal_without_supersaturation_hist)

    title = new_file_name(Path(img_info["filename"]), "_without_supersaturation")
    show_image(image_stretched, title=title)

def cal_with_supersaturation5_hist(image, lut):
    """ liniowe rozciągnięcie histogramu z 5% przesyceniem (liczenie dla jednego kanału)"""
    
    # oblicz całkowitą liczbę pikseli
    total_pixels = image.shape[0] * image.shape[1]
    
    # oblicz próg (5% pikseli)
    threshold = int(total_pixels * 0.05)
    
    # znajdź min_val: pomijamy pierwsze 5% pikseli
    cumsum = 0
    min_val = 0
    for i in range(256):
        cumsum += lut[i]
        if cumsum >= threshold:
            min_val = i
            break
    
    # znajdź max_val: pomijamy ostatnie 5% pikseli
    cumsum = 0
    max_val = 255
    for i in range(255, -1, -1):
        cumsum += lut[i]
        if cumsum >= threshold:
            max_val = i
            break
    
    Lmin = 0
    Lmax = 255
    hr = np.zeros(256, dtype=np.uint8)
    
    # obsługa przypadku min == max
    if min_val == max_val:
        hr[min_val] = 255
        return hr[image]
    
    # obliczanie tablicy przekształceń (dokładnie jak w wersji bez przesycenia)
    for Z in range(256):
        if Z < min_val:
            hr[Z] = Lmin
        elif Z > max_val:
            hr[Z] = Lmax
        else:
            hr[Z] = round(((Z - min_val) * (Lmax - Lmin)) / (max_val - min_val) + Lmin)
    
    image_stretched = hr[image]
    return image_stretched


def calandshow_with_supersaturation5_hist():
    """ liniowe rozciągnięcie histogramu z 5% przesyceniem i pokazanie obrazu"""
    image_stretched = None
    img_info = globals_var.opened_images[globals_var.current_window]
    image = img_info["image"]
    lut = generate_lut()
    
    if lut is not None:
        lut_values = lut["lut"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem lub nieobsługiwany obraz.")
        return
    
    image_stretched = apply_per_channel(image, lut, cal_with_supersaturation5_hist)
    
    title = new_file_name(Path(img_info["filename"]), "_with_supersaturation5")
    show_image(image_stretched, title=title)

def calhistogram_equalization(image, lut):
    """ funkcja liczy wyrównanie histogramu dla jednego kanału (monochromatycznego lub jednego kanału kolorowego)
    zwraca obraz po equalizacji"""
    # KROK 2: Tworzenie histogramu skumulowanego
    # Według wzoru rekurencyjnego z wykładu:
    # H_skum[0] = H[0] (zaczepienie)
    # H_skum[i] = H_skum[i-1] + H[i] (algorytm rekurencyjny)
    
    histogram_skumulowany = [0] * 256
    
    # Zaczepienie - pierwsza wartość
    histogram_skumulowany[0] = lut[0]
    
    # Rekurencyjne dodawanie kolejnych wartości
    for i in range(1, 256):
        histogram_skumulowany[i] = histogram_skumulowany[i-1] + lut[i]
    
    # KROK 3: Obliczenie całkowitej liczby pikseli w obrazie
    # (to jest wartość ostatniego elementu histogramu skumulowanego)
    height, width = image.shape[:2]
    total_pixels = height * width  # lub histogram_skumulowany[255]
    
    # KROK 4: Tworzenie tablicy przekodowań (LUT dla equlizacji)
    # Według wzoru z wykładu:
    # nowa_wartość = ((H_skum[i] - H_skum[0]) / (1 - H_skum[0]/total)) * L_max
    # 
    # Po uproszczeniu (dzieląc przez total_pixels):
    # nowa_wartość = ((H_skum[i] - H_skum_min) / (total_pixels - H_skum_min)) * 255
    #
    # gdzie H_skum_min to pierwsza niezerowa wartość w histogramie skumulowanym
    
    # Znajdź pierwszą niezerową wartość w histogramie skumulowanym
    h_skum_min = histogram_skumulowany[0]
    for val in histogram_skumulowany:
        if val > 0:
            h_skum_min = val
            break
    
    # Tablica przekodowań - mapuje starą wartość jasności na nową
    lut_equalization = [0] * 256
    
    # Dla każdego poziomu jasności (0-255) obliczamy nową wartość
    for i in range(256):
        if lut[i] == 0:
            # Jeśli dany poziom jasności nie występuje w obrazie, 
            # mapujemy go proporcjonalnie
            lut_equalization[i] = i
        else:
            # Wzór equalizacji z wykładu:
            # Normalizujemy histogram skumulowany do zakresu 0-255
            # numerator = licznik, denomnator = mianownik
            numerator = histogram_skumulowany[i] - h_skum_min
            denominator = total_pixels - h_skum_min
            
            if denominator > 0:
                # Obliczamy nową wartość i zaokrąglamy do liczby całkowitej
                nowa_wartosc = (numerator / denominator) * 255
                lut_equalization[i] = int(round(nowa_wartosc))
            else:
                lut_equalization[i] = i
    
    # KROK 5: Przekodowanie obrazu zgodnie z tablicą LUT
    # Tworzymy nowy obraz o tych samych wymiarach
    equalized_image = image.copy()
    
    # Przechodzimy przez każdy piksel obrazu
    # Algorytm: przeglądamy obraz wierszami (y), w każdym wierszu kolumnami (x)
    for y in range(height):
        for x in range(width):
            # Pobieramy starą wartość piksela
            old_value = image[y, x]
            
            # Przekodowujemy zgodnie z tablicą LUT
            # nowa wartość = lut_equalization[stara wartość]
            #new_value = lut_equalization[old_value]
            new_value = lut_equalization[int(old_value)]
            
            # Zapisujemy nową wartość w obrazie wynikowym
            equalized_image[y, x] = new_value
    return equalized_image

def histogram_equalization():
    """
    Selektywne wyrównanie histogramu przez equalizację.
    
    Algorytm według wykładu:
    1. Generacja tablicy LUT (histogram) - liczba pikseli o każdej wartości jasności
    2. Tworzenie histogramu skumulowanego (analog dystrybuanty)
    3. Normalizacja przez podzielenie przez sumę wszystkich pikseli
    4. Przekształcenie wartości według wzoru equlizacji
    5. Utworzenie tablicy przekodowań (LUT przekształcenia)
    6. Przekodowanie całego obrazu
    """
    
    # Sprawdzenie czy jest aktywne okno z obrazem
    img_info, image = get_focused_image_data()
    if image is None:
        return
    
    # Generacja tablicy LUT (histogram)
    lut_data = generate_lut()
    
    # Pobieramy tablicę lut z wygenerowanych danych
    lut = lut_data["lut"]  # tablica 256 elementów: histogram[i] = liczba pikseli o wartości i

    equalized_image = apply_per_channel(image, lut_data, calhistogram_equalization)
    
    # Wyświetlenie wyniku
    title = new_file_name(Path(img_info["filename"]), "_eq")
    show_image(equalized_image, title)

# zad 4
def negation():
    """Negacja - wersja zoptymalizowana bez pętli."""
    
    img_info, image = get_focused_mono_image()
    if image is None:
        return
    
    # Negacja całej tablicy naraz
    negated_image = 255 - image
    
    # Wyświetlenie
    #negated_image_bgr = cv2.cvtColor(negated_image, cv2.COLOR_GRAY2BGR)
    title = new_file_name(Path(img_info["filename"]), "_negation")
    show_image(negated_image, title)

def reduce_gray_levels():
    """Redukcja poziomów szarości przez powtórną kwantyzację."""
    img_info, image = get_focused_mono_image()
    if image is None:
        return
    
    # Okno dialogowe do wprowadzenia liczby poziomów
    dialog = Toplevel()
    dialog.title("Redukcja poziomów szarości")
    dialog.geometry("320x200")
    
    tk.Label(dialog, text="Podaj liczbę poziomów szarości (2-256):").pack(pady=10)
    
    entry = tk.Entry(dialog)
    entry.pack(pady=5)
    entry.insert(0, "16")  # wartość domyślna

    # ================================================================
    # Dodanie suwaka
    def update_entry_from_slider(value):
        entry.delete(0, tk.END)
        entry.insert(0, str(int(float(value))))
    
    slider = tk.Scale(
        dialog,
        from_=2,
        to=256,
        orient=tk.HORIZONTAL,
        length=250,
        command=update_entry_from_slider
    )
    slider.set(16)  # wartość domyślna
    slider.pack(pady=5)
    # ================================================================
    
    def apply_reduction():
        try:
            levels = int(entry.get())
            if levels < 2 or levels > 256:
                messagebox.showerror("Błąd", "Liczba poziomów musi być z zakresu 2-256.")
                return
            
            dialog.destroy()
            
            # Wykonaj redukcję poziomów szarości
            result_image = perform_gray_reduction(image, levels)
            
            # Wyświetl wynik
            title = new_file_name(Path(img_info["filename"]), f"_reduction{levels}")
            show_image(result_image, title)
            
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną liczbę całkowitą.")
    
    tk.Button(dialog, text="Zastosuj", command=apply_reduction).pack(pady=10)
    tk.Button(dialog, text="Anuluj", command=dialog.destroy).pack()

def perform_gray_reduction(image, levels):
    """
    Wykonuje redukcję poziomów szarości przez powtórną kwantyzację - wersja z LUT.
    
    Args:
        image: obraz wejściowy (monochromatyczny)
        levels: liczba poziomów szarości w obrazie wynikowym (2-256)
    
    Returns:
        obraz z zredukowaną liczbą poziomów szarości
    """
    # Tworzenie tablicy LUT (lookup table)
    lut = np.zeros(256, dtype=np.uint8)
    
    # Oblicz szerokość przedziału dla każdego poziomu
    interval_width = 256.0 / levels
    
    # Wypełnij tablicę LUT
    for i in range(256):
        # Określ, do którego przedziału należy wartość i
        interval_index = int(i / interval_width)
        
        # Zabezpieczenie przed przekroczeniem zakresu
        if interval_index >= levels:
            interval_index = levels - 1
        
        # Przypisz środkową wartość przedziału
        new_value = int((interval_index + 0.5) * interval_width)
        
        # Zabezpieczenie przed przekroczeniem zakresu 0-255
        lut[i] = min(255, max(0, new_value))
    
    # Zastosuj LUT do obrazu - znacznie szybsze niż pętle
    result = lut[image]
    
    return result

def threshold(dialog, title, function, add_name_suffix):
    """kod pokazujący okienko do progowania. można ten kod użyć jako progowanie binarne lub z zachowaniem poziomów szarości
    Args:
        dialog: okno dialogowe
        title: tytuł okna
        function: funkcja, która się uruchamia po kliknięciu zastosuj
        add_name_suffix: dodatek do nazwy pliku wynikowego"""
    
    img_info = globals_var.opened_images[globals_var.current_window]
    image = img_info["image"]
    
    # Sprawdź czy obraz jest monochromatyczny
    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacja działa tylko na obrazach monochromatycznych.")
        dialog.destroy()
        return

    dialog.title(title)
    dialog.geometry("600x520")
    
    # ========== TUTAJ WYWOŁUJĘ HISTOGRAM ==========
    # Tworzymy ramkę na histogram (to samo co main_frame w cal_hist)
    hist_frame = tk.Frame(dialog, bg='white')
    hist_frame.pack(pady=10)
    
    # Generujemy LUT i rysujemy histogram
    lut = generate_lut()
    if lut is not None and lut["color"] == False:
        bar_width = int(round(450 / 256))
        norm, var_max, mean, std, median_value, total_pixels = cal_mono_hist(lut["lut"])
        
        data = {
            "main_frame": hist_frame,
            "norm": norm,
            "var_max": var_max,
            "bar_width": bar_width,
            "mean": mean,
            "std": std,
            "median_value": median_value,
            "total_pixels": total_pixels,
            "color": "black"
        }
        show_hist(data)
    # ================================================
    
    # Ramka na kontrolki
    control_frame = tk.Frame(dialog)
    control_frame.pack(pady=10)
    
    tk.Label(control_frame, text="Wartość progu (0-255):").pack(pady=5)
    
    entry = tk.Entry(control_frame)
    entry.pack(pady=5)
    entry.insert(0, "128")  # wartość domyślna
    
    # Dodanie suwaka
    def update_entry_from_slider(value):
        entry.delete(0, tk.END)
        entry.insert(0, str(int(float(value))))
    
    slider = tk.Scale(
        control_frame,
        from_=0,
        to=255,
        orient=tk.HORIZONTAL,
        length=515,
        command=update_entry_from_slider
    )
    slider.set(128)  # wartość domyślna
    slider.pack(pady=5)
    
    def apply_threshold():
        try:
            threshold_value = int(entry.get())
            if threshold_value < 0 or threshold_value > 255:
                messagebox.showerror("Błąd", "Wartość progu musi być z zakresu 0-255.")
                return
            
            dialog.destroy()
            
            # Wykonaj progowanie binarne/z zachowaniem szarości
            result_image = function(image, threshold_value)
            
            # Wyświetl wynik
            title = new_file_name(Path(img_info["filename"]), f"{add_name_suffix}{threshold_value}")
            show_image(result_image, title)
            
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną liczbę całkowitą.")
    
    tk.Button(control_frame, text="Zastosuj", command=apply_threshold).pack(pady=10)
    tk.Button(control_frame, text="Anuluj", command=dialog.destroy).pack()

def binary_threshold():
    """Progowanie binarne z progiem wskazywanym przez użytkownika."""
    if globals_var.current_window not in globals_var.opened_images:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    # Okno dialogowe z histogramem
    dialog = Toplevel()
    threshold(dialog, "Progowanie binarne", perform_binary_threshold, "_binarythreshold")


def perform_binary_threshold(image, threshold):
    """
    Wykonuje progowanie binarne obrazu.
    
    Args:
        image: obraz wejściowy (monochromatyczny)
        threshold: wartość progu (0-255)
    
    Returns:
        obraz binarny (wartości 0 lub 255)
    """
    # Tworzenie tablicy LUT
    lut = np.zeros(256, dtype=np.uint8)
    
    # Wypełnij tablicę LUT zgodnie z progowaniem binarnym
    for i in range(256):
        if i >= threshold:
            lut[i] = 255  # biały
        else:
            lut[i] = 0    # czarny
    
    # Zastosuj LUT do obrazu
    result = lut[image]
    
    return result

def threshold_preserve_gray():
    """Progowanie z zachowaniem poziomów szarości."""
    if globals_var.current_window not in globals_var.opened_images:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return
    
    # Okno dialogowe z histogramem
    dialog = Toplevel()
    threshold(dialog, "Progowanie z zachowaniem poziomów szarości", perform_threshold_preserve_gray, "_thresholdpreservegray")

def perform_threshold_preserve_gray(image, threshold):
    """
    Wykonuje progowanie z zachowaniem poziomów szarości.
    Piksele poniżej progu są zerowane (czarne),
    piksele >= progu zachowują swoje wartości.
    
    Args:
        image: obraz wejściowy (monochromatyczny)
        threshold: wartość progu (0-255)
    
    Returns:
        obraz po progowaniu z zachowaniem poziomów szarości
    """
    # Tworzenie tablicy LUT
    lut = np.zeros(256, dtype=np.uint8)
    
    # Wypełnij tablicę LUT zgodnie z progowaniem z zachowaniem poziomów
    for i in range(256):
        if i >= threshold:
            lut[i] = i  # zachowaj oryginalną wartość
        else:
            lut[i] = 0  # zeruj (czarny)
    
    # Zastosuj LUT do obrazu
    result = lut[image]
    
    return result