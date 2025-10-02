import time # do opóźnień
import globals_var

"""Wątek monitorujący stan okna danego obrazu."""

def win_thread(win):
    """Wątek monitorujący stan okna Tkinter."""
    last_focus = None
    while True:
        if not win.winfo_exists():
            print("Okno zostało zamknięte")
            # usuń z słownika
            if win in globals_var.opened_images:
                del globals_var.opened_images[win]
            # Jeśli zamykane okno było aktywne, wyczyść current_window
            if globals_var.current_window == win:
                globals_var.current_window = None
            break
        # sprawdzaj focus
        try:
            is_focused = (win.focus_displayof() == win)
        except Exception:
            is_focused = False
        if is_focused != last_focus:
            last_focus = is_focused
            if is_focused:
                globals_var.current_window = win
        time.sleep(0.05)  # bardzo krótka przerwa, praktycznie nieodczuwalna