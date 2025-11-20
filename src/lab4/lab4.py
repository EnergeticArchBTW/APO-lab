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
import csv
import math #do logarytmowania

"""funkcje zrobione na labach 4"""

# zad 1

def save_results_to_csv(data, original_filename, suffix):
    """Pomocnicza funkcja do zapisu listy słowników do CSV (Excel)"""
    if not data:
        messagebox.showinfo("Info", "Nie znaleziono obiektów do zapisu.")
        return
    
    path = filedialog.asksaveasfilename(
        defaultextension=".jpg",
        filetypes=[("Arkusz", "*.csv")],
        initialdir=globals_var.OUTPUT_DIR, # <-- domyślny folder
        initialfile=original_filename+suffix
    )
    # Zapisz w tym samym folderze z dopiskiem
    #output_path = path.parent / f"{path.stem}{suffix}.csv"

    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            # Używamy średnika (;) jako separatora, bo polski Excel tak lubi
            writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader() # nagłówki kolumn
            writer.writerows(data) # dane
        
        #messagebox.showinfo("Sukces", f"Dane zapisano w pliku:\n{output_path.name}")
        messagebox.showinfo("Sukces", f"Dane zapisano w katalogu:\n{path}")
    except Exception as e:
        messagebox.showerror("Błąd zapisu", str(e))

def designation():
    # 1. Pobierz obraz (Wymagany mono/binarny)
    img_info, image = get_focused_mono_image()
    if image is None: return

    # 2. Binaryzacja i Inwersja (jeśli trzeba)
    # Wykład: Obraz ma pokazywać obiekty (jasne) i ciemne tło.
    # sprawdzamy, czy obraz jest binarny (0 i 255)
    if is_binary_image(image) == False:
        return

    # 3. Znalezienie konturów (Segmentacja obiektów)
    # Wykład: findContours znajduje kontury, co pozwala analizować każdy obiekt oddzielnie.
    # RETR_EXTERNAL - bierzemy tylko zewnętrzne obrysy (ignorujemy dziury w środku na tym etapie)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results = []
    preview_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) # Do wizualizacji numerków

    print(f"Znaleziono {len(contours)} obiektów.")

    # 4. Pętla po obiektach i obliczenia
    for i, contour in enumerate(contours):
        # Wykład: Funkcja moments liczy momenty dla danego konturu
        M = cv2.moments(contour)

        # Zabezpieczenie przed dzieleniem przez zero (bardzo małe szumy)
        if M['m00'] == 0:
            continue

        # --- A. Środek ciężkości (Centroid) ---
        # Wykład: Liczony z momentów m10/m00 i m01/m00 (momenty geometryczne)
        cx = int(M['m10'] / M['m00']) # po m wartości p i q jak w wykładzie
        cy = int(M['m01'] / M['m00'])

        # --- A. Momenty Hu (Niezmiennicze) ---
        # Wykład: Moment 1 i 7 mają największą "inwariantność" 
        hu_moments = cv2.HuMoments(M).flatten()

        #logarytmujemy momenty Hu dla lepszej interpretacji
        for j in range(len(hu_moments)):
            # Zabezpieczenie: logarytmujemy tylko jeśli nie jest zerem
            if hu_moments[j] != 0:
                # Wzór: -1 * znak * log10(|wartość|)
                # Dzięki temu 10^-7 zamieni się w czytelne "7" (z odpowiednim znakiem)
                hu_moments[j] = -1 * math.copysign(1.0, hu_moments[j]) * math.log10(abs(hu_moments[j]))
            else:
                hu_moments[j] = 0.0

        # --- B. Pole powierzchni i obwód ---
        # pole powierzchni - jest najczęściej wyrażane ilością pikseli wewnątrz obrysu
        area = cv2.contourArea(contour)

        # obwód - długość brzegu obiektu
        # True oznacza, że kontur jest zamknięty (figura geometryczna)
        perimeter = cv2.arcLength(contour, True)

        # --- C. Współczynniki Kształtu ---
        
        # 1. Aspect Ratio & Extent (wymagają prostokąta otaczającego)
        x, y, w, h = cv2.boundingRect(contour)
        rect_area = w * h
        
        # Zabezpieczenie przed dzieleniem przez zero
        aspect_ratio = float(w) / h if h > 0 else 0
        extent = float(area) / rect_area if rect_area > 0 else 0
        
        # 2. Solidity (wymaga otoczki wypukłej - Convex Hull)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        # 3. Equivalent Diameter
        # średnia średnica równoważona
        equivalent_diameter = np.sqrt(4 * area / np.pi)
        
        # Zbieramy dane do wektora cech
        # (Wykład wspomina o logarytmowaniu momentów Hu bo są małe, 
        # więc dodaję log10)
        obj_data = {
            "ID Obiektu": i + 1,
            # Podpunkt a)
            "M00 (Masa)": M['m00'],     # Moment zerowy
            "Hu 1 (z log10)": hu_moments[0],      # momenty Hu
            "Hu 7 (z log10)": hu_moments[6],
            # Podpunkt b)
            "Pole (Area)": area,
            "Obwod (Perimeter)": perimeter,
            "Centroid X": cx,           # Współrzędna X środka
            "Centroid Y": cy,           # Współrzędna Y środka
            # Podpunkt c) - Współczynniki
            "Aspect Ratio": aspect_ratio, # Stosunek boków
            "Extent": extent,             # Wypełnienie prostokąta
            "Solidity": solidity,         # Masywność (Wypukłość)
            "EquivDiameter": equivalent_diameter, # Średnica koła
            # pomocnicze
            "Hu 2 (z log10)": hu_moments[1],      # Momenty Hu
            "Hu 3 (z log10)": hu_moments[2]
        }
        results.append(obj_data)

        # Wizualizacja: Rysujemy numer obiektu i środek ciężkości
        cv2.circle(preview_img, (cx, cy), 5, (0, 0, 255), -1)
        cv2.putText(preview_img, str(i+1), (cx - 20, cy - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 5. Zapis do pliku (Excel CSV)
    # Wykład: Oprogramowanie ma zamieścić pomiary w Excelu
    save_results_to_csv(results, img_info["filename"], "_moments")
    
    # Pokaż obraz z ponumerowanymi obiektami (żeby wiedzieć który jest który w Excelu)
    show_image(preview_img, "Zidentyfikowane Obiekty")