# from menu import MainMenu # plik main.py definiuje listę rozwijaną
from tkinter import Tk, Menu # do listy rozwijanej
from lab1 import * 

"""Plik uruchamiający całą aplikację oraz posiadający definicję głównego okna palikacji."""

class MainMenu(Tk):
    def __init__(self, open_callback, save_callback, duplicate_callback, lut_callback, hist_callback, without_supersaturation_hist_callback, with_supersaturation5_hist_callback, eq_callback, negation_callback, reduce_gray_callback, binary_threshold_callback, threshold_preserve_gray_callback):
        super().__init__()
        self.title("APO laby - Michał Rymkiewicz")
        self.minsize(400, 200)  # minimalna szerokość: 400px, wysokość: 200px

        # Tworzenie paska menu
        menubar = Menu(self)
        self.config(menu=menubar)

        # Menu "Lab 1"
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Otwórz", command=open_callback)
        file_menu.add_command(label="Zapisz jako", command=save_callback)
        file_menu.add_command(label="Duplikuj", command=duplicate_callback)
        file_menu.add_command(label="Tablica LUT", command=lut_callback)
        file_menu.add_command(label="Histogram", command=hist_callback)
        file_menu.add_command(label="Rozciągnięcie histogramu bez przesycenia", command=without_supersaturation_hist_callback)
        file_menu.add_command(label="Rozciągnięcie histogramu z przesyceniem 5%", command=with_supersaturation5_hist_callback)
        file_menu.add_command(label="equalizacja", command=eq_callback)
        file_menu.add_command(label="negacja", command=negation_callback)
        file_menu.add_command(label="redukcja poziomów szarości przez powtórną kwantyzację", command=reduce_gray_callback)
        file_menu.add_command(label="progowanie binarne", command=binary_threshold_callback)
        file_menu.add_command(label="Progowanie z zachowaniem poziomów szarości", command=threshold_preserve_gray_callback)
        file_menu.add_separator()
        file_menu.add_command(label="Wyjdź", command=self.quit)
        menubar.add_cascade(label="Lab 1", menu=file_menu)

if __name__ == "__main__":
    # Tworzymy folder outputs, jeśli nie istnieje
    globals_var.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # threading.Thread(target=show_focused_number, daemon=True).start()
    menu = MainMenu(open_and_show_image, save_image, duplicate_focused_image, show_lut, cal_and_show_hist, calandshow_without_supersaturation_hist, calandshow_with_supersaturation5_hist, histogram_equalization, negation, reduce_gray_levels, binary_threshold, threshold_preserve_gray)
    menu.mainloop()