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
from lab1.lab1add import *

"""funkcje zrobione na labach 1, które są bezpośrednio wywoływane z menu"""

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

def calandshow_without_supersaturation_hist():
    """ liniowe rozciągnięcie histogramu bez przesycenia i pokazanie obrazu"""

    image_stretched = None

    #img_info = globals_var.opened_images[globals_var.current_window]
    #image = img_info["image"]

    img_info, image = get_focused_image_data()
    if image is None:
        return

    lut = generate_lut()
    if lut is not None:
        lut_values = lut["lut"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem lub nieobsługiwany obraz.")
        return

    image_stretched = apply_per_channel(image, lut, cal_without_supersaturation_hist)

    title = new_file_name(Path(img_info["filename"]), "_without_supersaturation")
    show_image(image_stretched, title=title)

def calandshow_with_supersaturation5_hist():
    """ liniowe rozciągnięcie histogramu z 5% przesyceniem i pokazanie obrazu"""
    image_stretched = None
    #img_info = globals_var.opened_images[globals_var.current_window]
    #image = img_info["image"]

    img_info, image = get_focused_image_data()
    if image is None:
        return

    lut = generate_lut()
    
    if lut is not None:
        lut_values = lut["lut"]
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem lub nieobsługiwany obraz.")
        return
    
    image_stretched = apply_per_channel(image, lut, cal_with_supersaturation5_hist)
    
    title = new_file_name(Path(img_info["filename"]), "_with_supersaturation5")
    show_image(image_stretched, title=title)

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

def binary_threshold():
    """Progowanie binarne z progiem wskazywanym przez użytkownika."""
    # Okno dialogowe z histogramem
    dialog = Toplevel()
    threshold(dialog, "Progowanie binarne", perform_binary_threshold, "_binarythreshold")

def threshold_preserve_gray():
    """Progowanie z zachowaniem poziomów szarości."""
    # Okno dialogowe z histogramem
    dialog = Toplevel()
    threshold(dialog, "Progowanie z zachowaniem poziomów szarości", perform_threshold_preserve_gray, "_thresholdpreservegray")