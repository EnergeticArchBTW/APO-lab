# from menu import MainMenu # plik main.py definiuje listę rozwijaną
from tkinter import Tk, Menu # do listy rozwijanej
from globals_var import *
from lab1 import * 
from lab2 import * 

"""Plik uruchamiający całą aplikację oraz posiadający definicję głównego okna palikacji."""

class MainMenu(Tk):
    def __init__(
            # lab 1
            self, open_callback, save_callback, duplicate_callback, lut_callback, hist_callback, without_supersaturation_hist_callback,
            with_supersaturation5_hist_callback, eq_callback, negation_callback, reduce_gray_callback, binary_threshold_callback,
            threshold_preserve_gray_callback,
            # lab 2
            add_images_without_saturation_callback, add_images_with_saturation_callback, add_number_with_stauration_callback,
            add_number_without_stauration_callback, divide_number_with_stauration_callback, divide_number_without_stauration_callback,
            multiply_number_with_stauration_callback, multiply_number_without_stauration_callback, subtract_images_absolute_callback,
            convert_grayscale_to_binary_mask_callback, convert_binary_to_grayscale_mask_callback, not_logic_callback,
            and_logic_callback, or_logic_callback, xor_logic_callback):
        super().__init__()
        self.title("APO laby - Michał Rymkiewicz")
        self.minsize(400, 200)  # minimalna szerokość: 400px, wysokość: 200px

        # Tworzenie paska menu
        menubar = Menu(self)
        self.config(menu=menubar)

        # Menu "Lab 1"
        file_menu = Menu(menubar, tearoff=0)
        # lab 1
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
        # lab 2
        file_menu2 = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lab 2", menu=file_menu2)
        file_menu2.add_command(label="Dodawanie obrazów do 5 bez wysycenia", command=add_images_without_saturation_callback)
        file_menu2.add_command(label="Dodawanie obrazów do 5 z wysyceniem", command=add_images_with_saturation_callback)
        file_menu2.add_command(label="Dodawanie liczby całkowitej do obrazu z saturacją", command=add_number_with_stauration_callback)
        file_menu2.add_command(label="Dodawanie liczby całkowitej do obrazu bez saturacji", command=add_number_without_stauration_callback)
        file_menu2.add_command(label="Dzielenie liczby całkowitej do obrazu z saturacją", command=divide_number_with_stauration_callback)
        file_menu2.add_command(label="Dzielenie liczby całkowitej do obrazu bez saturacji", command=divide_number_without_stauration_callback)
        file_menu2.add_command(label="Mnożenie liczby całkowitej do obrazu z saturacją", command=multiply_number_with_stauration_callback)
        file_menu2.add_command(label="Mnożenie liczby całkowitej do obrazu bez saturacji", command=multiply_number_without_stauration_callback)
        file_menu2.add_command(label="różnica bezwględna obrazów", command=subtract_images_absolute_callback)
        file_menu2.add_command(label="z 8-bit na binarną", command=convert_grayscale_to_binary_mask_callback)
        file_menu2.add_command(label="z binarnej na 8-bit", command=convert_binary_to_grayscale_mask_callback)
        file_menu2.add_command(label="NOT", command=not_logic_callback)
        file_menu2.add_command(label="AND", command=and_logic_callback)
        file_menu2.add_command(label="OR", command=or_logic_callback)
        file_menu2.add_command(label="XOR", command=xor_logic_callback)

if __name__ == "__main__":
    # Tworzymy folder outputs, jeśli nie istnieje
    globals_var.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # threading.Thread(target=show_focused_number, daemon=True).start()
    globals_var.root = MainMenu(
        # lab 1
        open_and_show_image, save_image, duplicate_focused_image, show_lut, cal_and_show_hist, calandshow_without_supersaturation_hist,
        calandshow_with_supersaturation5_hist, histogram_equalization, negation, reduce_gray_levels, binary_threshold, threshold_preserve_gray,
        # lab 2
        add_images_without_saturation, add_images_with_saturation, add_number_with_stauration, add_number_without_stauration, divide_number_with_stauration,
        divide_number_without_stauration, multiply_number_with_stauration, multiply_number_without_stauration, subtract_images_absolute, convert_grayscale_to_binary_mask, 
        convert_binary_to_grayscale_mask, not_logic, and_logic, or_logic, xor_logic)
    globals_var.root.mainloop()