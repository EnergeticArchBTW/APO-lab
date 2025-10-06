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
import threading # do wielowątkowości

"""funkcje zrobione na labach 1"""

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
            print(f"Zapisano obraz w: {file_path}")
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
            stem, ext = file_path_obj.stem, file_path_obj.suffix
            display_name = f"{stem}[{globals_var.current_id}]{ext}"
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
        stem, ext = Path(img_info["filename"]).stem, Path(img_info["filename"]).suffix
        new_name = f"{stem}_copy{ext}"
        show_image(image_copy, title=new_name)
    else:
        messagebox.showerror("Błąd", "Brak aktywnego okna z obrazem do duplikacji.")

# def show_focused_number():
#     """Wyświetla ID aktualnie aktywnego okna."""
#     while True:
#         if current_window in opened_images:
#             img_info = opened_images[current_window]
#             print(f"Aktualne okno ID: {img_info['id']}, Nazwa pliku: {img_info['filename']}")
#         else:
#             print("Brak aktywnego okna z obrazem.")
#         time.sleep(5)  # co 5 sekund

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

        elif len(image.shape) == 3 and image.shape[2] == 3:
            # KOLOROWY
            lut_b = [0] * 256
            lut_g = [0] * 256
            lut_r = [0] * 256
            height, width, _ = image.shape
            for y in range(height):
                for x in range(width):
                    b, g, r = image[y, x]
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

def show_hist():
    """ pokazanie histogramu """
    lut = generate_lut()
    #sprawdzamy czy wogóle jakiś obrazek jest
    if lut is not None:
        #okno.geometry("450x350") #szerokość 450 wysokość 350
        #dla monochromatycznych
        if lut["color"] == False:
            #wzięcie jasności, co ma najwięcej pikseli
            var_max = max(lut["lut"]) # do niej normowane wysokości słupków
            print(var_max)

            # normowanie przez podzielenie
            norm = lut["lut"]

            #running_count to licznik do mediany
            mean = std = median_value = total_pixels = brightness_sum = running_count = 0
            norm = [0] * len(lut["lut"])
            # obliczenia tylko gdy nie ma samych zer
            if var_max != 0:
                norm = [int((val / var_max) * 300) for val in lut["lut"]]

                #kumulowanie informacji
                total_pixels = sum(lut["lut"])              #ilość pikseli w obrazie
                median_pixel = total_pixels // 2            # połowa — do mediany

                for level, count in enumerate(lut["lut"]):
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
                variance_sum = sum(((level - mean) ** 2) * count for level, count in enumerate(lut["lut"]))
                std = (variance_sum / total_pixels) ** 0.5 if total_pixels > 0 else 0

            # Wyniki
            print(f"Średnia jasność: {mean:.2f}")
            print(f"Odchylenie standardowe: {std:.2f}")
            print(f"Mediana: {median_value}")
            print(f"Liczba pikseli: {total_pixels}")

            # pokaż dla sprawdzenia
            print(norm)

            #obliczanie grubości słupka (szerokość) / 256
            bar_width = int(round(450 / 256))

            # rysowanie (potrzebne norm, var_max, bar_width)
            okno = tk.Toplevel()
            okno.title("histogram")
            canvas = tk.Canvas(okno, width=580, height=360, bg='white')
            canvas.pack()
            
            # rysowanie słupków (przesunięte o 50 w prawo i w górę by zrobić miejsce na opisy)
            for i, height in enumerate(norm):
                x = 50 + i * bar_width
                canvas.create_rectangle(x, 300 - height, x + bar_width, 300, fill='black', outline='')
            
            # tekst z maksymalną wartością (góra po lewej)
            canvas.create_text(25, 0, text=str(var_max), anchor='n')
            
            # tekst "0" na dole po lewej
            canvas.create_text(25, 300, text='0', anchor='s')
            
            # tekst "0" na dole histogramu po lewej stronie
            canvas.create_text(50, 320, text='0', anchor='n')
            
            # tekst "255" na dole histogramu po prawej stronie
            canvas.create_text(50 + 255 * bar_width, 320, text='255', anchor='n')