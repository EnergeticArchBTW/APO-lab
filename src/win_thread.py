import time # do opóźnień

"""Wątek monitorujący stan okna danego obrazu."""

def win_thread(win):
    """Wątek monitorujący stan okna Tkinter."""
    while True:
        time.sleep(1)  # sprawdzaj co sekundę
        if not win.winfo_exists():
            print("Okno zostało zamknięte")
            break