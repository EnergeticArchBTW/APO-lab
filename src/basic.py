import cv2  # biblioteka do wczytywania/zapisu obrazów
import globals_var  # zmienne globalne
import threading # do wielowątkowości
from win_thread import win_thread
from tkinter import Toplevel, Canvas #do okna z obrazem
from tkinter import messagebox # do błędów
from PIL import Image, ImageTk  # do konwersji obrazów do formatu Tkinter

""" funkcje, które są najczęściej używane w różnych miejscach """

def show_image(image, title="Podgląd obrazu"):
    """Wyświetla obraz w nowym oknie Tkinter z Canvas."""
    win = Toplevel()
    win.title(title)

    # Konwersja obrazu OpenCV (BGR) do PIL (RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(image_rgb)
    photo = ImageTk.PhotoImage(pil_img)

    canvas = Canvas(win, width=photo.width(), height=photo.height())
    img_id = canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo  # zapobiega usunięciu z pamięci

    # dodaj do słownika
    globals_var.opened_images[win] = {"id": globals_var.current_id, "image": image, "filename": title}
    globals_var.current_id += 1
    # uruchom wątek monitorujący okno
    threading.Thread(target=win_thread, daemon=True, args=(win,)).start()
    """
    # obsługa focusa
    def on_focus(event):
        globals_var.current_window = win

    win.bind("<FocusIn>", on_focus)
    globals_var.current_window = win
    """
    # ---------zmiana wielkości obrazu scrollem myszki ---------
    # Przechowuj oryginalny obraz i aktualny zoom
    win.original_image = image
    win.zoom = 1.0

    def update_image():
        # Przeskaluj obraz zgodnie z win.zoom
        # konwersja do PIL
        pil_img = Image.fromarray(cv2.cvtColor(win.original_image, cv2.COLOR_BGR2RGB))
        # pobieranie rozmiaru
        w, h = pil_img.size
        # aktualny współczynnik zoom
        scale = win.zoom
        # przeskalowanie obrazu
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        # tworzy obiekt PhotoImage
        photo = ImageTk.PhotoImage(pil_img)
        # ustawia rozmiar canvasa i aktualizuje obraz
        canvas.config(width=photo.width(), height=photo.height())
        # przywiązanie obrazu do canvasa, by nie został usunięty z pamięci
        canvas.photo = photo
        # aktualizacja obrazu na canvasie
        canvas.itemconfig(img_id, image=photo)
        win.title(f"{title} {win.zoom*100:.0f}% " + ("Monochromatyczny" if len(image.shape) == 2 else "Kolorowy"))
        canvas.pack()

    def on_mousewheel(event):
        # Zoom in/out
        win.zoom *= 1.1 if event.delta > 0 else 1/1.1
        update_image()

    canvas.bind("<MouseWheel>", on_mousewheel)
    win.bind("<FocusIn>", lambda e: setattr(globals_var, "current_window", win))
    update_image()
    # ----------------------------------------------------------

def generate_lut():
    """generuje LUT na podstawie stworzonej jednowymiarowej tablicy.
    tablica będzie miała indeks związany z poziomem jasności,
    a wartość będzie odpowiadała liczbie pikseli w obrazie o takiej wartości
    "color" czy kolorowy albo monochromatyczny
    "lut" tablica lub tablice lut
    "title" tytuł okna
    """
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        tit = f"{img_info["filename"]} tablica LUT"

        image = img_info["image"]
        h, w = 200, 256 # rozmiar obrazka z LUT

        # Sprawdź, czy obraz jest monochromatyczny czy kolorowy
        if len(image.shape) == 2:
            # MONOCHROMATYCZNY
            lut = [0] * 256
            height, width = image.shape
            for y in range(height):
                for x in range(width):
                    val = image[y, x]
                    lut[val] += 1
            result = {"color": False, "lut": lut, "title": tit}

        elif (len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] in [3, 4])):
            """ poprzedni warunek nie działał dla .png len(image.shape) == 3 and image.shape[2] == 3"""
            # KOLOROWY
            lut_b = [0] * 256
            lut_g = [0] * 256
            lut_r = [0] * 256
            height, width, _ = image.shape
            for y in range(height):
                for x in range(width):
                    b, g, r = image[y, x][:3]
                    lut_b[b] += 1
                    lut_g[g] += 1
                    lut_r[r] += 1
            result = {"color": True, "lut": [lut_r, lut_g, lut_b], "title": tit}

        else:
            messagebox.showerror("Błąd", "Nieobsługiwany format obrazu.")
            return None
        
        return result
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return None

def new_file_name(path, middle_name):
    """
    funkcja zwracającą nową nazwę pliku z rozszerzeniem.
    Args:
        path: obiekt Path do pliku
        middle_name: dodana fraza przed rozszerzeniem do pliku
    Returns:
        string z nową nazwą pliku
    """
    stem, ext = path.stem, path.suffix
    return f"{stem}{middle_name}{ext}"