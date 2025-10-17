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

def add_images_no_saturation(images):
    """
    Dodaje obrazy bez wysycenia (z zawijaniem wartości).
    
    Args:
        images: lista obrazów do dodania (2-5 obrazów)
    
    Returns:
        numpy.ndarray: wynikowy obraz lub None w przypadku błędu
    """
    if not images or len(images) < 2:
        messagebox.showerror("Błąd", "Potrzebne są co najmniej 2 obrazy!")
        return None
    
    if len(images) > 5:
        messagebox.showerror("Błąd", "Maksymalnie 5 obrazów!")
        return None
    
    # Porównaj wszystkie obrazy z pierwszym
    first_img = images[0]
    for i, img in enumerate(images[1:], 1):
        if not compare_images(first_img, img):
            messagebox.showerror("Błąd", f"Obraz {i+1} nie pasuje do pierwszego!")
            return None
    
    # Dodawanie bez wysycenia - OpenCV automatycznie zawija wartości (modulo 256)
    result = images[0].copy()
    for img in images[1:]:
        result = cv2.add(result, img)
    
    return result

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
    print("\n--- DEBUG: Rozpoczynam przygotowanie 'image_data' ---")
    
    for key, data in globals_var.opened_images.items():
        image_obj = data.get("image")
        data_id = data.get("id")
        
        # Dodatkowy debug, aby sprawdzić, co jest w 'image'
        if image_obj is None:
            print(f"  [UWAGA]: Obraz dla klucza {key} (id: {data_id}) ma wartość None.")
        else:
            # Sprawdzamy typ, na wypadek gdyby to był numpy
            if hasattr(image_obj, 'shape'): 
                print(f"  [OK]: Obraz dla klucza {key} (id: {data_id}) to tablica NumPy o kształcie {image_obj.shape}")
            else:
                print(f"  [OK]: Obraz dla klucza {key} (id: {data_id}) to obiekt typu {type(image_obj)}")
                
        image_data.append((key, data.get("filename", "Brak Nazwy"), image_obj, data_id))
    
    print("--- DEBUG: Zakończono przygotowanie 'image_data' ---\n")

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

    # ----- POCZĄTEK DEBUGGINGU -----
    print("\n--- DEBUG: START ---")
    print("Aktualna zawartość globals_var.opened_images:")
    if not globals_var.opened_images:
        print("  Słownik jest PUSTY.")
    else:
        # Wypisujemy klucze (obiekty okien) i 'filename' dla identyfikacji
        for okno_klucz, dane in globals_var.opened_images.items():
            print(f"  Klucz (okno): {okno_klucz} -> Dane: {{'filename': {dane.get('filename')}, 'id': {dane.get('id')}}}")
            
    print("\nAktualna zawartość check_vars (klucz -> wartość zaznaczenia):")
    if not check_vars:
        print("  Słownik jest PUSTY.")
    else:
        for klucz, var in check_vars.items():
            print(f"  Klucz (nazwa?): {klucz} -> Wartość Vara: {var.get()}")
    print("--- DEBUG: Rozpoczynam pętlę ---\n")
    # ----- KONIEC DEBUGGINGU -----

    def on_select_button_click():
        """Obsługuje kliknięcie przycisku 'Wybierz'."""
        nonlocal selected_images
        selected_images.clear() 

        print(check_vars)

        for checked_id, var in check_vars.items():
        
            print(f"Sprawdzam ID: {checked_id}, Wartość (zaznaczony?): {var.get()}")
        
            if var.get() == 1:  # Jeśli Checkbutton jest zaznaczony
                print(f"  [ZAZNACZONO]: ID: {checked_id}")
            
                found_image = None
            
                for okno_key, data_dict in globals_var.opened_images.items():
                    if data_dict.get("id") == checked_id:
                        print(f"    ZNALAZŁEM! ID {checked_id} pasuje do okna {okno_key}")
                        found_image = data_dict.get("image")
                        break 

                # --- KRYTYCZNA POPRAWKA JEST TUTAJ ---
                # Musimy użyć 'is not None', aby poprawnie obsługiwać
                # tablice NumPy (które powodowały 'ValueError') ORAZ wartość None.
                
                if found_image is not None: 
                    print("    Sukces: Dodaję obraz do listy.")
                    selected_images.append(found_image)
                else:
                    # Ten błąd oznacza, że data_dict.get("image") zwróciło None.
                    print(f"    BŁĄD: Obiekt obrazu znaleziony dla ID {checked_id} ma wartość 'None'. Nie można dodać.")

        print(f"\nOstatecznie wybrano obrazów: {len(selected_images)}")

        print("\n--- DEBUG: Pętla zakończona ---")
        print(f"Ostateczna liczba wybranych obrazów: {len(selected_images)}")
        print("--- DEBUG: KONIEC ---")
        
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
    """funkcja dodająca od 2 do 5 obrazów bez wysycenia z GUI
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
    
    # Dodawanie bez wysycenia - OpenCV automatycznie zawija wartości (modulo 256)
    result = images[0].copy()
    for img in images[1:]:
        result = cv2.add(result, img)
    
    show_image(result, "Wynik dodawania bez wysycenia")