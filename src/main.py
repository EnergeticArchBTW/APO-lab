import cv2  # biblioteka do wczytywania/zapisu obrazów
#import matplotlib.pyplot as plt  # do wyświetlania obrazów
from pathlib import Path  # do pracy ze ścieżkami
from tkinter import filedialog  # do okna wyboru pliku
from tkinter import Toplevel, Canvas #do okna z obrazem
from PIL import Image, ImageTk  # do konwersji obrazów do formatu Tkinter
from menu import MainMenu # plik main.py definiuje listę rozwijaną
import numpy as np # do operacji na tablicach
import threading # do wielowątkowości
import time # do opóźnień

opened_images = {}      # słownik: okno -> {"id": ..., "image": ..., "filename": ...}
current_id = 0       # licznik unikalnych ID dla okien
current_window = None   # wskaźnik na aktualnie aktywne okno

# Ścieżki do folderów
DATA_DIR = Path(__file__).parent.parent / "data" / "images"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Tworzymy folder outputs, jeśli nie istnieje
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def show_image(image, title="Podgląd obrazu"):
    """Wyświetla obraz w nowym oknie Tkinter z Canvas."""
    global current_id, current_window
    win = Toplevel()
    win.title(title)

    # Konwersja obrazu OpenCV (BGR) do PIL (RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    photo = ImageTk.PhotoImage(pil_img)

    canvas = Canvas(win, width=photo.width(), height=photo.height())
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # zapobiega usunięciu z pamięci

    # dodaj do słownika
    opened_images[win] = {"id": current_id, "image": image, "filename": title}
    current_id += 1
    # obsługa focusa
    def on_focus(event):
        global current_window
        current_window = win

    win.bind("<FocusIn>", on_focus)
    current_window = win

def save_image():
    """Zapisuje sfocusowany obraz w wybranej przez użytkownika lokalizacji."""
    if current_window in opened_images:
        img_info = opened_images[current_window]
        image = img_info["image"]
        # Prośba o lokalizację i nazwę pliku
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("Obrazy", "*.bmp;*.tif;*.png;*.jpg;*.jpeg")],
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
                    print("Błąd przy zapisie obrazu.")
                    return
            print(f"Zapisano obraz w: {file_path}")
    else:
        print("Brak aktywnego okna z obrazem do zapisu.")

def open_and_show_image():
    """Prosi użytkownika o wybór pliku i wyświetla obraz w nowym oknie."""
    global current_id
    file_path = filedialog.askopenfilename(
        title="Wybierz obraz",
        filetypes=[("Obrazy", "*.bmp;*.tif;*.png;*.jpg;*.jpeg")]
    )
    if file_path:
        # Wczytaj plik jako bajty, potem zdekoduj przez OpenCV (by polskie nazwy działały)
        file_path_obj = Path(file_path)
        with open(file_path_obj, "rb") as f:
            file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if image is not None:
            # Dodaj ID do nazwy pliku
            stem, ext = file_path_obj.stem, file_path_obj.suffix
            display_name = f"{stem}[{current_id}]{ext}"
            # Pokaz obraz
            show_image(image, title=display_name)
        else:
            print("Nie udało się wczytać obrazu.")

def duplicate_focused_image():
    """Duplikuje aktualnie sfocusowany obraz i wyświetla w nowym oknie."""
    if current_window in opened_images:
        img_info = opened_images[current_window]
        image_copy = img_info["image"].copy()
        # Dodaj _copy do nazwy pliku przed rozszerzeniem
        stem, ext = Path(img_info["filename"]).stem, Path(img_info["filename"]).suffix
        new_name = f"{stem}_copy{ext}"
        show_image(image_copy, title=new_name)
    else:
        print("Brak aktywnego okna z obrazem do duplikacji.")

# def show_focused_number():
#     """Wyświetla ID aktualnie aktywnego okna."""
#     while True:
#         if current_window in opened_images:
#             img_info = opened_images[current_window]
#             print(f"Aktualne okno ID: {img_info['id']}, Nazwa pliku: {img_info['filename']}")
#         else:
#             print("Brak aktywnego okna z obrazem.")
#         time.sleep(5)  # co 5 sekund

if __name__ == "__main__":
    # threading.Thread(target=show_focused_number, daemon=True).start()
    menu = MainMenu(open_and_show_image, save_image, duplicate_focused_image)
    menu.mainloop()