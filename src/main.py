# from menu import MainMenu # plik main.py definiuje listę rozwijaną
from tkinter import Tk, Menu # do listy rozwijanej
from globals_var import *
from lab1.lab1 import * 
from lab2.lab2 import * 
from lab3.lab3 import * 
from lab4.lab4 import * 
from projekt.projekt31 import *

"""Plik uruchamiający całą aplikację oraz posiadający definicję głównego okna palikacji."""

class MainMenu(Tk):
    def __init__(
            self,
            # projekt
            averaging_photos_callabck, run_logical_operations_project_callback, convert_to_grayscale_and_show_callback,
            # lab 1
            open_callback, save_callback, duplicate_callback, lut_callback, hist_callback, without_supersaturation_hist_callback,
            with_supersaturation5_hist_callback, eq_callback, negation_callback, reduce_gray_callback, binary_threshold_callback,
            threshold_preserve_gray_callback,
            # lab 2
            add_images_without_saturation_callback, add_images_with_saturation_callback, add_number_with_stauration_callback,
            add_number_without_stauration_callback, divide_number_with_stauration_callback, divide_number_without_stauration_callback,
            multiply_number_with_stauration_callback, multiply_number_without_stauration_callback, subtract_images_absolute_callback,
            convert_grayscale_to_binary_mask_callback, convert_binary_to_grayscale_mask_callback, not_logic_callback,
            and_logic_callback, or_logic_callback, xor_logic_callback, show_filter_selection_window_callback,
            run_gaussian_filter_callback, run_sobel_operator_callback, run_median_filter_callback,
            run_canny_detector_callback,
            # lab 3
            stretch_histogram_operation_callback, threshold_preserve_gray_user_callback, otsu_callback,
            run_adaptive_threshold_callback, run_morphological_operations_callback,
            run_skeletonization_callback, designation_callback, run_grabcut_callback):
        super().__init__()
        self.title("APO laby - Michał Rymkiewicz")
        self.minsize(400, 200)  # minimalna szerokość: 400px, wysokość: 200px

        # Tworzenie paska menu
        menubar = Menu(self)
        self.config(menu=menubar)

        # Menu "Projekt"
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="uśrednianie obrazów", command=averaging_photos_callabck)
        file_menu.add_command(label="usuwanie szumu obraz binarny", command=run_logical_operations_project_callback)
        file_menu.add_command(label="konwersja obrazu na monochromatycny", command=convert_to_grayscale_and_show_callback)
        menubar.add_cascade(label="Projekt", menu=file_menu)

        # Menu "Lab 1"
        file_menu2 = Menu(menubar, tearoff=0)
        # lab 1
        file_menu2.add_command(label="Otwórz", command=open_callback)
        file_menu2.add_command(label="Zapisz jako", command=save_callback)
        file_menu2.add_command(label="Duplikuj", command=duplicate_callback)
        file_menu2.add_command(label="Tablica LUT", command=lut_callback)
        file_menu2.add_command(label="Histogram", command=hist_callback)
        file_menu2.add_command(label="Rozciągnięcie histogramu bez przesycenia", command=without_supersaturation_hist_callback)
        file_menu2.add_command(label="Rozciągnięcie histogramu z przesyceniem 5%", command=with_supersaturation5_hist_callback)
        file_menu2.add_command(label="equalizacja", command=eq_callback)
        file_menu2.add_command(label="negacja", command=negation_callback)
        file_menu2.add_command(label="redukcja poziomów szarości przez powtórną kwantyzację", command=reduce_gray_callback)
        file_menu2.add_command(label="progowanie binarne", command=binary_threshold_callback)
        file_menu2.add_command(label="Progowanie z zachowaniem poziomów szarości", command=threshold_preserve_gray_callback)
        file_menu2.add_separator()
        file_menu2.add_command(label="Wyjdź", command=self.quit)
        menubar.add_cascade(label="Lab 1", menu=file_menu2)
        # lab 2
        file_menu3 = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Lab 2", menu=file_menu3)
        file_menu3.add_command(label="Dodawanie obrazów do 5 bez wysycenia", command=add_images_without_saturation_callback)
        file_menu3.add_command(label="Dodawanie obrazów do 5 z wysyceniem", command=add_images_with_saturation_callback)
        file_menu3.add_command(label="Dodawanie liczby całkowitej do obrazu z saturacją", command=add_number_with_stauration_callback)
        file_menu3.add_command(label="Dodawanie liczby całkowitej do obrazu bez saturacji", command=add_number_without_stauration_callback)
        file_menu3.add_command(label="Dzielenie liczby całkowitej do obrazu z saturacją", command=divide_number_with_stauration_callback)
        file_menu3.add_command(label="Dzielenie liczby całkowitej do obrazu bez saturacji", command=divide_number_without_stauration_callback)
        file_menu3.add_command(label="Mnożenie liczby całkowitej do obrazu z saturacją", command=multiply_number_with_stauration_callback)
        file_menu3.add_command(label="Mnożenie liczby całkowitej do obrazu bez saturacji", command=multiply_number_without_stauration_callback)
        file_menu3.add_command(label="różnica bezwględna obrazów", command=subtract_images_absolute_callback)
        file_menu3.add_command(label="z 8-bit na binarną", command=convert_grayscale_to_binary_mask_callback)
        file_menu3.add_command(label="z binarnej na 8-bit", command=convert_binary_to_grayscale_mask_callback)
        file_menu3.add_command(label="NOT", command=not_logic_callback)
        file_menu3.add_command(label="AND", command=and_logic_callback)
        file_menu3.add_command(label="OR", command=or_logic_callback)
        file_menu3.add_command(label="XOR", command=xor_logic_callback)
        file_menu3.add_command(label="wybierz filtr", command=show_filter_selection_window_callback)
        file_menu3.add_command(label="filtr gaussowski", command=run_gaussian_filter_callback)
        file_menu3.add_command(label="detekcja krawędzi operacjami sobela", command=run_sobel_operator_callback)
        file_menu3.add_command(label="filtracja medianowa", command=run_median_filter_callback)
        file_menu3.add_command(label="detekcja krawędzi operatorem Canyego", command=run_canny_detector_callback)
        # lab 3
        file_menu4 = Menu(menubar, tearoff=0)
        file_menu4.add_command(label="Rozciąganie histogramu w zadanym przez użytkownika zakresie", command=stretch_histogram_operation_callback)
        file_menu4.add_command(label="Progowanie z dwoma progami wyznaczonymi przez użytkownika", command=threshold_preserve_gray_user_callback)
        file_menu4.add_command(label="Progowanie z progiem wyznaczonym metodą Otsu", command=otsu_callback)
        file_menu4.add_command(label="Implementacja progowanie adaptacyjnego (adaptive threshold)", command=run_adaptive_threshold_callback)
        file_menu4.add_command(label="operacje morfologii matematycznej", command=run_morphological_operations_callback)
        file_menu4.add_command(label="szkieletyzacja", command=run_skeletonization_callback)
        file_menu4.add_command(label="wyznaczanie momentu, pola powierzchni i współczynniki kształtu", command=designation_callback)
        file_menu4.add_command(label="segmentacja z GraphCut", command=run_grabcut_callback)
        menubar.add_cascade(label="Lab 3", menu=file_menu4)

