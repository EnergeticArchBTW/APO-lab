from pathlib import Path  # do pracy ze ścieżkami

"""Moduł z globalnymi zmiennymi dla aplikacji."""

opened_images = {}      # słownik: okno -> {"id": ..., "image": ..., "filename": ...}
current_id = 0       # licznik unikalnych ID dla okien
current_window = None   # wskaźnik na aktualnie aktywne okno

# Ścieżki do folderów
DATA_DIR = Path(__file__).parent.parent / "data" / "images"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"