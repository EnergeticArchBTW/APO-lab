import cv2  # biblioteka do wczytywania/zapisu obrazów
import globals_var  # zmienne globalne
import threading # do wielowątkowości
from win_thread import win_thread
from tkinter import Toplevel, Canvas #do okna z obrazem
from tkinter import messagebox # do błędów
import numpy as np # do operacji na tablicach
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

        # Zmień rozmiar okna 'win', ale tylko jeśli nie jest zmaksymalizowane
        if win.state() == 'normal':
            win.geometry(f"{photo.width()}x{photo.height()}")
        # --- KONIEC DODANEGO FRAGMENTU ---

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

    # --------- obsługa maksymalizacji i zmiany rozmiaru okna ---------
    win.previous_state = win.state()  # Zmienna do śledzenia poprzedniego stanu okna

    def on_resize_or_maximize(event):
        """Obsługuje zdarzenie zmiany rozmiaru lub stanu okna (np. maksymalizacji)."""
        current_state = win.state()

        # Sprawdzamy, czy okno *właśnie* zostało zmaksymalizowane
        # (przeszło ze stanu 'normal' lub innego do 'zoomed')
        if current_state == 'zoomed' and win.previous_state != 'zoomed':
            print("maksymalizacja")
            # UWAGA: Aby to działało poprawnie, widget Canvas MUSI
            # być spakowany z opcjami fill="both" i expand=True,
            # a funkcja update_image() NIE POWINNA zmieniać rozmiaru
            # canvasu za pomocą canvas.config().
            
            # Zakładając, że canvas wypełnia okno, pobieramy jego aktualne wymiary
            # (event.width i event.height odnoszą się do widgetu, do którego przypięto zdarzenie)
            # Ponieważ zdarzenie jest przypięte do 'win', musimy pobrać rozmiar 'canvas'
            # lub (prościej) rozmiar *wewnętrzny* okna:
            
            canvas_width = win.winfo_width()
            canvas_height = win.winfo_height()

            # Pobieramy oryginalne wymiary obrazu (z atrybutów numpy/OpenCV)
            h, w = win.original_image.shape[:2]

            if w > 0 and h > 0:
                # Obliczamy współczynniki skalowania dla szerokości i wysokości
                ratio_w = canvas_width / w
                ratio_h = canvas_height / h
                
                # Wybieramy mniejszy współczynnik (tryb "fit"),
                # aby zachować proporcje i zmieścić cały obraz
                win.zoom = min(ratio_w, ratio_h)
                
                # Aktualizujemy obraz z nowym, obliczonym zoomem
                update_image()
        
        elif current_state == 'normal' and win.previous_state != 'normal':
            print("minimalizacja")
            win.zoom = 1.0
            update_image()
        
        # Zapisujemy bieżący stan jako poprzedni dla następnego wywołania
        win.previous_state = current_state

    # Przypisanie funkcji do zdarzenia <Configure> okna 'win'
    win.bind("<Configure>", on_resize_or_maximize)
    # ----------------------------------------------------------

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

def get_focused_image_data():
    """Pobiera dane aktywnego obrazu (img_info, image). Zwraca (None, None) i pokazuje błąd, jeśli nie ma aktywnego okna.
    przykładowe użycie:
        img_info, image = get_focused_image_data()
        if image is None:
            return
    """
    if globals_var.current_window not in globals_var.opened_images:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem.")
        return None, None
    
    img_info = globals_var.opened_images[globals_var.current_window]
    image = img_info["image"]
    return img_info, image

def get_focused_mono_image():
    """Pobiera aktywny obraz i sprawdza, czy jest mono. Zwraca (img_info, image) lub (None, None) przy błędzie.
    przykładowe użycie:
        img_info, image = get_focused_mono_image()
        if image is None:
            return
    """
    img_info, image = get_focused_image_data() # Używamy funkcji wyżej
    if image is None:
        return None, None

    if len(image.shape) != 2:
        messagebox.showerror("Błąd", "Operacja działa tylko na obrazach monochromatycznych.")
        return None, None
        
    return img_info, image

def apply_per_channel(image, lut_data, single_channel_function):
    """Aplikuje funkcję 'single_channel_function' na obrazie mono lub na każdym kanale obrazu kolorowego."""
    
    lut_values = lut_data["lut"]
    
    if lut_data["color"] == False:
        # Obraz mono
        return single_channel_function(image, lut_values)
    else:
        # Obraz kolorowy
        # Dzielenie na kanały
        b = image[:, :, 0:1]
        g = image[:, :, 1:2]
        r = image[:, :, 2:3]
        
        # 'single_channel_function' to np. cal_with_supersaturation5_hist
        r_processed = single_channel_function(r, lut_values[0])
        g_processed = single_channel_function(g, lut_values[1])
        b_processed = single_channel_function(b, lut_values[2])

        # składanie
        return np.dstack((b_processed, g_processed, r_processed))