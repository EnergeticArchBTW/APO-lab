from tkinter import Tk, Menu

class MainMenu(Tk):
    def __init__(self, open_callback, save_callback, duplicate_callback):
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
        file_menu.add_separator()
        file_menu.add_command(label="Wyjdź", command=self.quit)
        menubar.add_cascade(label="Lab 1", menu=file_menu)