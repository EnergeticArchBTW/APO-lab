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

def cal_mono_hist(mono_lut):
    """ oblicza monochromatyczny histogram (albo jeden kanał kolorowy) i zwraca norm, var_max, mean, std, median_value, total_pixels.
     mono_lut to już jest sama tablica "lut", dla której wiadomo, że ma tylko jedną listę """
    var_max = max(mono_lut) # do niej normowane wysokości słupków
    print(var_max)

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
        bar_width = int(round(450 / 256))

        #okno.geometry("450x350") #szerokość 450 wysokość 350
        #dla monochromatycznych
        if lut["color"] == False:

            norm, var_max, mean, std, median_value, total_pixels = cal_mono_hist(lut["lut"])

            # Wyniki
            print(f"Średnia jasność: {mean:.2f}")
            print(f"Odchylenie standardowe: {std:.2f}")
            print(f"Mediana: {median_value}")
            print(f"Liczba pikseli: {total_pixels}")

            # pokaż dla sprawdzenia
            print(norm)

            #zwrócenie danych potrzebnych dla show_hist()
            data = {"main_frame": main_frame, "norm": norm, "var_max": var_max, "bar_width": bar_width,
                    "mean": mean, "std": std, "median_value": median_value, "total_pixels": total_pixels,
                    "color": "black"}
            show_hist(data)
        
        else:
            # RED
            norm_r, var_max_r, mean_r, std_r, median_value_r, total_pixels_r = cal_mono_hist(lut["lut"][0])
            data = {"main_frame": main_frame, "norm": norm_r, "var_max": var_max_r, "bar_width": bar_width,
                    "mean": mean_r, "std": std_r, "median_value": median_value_r, "total_pixels": total_pixels_r,
                    "color": "red"}
            show_hist(data)

            #GREEN
            norm_g, var_max_g, mean_g, std_g, median_value_g, total_pixels_g = cal_mono_hist(lut["lut"][1])
            data = {"main_frame": main_frame, "norm": norm_g, "var_max": var_max_g, "bar_width": bar_width,
                    "mean": mean_g, "std": std_g, "median_value": median_value_g, "total_pixels": total_pixels_g,
                    "color": "green"}
            show_hist(data)

            #BLUE
            norm_b, var_max_b, mean_b, std_b, median_value_b, total_pixels_b = cal_mono_hist(lut["lut"][2])
            data = {"main_frame": main_frame, "norm": norm_b, "var_max": var_max_b, "bar_width": bar_width,
                    "mean": mean_b, "std": std_b, "median_value": median_value_b, "total_pixels": total_pixels_b,
                    "color": "blue"}
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
    """ oblicza i pokazuje cały histogram dla monochromatycznych i kolrowych obrazów
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

    print(f"min_val = {min_val}, max_val = {max_val}")

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
    
    # sprawdzamy czy monochromatyczny
    if lut["color"] == False:
        image_stretched = cal_without_supersaturation_hist(image, lut_values)
    
    else:
        #dzielenie obrazu kolorowego na kanały
        b, g, r = cv2.split(image)
        r_stretched = cal_without_supersaturation_hist(r, lut_values[0])
        g_stretched = cal_without_supersaturation_hist(g, lut_values[1])
        b_stretched = cal_without_supersaturation_hist(b, lut_values[2])

        image_stretched = np.dstack((b_stretched, g_stretched, r_stretched))

    title = f"{img_info["filename"]}_without_supersaturation{Path(img_info["filename"]).suffix}"
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
    
    print(f"min_val = {min_val}, max_val = {max_val}")
    
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
    
    # sprawdzamy czy monochromatyczny
    if lut["color"] == False:
        image_stretched = cal_with_supersaturation5_hist(image, lut_values)
    else:
        # dzielenie obrazu kolorowego na kanały
        b, g, r = cv2.split(image)
        r_stretched = cal_with_supersaturation5_hist(r, lut_values[0])
        g_stretched = cal_with_supersaturation5_hist(g, lut_values[1])
        b_stretched = cal_with_supersaturation5_hist(b, lut_values[2])
        image_stretched = np.dstack((b_stretched, g_stretched, r_stretched))
    
    title = f"{img_info['filename']}_with_supersaturation5{Path(img_info['filename']).suffix}"
    show_image(image_stretched, title=title)