if __name__ == "__main__":
    # Tworzymy folder outputs, jeśli nie istnieje
    globals_var.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # threading.Thread(target=show_focused_number, daemon=True).start()
    globals_var.root = MainMenu(
        # projekt
        averaging_photos, run_logical_operations_project, convert_to_grayscale_and_show,
        # lab 1
        open_and_show_image, save_image, duplicate_focused_image, show_lut, cal_and_show_hist, calandshow_without_supersaturation_hist,
        calandshow_with_supersaturation5_hist, histogram_equalization, negation, reduce_gray_levels, binary_threshold, threshold_preserve_gray,
        # lab 2
        add_images_without_saturation, add_images_with_saturation, add_number_with_stauration, add_number_without_stauration, divide_number_with_stauration,
        divide_number_without_stauration, multiply_number_with_stauration, multiply_number_without_stauration, subtract_images_absolute, convert_grayscale_to_binary_mask, 
        convert_binary_to_grayscale_mask, not_logic, and_logic, or_logic, xor_logic, show_filter_selection_window, run_gaussian_filter, run_sobel_operator,
        run_median_filter, run_canny_detector,
        # lab 3
        stretch_histogram_operation, threshold_preserve_gray_user, otsu, run_adaptive_threshold,
        run_morphological_operations, run_skeletonization, designation, run_grabcut)

    globals_var.root.mainloop()