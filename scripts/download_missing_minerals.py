"""
Script para descargar minerales EDS faltantes de SFU y otras fuentes.
Enfocado en minerales que causan errores de validacion.
"""

import os
import urllib.request
import time
from pathlib import Path

BASE_URL_SFU = "https://www.sfu.ca/~marshall/sem/"

# Minerales que necesitamos para mejorar accuracy
# (minerales que estan en test pero no en BD)
MINERALES_FALTANTES = [
    # Celestite/Celestina - disponible en SFU
    ("Celestite", [
        "Celes.jpg", "celestite.jpg", "Celestite.jpg",
        "celestine.jpg", "Celestine.jpg", "cel.jpg"
    ]),
    # Quartz para Amatista (amatista = cuarzo morado)
    ("Quartz", [
        "qtz.jpg", "Quartz.jpg", "quartz.jpg",
        "SiO2.jpg", "silica.jpg"
    ]),
    # Magnetite (ya tenemos, pero verificar)
    ("Magnetite", [
        "mag.jpg", "Magnetite.jpg", "magnetite.jpg",
        "Fe3O4.jpg"
    ]),
    # Gahnite (espinela de zinc)
    ("Gahnite", [
        "gahnite.jpg", "Gahnite.jpg", "gah.jpg"
    ]),
    # Otros silicatos utiles
    ("Almandine", ["alm.jpg", "Almandine.jpg", "almandine.jpg"]),
    ("Diopside", ["Dio6.jpg", "diopside.jpg", "dio.jpg"]),
    ("Forsterite", ["forsterite.jpg", "Forsterite.jpg", "fo.jpg"]),
    ("Hypersthene", ["hypersthene.jpg", "hyp.jpg"]),
    ("Jadeite", ["Jadeite.jpg", "jadeite.jpg"]),
    ("Tremolite", ["Tre1.jpg", "tremolite.jpg"]),
    ("Wollastonite", ["Woll.jpg", "wollastonite.jpg"]),
    # Carbonatos
    ("Dolomite", ["Dolo.jpg", "dolomite.jpg"]),
    ("Rhodochrosite", ["Rhodochrosite.jpg", "rhodochrosite.jpg"]),
    # Sulfuros
    ("Arsenopyrite", ["apy.jpg", "Arsenopyrite.jpg"]),
    ("Bismuthinite", ["Bismuthinite.jpg", "bismuthinite.jpg"]),
    # Otros
    ("Apatite", ["Apa.jpg", "apatite.jpg"]),
    ("Turquoise", ["Turquoise.jpg", "turquoise.jpg"]),
    ("Scheelite", ["Scheelite.jpg", "scheelite.jpg"]),
    ("Wolframite", ["Wolframite.jpg", "wolframite.jpg"]),
    ("Chromite", ["Chromite.jpg", "chr.jpg"]),
    ("Brannerite", ["brannerite.jpg", "Brannerite.jpg"]),
]


def download_mineral(mineral_name: str, variantes: list, output_dir: Path) -> bool:
    """Intenta descargar un mineral de SFU."""
    filename = f"EDS_{mineral_name}.jpg"
    filepath = output_dir / filename

    if filepath.exists():
        print(f"  [EXISTE] {mineral_name}")
        return True

    for variante in variantes:
        url = BASE_URL_SFU + variante
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                if len(data) > 1000:  # Verificar que no es error HTML
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    print(f"  [OK] {mineral_name} <- {variante} ({len(data)//1024}KB)")
                    return True
        except Exception as e:
            continue

    print(f"  [FAIL] {mineral_name}")
    return False


def main():
    print("="*60)
    print("DESCARGANDO MINERALES FALTANTES DE SFU")
    print("="*60)

    output_dir = Path("espectros_externos/SFU")
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = []

    for mineral, variantes in MINERALES_FALTANTES:
        success = download_mineral(mineral, variantes, output_dir)
        if success:
            downloaded += 1
        else:
            failed.append(mineral)
        time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"Nuevos descargados: {downloaded}")
    print(f"No encontrados: {len(failed)}")
    if failed:
        print(f"Fallidos: {', '.join(failed)}")
    print("="*60)

    return downloaded, failed


if __name__ == "__main__":
    main()
