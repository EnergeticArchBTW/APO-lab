import cv2  # biblioteka do wczytywania/zapisu obrazów
#import matplotlib.pyplot as plt  # do wyświetlania obrazów
from pathlib import Path  # do pracy ze ścieżkami
from tkinter import filedialog  # do okna wyboru pliku
from tkinter import Toplevel, Canvas #do okna z obrazem
from PIL import Image, ImageTk  # do konwersji obrazów do formatu Tkinter
from menu import MainMenu # plik main.py definiuje listę rozwijaną
import numpy as np # do operacji na tablicach
import threading # do wielowątkowości

# Ścieżki do folderów
DATA_DIR = Path(__file__).parent.parent / "data" / "images"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Tworzymy folder outputs, jeśli nie istnieje
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def show_image(image, title="Podgląd obrazu"):
    """Wyświetla obraz w nowym oknie Tkinter z Canvas."""
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

def save_copy(image, filename):
    """Zapisuje kopię obrazu do folderu outputs/."""
    out_path = OUTPUT_DIR / filename
    cv2.imwrite(str(out_path), image)
    print(f"Zapisano kopię obrazu w: {out_path}")

def open_and_show_image():
    """Prosi użytkownika o wybór pliku i wyświetla obraz w nowym oknie."""
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
            show_image(image, title=f"{file_path_obj.name}")
        else:
            print("Nie udało się wczytać obrazu.")

if __name__ == "__main__":
    menu = MainMenu(open_and_show_image, save_copy, show_image)
    menu.mainloop()