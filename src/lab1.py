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
        win.title(f"{title} {win.zoom*100:.0f}%")
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
    a wartość będzie odpowiadała liczbie pikseli w obrazie o takiej wartości"""
    if globals_var.current_window in globals_var.opened_images:
        img_info = globals_var.opened_images[globals_var.current_window]
        # Tworzymy nowe okno
        okno = tk.Toplevel()
        tit = f"{img_info["filename"]} tablica LUT"
        okno.title(tit)

        image = img_info["image"]
        h, w = 200, 256 # rozmiar obrazka z LUT

        # Sprawdź, czy obraz jest monochromatyczny czy kolorowy
        # print(f"Kształt obrazu: {image.shape}")
        if len(image.shape) == 2:
            # MONOCHROMATYCZNY
            lut = [0] * 256
            height, width = image.shape
            for y in range(height):
                for x in range(width):
                    val = image[y, x]
                    lut[val] += 1
            #print("LUT dla obrazu monochromatycznego:", lut)
            # pokazanie tablicy LUT w oknie
            """
            # Tworzymy Treeview z jedną kolumną
            tree = ttk.Treeview(okno, columns=("Wartość",), show="headings")
            tree.heading("Wartość", text="Wartość")
            tree.pack(padx=10, pady=10)

            # Wypełniamy tabelę
            for element in lut:
                tree.insert("", tk.END, values=(element,))
            """
            """
            # Frame z przewijaniem
            frame = tk.Frame(okno)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Scrollbar
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Treeview
            tree = ttk.Treeview(frame, columns=("Wartość",), show="headings", yscrollcommand=scrollbar.set)
            tree.heading("Wartość", text="Wartość")
            tree.column("Wartość", anchor=tk.CENTER, width=250)
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar.config(command=tree.yview)

            # Wypełnienie danymi
            for i, element in enumerate(lut):
                tree.insert("", tk.END, values=(element,))
            """
            """
            frame = tk.Frame(okno)
            frame.pack(padx=10, pady=10)

            # Treeview z dwiema kolumnami
            tree = ttk.Treeview(frame, columns=("Indeks", "Wartość"), show="headings", height=10)
            tree.heading("Indeks", text="Poziom jasności")
            tree.heading("Wartość", text="Wartość")
            tree.column("Indeks", width=120)
            tree.column("Wartość", width=120)
            tree.pack()

            # Funkcja aktualizująca widok
            def aktualizuj(val):
                tree.delete(*tree.get_children())
                start = int(val)
                for i in range(start, min(start + 10, 256)):
                    tree.insert("", tk.END, values=(i, lut[i]))

            # Suwak
            suwak = tk.Scale(okno, from_=0, to=246, orient=tk.HORIZONTAL, command=aktualizuj, length=260)
            suwak.pack(padx=10, pady=10)
            suwak.set(0)
            """
            frame = tk.Frame(okno)
            frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
                tree.insert("", tk.END, values=(i, lut[i]))
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
            # print("LUT dla kanału B:", lut_b)
            # print("LUT dla kanału G:", lut_g)
            # print("LUT dla kanału R:", lut_r)
            
        else:
            okno.destroy()
            print("Nieobsługiwany format obrazu.")
    else:
        okno.destroy()
        print("Brak aktywnego okna z obrazem.")

def show_lut():
    """Generuje i wyświetla tablicę LUT dla aktualnie sfocusowanego obrazu."""
    lut_image = generate_lut()
    # if lut_image is not None:
    #     title = globals_var.opened_images[globals_var.current_window]["filename"] + "_LUT"
    #     show_image(lut_image, title)