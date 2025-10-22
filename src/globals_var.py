from pathlib import Path  # do pracy ze ścieżkami
import numpy as np
from lab2 import *

"""Moduł z globalnymi zmiennymi dla aplikacji."""

opened_images = {}      # słownik: okno -> {"id": ..., "image": ..., "filename": ...}
current_id = 0       # licznik unikalnych ID dla okien
current_window = None   # wskaźnik na aktualnie aktywne okno
root = None             # główne okno aplikacji

# Ścieżki do folderów
DATA_DIR = Path(__file__).parent.parent / "data" / "images"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

#----------- Baza danych masek kerneli (lab 2) --------------
# --- MASKI WYGŁADZAJĄCE ---
KERNEL_AVG = np.array([[1, 1, 1], 
                       [1, 1, 1], 
                       [1, 1, 1]], dtype=np.float32) / 9.0

# Z wykładu - uśrednianie z wagami to "krzyż"
KERNEL_WEIGHTED_AVG = np.array([[0, 1, 0], 
                              [1, 1, 1], 
                              [0, 1, 0]], dtype=np.float32) / 5.0

# --- MASKI WYOSTRZAJĄCE (LAPLASJANY) ---
# (Sprawdź dokładne wartości na slajdach)
KERNEL_LAPLACIAN_1 = np.array([[0, 1, 0], 
                             [1,  -4, 1], 
                             [0, 1, 0]], dtype=np.float32)

KERNEL_LAPLACIAN_2 = np.array([[-1, -1, -1], 
                             [-1,  8, -1], 
                             [-1, -1, -1]], dtype=np.float32)

KERNEL_LAPLACIAN_3 = np.array([[-1, 2, -1], 
                             [2,  -4, 2], 
                             [-1, 2, -1]], dtype=np.float32) # Przykładowa

# --- MASKI PREWITTA (KIERUNKOWE) ---
KERNEL_PREWITT_E = np.array([[-1, 0, 1], 
                           [-1, 0, 1], 
                           [-1, 0, 1]], dtype=np.float32)

KERNEL_PREWITT_NE = np.array([[-1, -1, 0], 
                            [-1,  0, 1], 
                            [ 0,  1, 1]], dtype=np.float32)

KERNEL_PREWITT_N  = np.array([[ 1,  1,  1],
                              [ 0,  0,  0],
                              [-1, -1, -1]], dtype=np.float32)

KERNEL_PREWITT_NW = np.array([[ 0,  1,  1],
                              [-1,  0,  1],
                              [-1, -1,  0]], dtype=np.float32)

KERNEL_PREWITT_W  = np.array([[ 1,  0, -1],
                              [ 1,  0, -1],
                              [ 1,  0, -1]], dtype=np.float32)

KERNEL_PREWITT_SW = np.array([[ 1,  1,  0],
                              [ 1,  0, -1],
                              [ 0, -1, -1]], dtype=np.float32)

KERNEL_PREWITT_S  = np.array([[-1, -1, -1],
                              [ 0,  0,  0],
                              [ 1,  1,  1]], dtype=np.float32)

KERNEL_PREWITT_SE = np.array([[ 0, -1, -1],
                              [ 1,  0, -1],
                              [ 1,  1,  0]], dtype=np.float32)
# -------------------------------------------------------

# Słownik mapujący nazwy wyświetlane na funkcje i kernele dla funkcji show_filter_selection_window() z lab2.py
FILTER_MAP = {
    # Wygładzanie
    "Wygładzanie: Uśredniające": {
        "func": menu_smooth_avg, 
        "kernel": globals_var.KERNEL_AVG
    },
    "Wygładzanie: Ważone (Krzyż)": {
        "func": menu_smooth_weighted, 
        "kernel": globals_var.KERNEL_WEIGHTED_AVG
    },
    
    # Wyostrzanie
    "Wyostrzanie: Laplasjan 1 (4)": {
        "func": menu_sharpen_lap1,
        "kernel": globals_var.KERNEL_LAPLACIAN_1
    },
    "Wyostrzanie: Laplasjan 2 (8)": {
        "func": menu_sharpen_lap2,
        "kernel": globals_var.KERNEL_LAPLACIAN_2
    },
    "Wyostrzanie: Laplasjan 3 (diagonalny)": {
        "func": menu_sharpen_lap3,
        "kernel": globals_var.KERNEL_LAPLACIAN_3
    },

    # Prewitt
    "Kierunkowy: Prewitt E (Wschód)": {
        "func": menu_prewitt_e,
        "kernel": globals_var.KERNEL_PREWITT_E
    },
    "Kierunkowy: Prewitt NE (Płn-Wschód)": {
        "func": menu_prewitt_ne,
        "kernel": globals_var.KERNEL_PREWITT_NE
    },
    "Kierunkowy: Prewitt N (Północ)": {
        "func": menu_prewitt_n,
        "kernel": globals_var.KERNEL_PREWITT_N
    },
    "Kierunkowy: Prewitt NW (Płn-Zachód)": {
        "func": menu_prewitt_nw,
        "kernel": globals_var.KERNEL_PREWITT_NW
    },
    "Kierunkowy: Prewitt W (Zachód)": {
        "func": menu_prewitt_w,
        "kernel": globals_var.KERNEL_PREWITT_W
    },
    "Kierunkowy: Prewitt SW (Płd-Zachód)": {
        "func": menu_prewitt_sw,
        "kernel": globals_var.KERNEL_PREWITT_SW
    },
    "Kierunkowy: Prewitt S (Południe)": {
        "func": menu_prewitt_s,
        "kernel": globals_var.KERNEL_PREWITT_S
    },
    "Kierunkowy: Prewitt SE (Płd-Wschód)": {
        "func": menu_prewitt_se,
        "kernel": globals_var.KERNEL_PREWITT_SE
    },
}