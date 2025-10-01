from menu import MainMenu # plik main.py definiuje listę rozwijaną
from lab1 import * 
import threading # do wielowątkowości
import time # do opóźnień

if __name__ == "__main__":
    # Tworzymy folder outputs, jeśli nie istnieje
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # threading.Thread(target=show_focused_number, daemon=True).start()
    menu = MainMenu(open_and_show_image, save_image, duplicate_focused_image)
    menu.mainloop()