import cv2  # biblioteka do wczytywania/zapisu obrazów
import matplotlib.pyplot as plt  # do wyświetlania obrazów
from pathlib import Path  # do pracy ze ścieżkami

# Ścieżki do folderów
#DATA_DIR = Path("../data/images")
DATA_DIR = Path(__file__).parent.parent / "data" / "images"
#OUTPUT_DIR = Path("../outputs")
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Tworzymy folder outputs, jeśli nie istnieje
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_image(filename):
    """Wczytuje obraz z folderu data/images."""
    img_path = DATA_DIR / filename
    image = cv2.imread(str(img_path))
    if image is None:
        raise FileNotFoundError(f"Nie znaleziono pliku: {img_path}")
    return image

def show_image(image, title="Podgląd obrazu"):
    """Wyświetla obraz w oknie matplotlib (RGB)."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # konwersja BGR -> RGB
    plt.imshow(image_rgb)
    plt.title(title)
    plt.axis("off")
    plt.show()

def save_copy(image, filename):
    """Zapisuje kopię obrazu do folderu outputs/."""
    out_path = OUTPUT_DIR / filename
    cv2.imwrite(str(out_path), image)
    print(f"Zapisano kopię obrazu w: {out_path}")

if __name__ == "__main__":
    # przykład użycia
    test_file = "example.jpg"  # wrzuć plik do data/images/

    # 1. Wczytaj
    img = load_image(test_file)

    # 2. Wyświetl
    show_image(img, "Oryginalny obraz")

    # 3. Zapisz kopię
    save_copy(img, "example_copy.jpg")
