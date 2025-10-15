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
    # Lista par (klucz_słownika, nazwa_pliku, obiekt_obrazu)
    image_data = []
    for key, data in globals_var.opened_images.items():
        image_data.append((key, data.get("filename", "Brak Nazwy"), data.get("image")))

    if not image_data:
        messagebox.showinfo("Brak danych", "Brak danych obrazów do przetworzenia.")
        return []

    # 3. Utworzenie głównego okna (root) i okna podrzędnego (Toplevel)
    # Musimy mieć root, nawet jeśli jest schowany, żeby Toplevel działał poprawnie.
    # W Twojej aplikacji root prawdopodobnie już istnieje. Tutaj go symulujemy.
    try:
        root = tk.Tk()
        root.withdraw() # Ukryj główne okno
    except tk.TclError:
        # Możliwe, że root już istnieje (np. w środowisku IDE/interaktywnym)
        root = tk.Toplevel()
        root.withdraw()

    selection_window = tk.Toplevel(root)
    selection_window.title("Wybierz Obrazy")
    selection_window.geometry("400x300")
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
        selected_images.clear() # Czyścimy listę na wszelki wypadek

        for key, var in check_vars.items():
            if var.get() == 1:  # Jeśli Checkbutton jest zaznaczony (wartość 1)
                # Odszukaj odpowiadający obiekt obrazu w global_vars.opened_images
                image_object = globals_var.opened_images.get(key, {}).get("image")
                if image_object:
                    selected_images.append(image_object)
        
        # Zamykamy okno i zwalniamy focus
        selection_window.grab_release()
        selection_window.destroy()
        
        # Opcjonalnie: Zamykamy też root, jeśli został stworzony w tej funkcji
        # W Twojej aplikacji (jeśli root jest głównym oknem) tego kroku nie rób!
        try:
            root.destroy()
        except Exception:
            pass

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
    for key, filename, image_obj in image_data:
        # Używamy IntVara, żeby sprawdzić, czy Checkbutton jest zaznaczony (0 lub 1)
        var = tk.IntVar(value=0) 
        check_vars[key] = var

        # Checkbutton wyświetla nazwę pliku, a jego stan jest powiązany z var
        cb = tk.Checkbutton(check_frame, text=filename, variable=var, 
                            anchor="w", justify="left")
        cb.pack(fill="x", padx=10, pady=2)

    # 6. Dodanie przycisku "Wybierz"
    select_button = tk.Button(selection_window, text="Wybierz", command=on_select_button_click)
    select_button.pack(side="bottom", fill="x", pady=10)

    # Uruchomienie pętli zdarzeń okna podrzędnego, czekając na jego zamknięcie
    # Musimy użyć wait_window, żeby funkcja mogła zwrócić wynik po zamknięciu okna.
    selection_window.protocol("WM_DELETE_WINDOW", lambda: [selection_window.grab_release(), selection_window.destroy(), messagebox.showinfo("Anulowano", "Wybór anulowany."), root.destroy() if 'root' in locals() and root.winfo_exists() else None])
    selection_window.wait_window(selection_window)
    
    # 7. Zwrócenie wyniku po zamknięciu okna
    return selected_images


def add_images_without_saturation():
    """funkcja dodająca od 2 do 5 obrazów bez wysycenia z GUI
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
    
    # Dodawanie bez wysycenia - OpenCV automatycznie zawija wartości (modulo 256)
    result = images[0].copy()
    for img in images[1:]:
        result = cv2.add(result, img)
    
    show_image(result, "Wynik dodawania bez wysycenia")