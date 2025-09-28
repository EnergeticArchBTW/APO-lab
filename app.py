import tkinter as tk
from tkinter import filedialog, messagebox

class AplikacjaOkienkowa:
    def __init__(self):
        # Tworzenie głównego okna
        self.root = tk.Tk()
        self.root.title("Moja Aplikacja")
        self.root.geometry("600x400")
        
        # Tworzenie paska menu
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Tworzenie menu "Plik"
        self.menu_plik = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Plik", menu=self.menu_plik)
        
        # Dodawanie opcji "Otwórz" do menu Plik
        self.menu_plik.add_command(label="Otwórz", command=self.otworz_plik)
        
        # Opcjonalnie: dodanie separatora i opcji Wyjście
        self.menu_plik.add_separator()
        self.menu_plik.add_command(label="Wyjście", command=self.root.quit)
    
    def otworz_plik(self):
        """Funkcja obsługująca wybór i otwieranie pliku"""
        # Otwieranie okna dialogowego wyboru pliku
        sciezka_pliku = filedialog.askopenfilename(
            title="Wybierz plik",
            filetypes=[
                ("Pliki tekstowe", "*.txt"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        
        # Jeśli użytkownik wybrał plik
        if sciezka_pliku:
            try:
                # Próba odczytania pliku
                with open(sciezka_pliku, 'r', encoding='utf-8') as plik:
                    zawartosc = plik.read()
                
                # Wyświetlenie zawartości w polu tekstowym
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, zawartosc)
                
                # Aktualizacja tytułu okna
                self.root.title(f"Moja Aplikacja - {sciezka_pliku}")
                
            except Exception as e:
                # Obsługa błędów przy otwieraniu pliku
                messagebox.showerror(
                    "Błąd", 
                    f"Nie można otworzyć pliku:\n{str(e)}"
                )
    
    def uruchom(self):
        """Uruchamianie aplikacji"""
        self.root.mainloop()

# Tworzenie i uruchamianie aplikacji
if __name__ == "__main__":
    aplikacja = AplikacjaOkienkowa()
    aplikacja.uruchom()