# APO-lab

Aplikacja do przetwarzania i analizy obrazów realizowana w ramach laboratoriów APO.

## Wymagania

* **Python:** 3.8+
* **Biblioteki:** `opencv-python`, `Pillow`, `numpy`
* **Interfejs:** `tkinter` (standardowa biblioteka Pythona)

## Instalacja i uruchomienie

### 1. Przygotowanie środowiska
Sklonuj repozytorium
```text
git clone https://github.com/EnergeticArchBTW/APO-lab.git

```

### 2. Konfiguracja (Windows)

Otwórz terminal w folderze projektu:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

```

### 3. Konfiguracja (Linux - Ubuntu/Debian)

Wymagane jest doinstalowanie pakietu systemowego dla GUI:

```bash
sudo apt update
sudo apt install python3-tk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

```

---

## Zestawienie technologii

| Technologia | Zastosowanie |
| --- | --- |
| **OpenCV (cv2)** | Przetwarzanie sygnałów, operacje na macierzach obrazu. |
| **Tkinter** | Obsługa GUI, okna `Toplevel`, tablice LUT, dialogi systemowe. |
| **Pillow (PIL)** | Konwersja formatów i renderowanie podglądu w GUI. |
| **NumPy** | Niskopoziomowe operacje na pikselach. |
| **Pathlib** | Zarządzanie ścieżkami plików niezależnie od systemu operacyjnego. |