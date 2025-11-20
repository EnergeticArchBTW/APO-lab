import cv2
import os
from pathlib import Path

""" osobny plik oddzielony od całego programu, który przerabia kolorowy obraz na monochromatyczny """

def convert_to_grayscale_and_save(input_path, output_path=None):
    # Wczytaj obraz jako kolorowy
    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(f"Nie można wczytać obrazu: {input_path}")

    # Konwersja do skali szarości, jeśli trzeba
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 2:
        image_gray = image.copy()
    else:
        raise ValueError("Nieznany format obrazu")

    # Domyślna ścieżka zapisu
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_gray{ext}"

    # Zapis obrazu
    cv2.imwrite(output_path, image_gray)
    print(f"Zapisano obraz grayscale do: {output_path}")

    return image_gray

img = convert_to_grayscale_and_save("C://Users//Michal//Desktop//APO-Projekt//data//images//przecinek.png")
"""
folder_path_obj = Path("C://Users//Michal//Desktop//APO-Projekt//data//images//projekt//2_przyklad")

for obraz in folder_path_obj.iterdir():
    if obraz.is_file():
        convert_to_grayscale_and_save(str(obraz))
"""