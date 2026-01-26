"""
Script para descargar espectros EDS de Simon Fraser University (SFU)
Fuente: https://www.sfu.ca/~marshall/sem/mineral.htm
"""

import os
import urllib.request
import time
from pathlib import Path

# Base URL de SFU
BASE_URL = "https://www.sfu.ca/~marshall/sem/"

# Lista de minerales con sus archivos de imagen (nombre_mineral, archivo_imagen)
# Extraído de https://www.sfu.ca/~marshall/sem/mineral.htm
MINERALES_SFU = [
    # SILICATOS
    ("Adularia", "adul.jpg"),
    ("Albite", "albite.jpg"),
    ("Almandine", "Almandine.jpg"),
    ("Andalusite", "andradite.jpg"),
    ("Anorthite", "an1.jpg"),
    ("Anorthoclase", "anorthoclase.jpg"),
    ("Augite", "augite.jpg"),
    ("Axinite", "axinite.jpg"),
    ("Benitoite", "Ben2.jpg"),
    ("Beryl", "beryl.jpg"),
    ("Biotite", "Bio.jpg"),
    ("Chlorite", "Chl.jpg"),
    ("Chloritoid", "Chloritoid.jpg"),
    ("Cordierite", "Cordierite.jpg"),
    ("Diopside", "Dio6.jpg"),
    ("Epidote", "epi.jpg"),
    ("Fayalite", "Olivine.jpg"),
    ("Forsterite", "forsterite.jpg"),
    ("Glaucophane", "Glaucophane.jpg"),
    ("Grandidierite", "Grandidierite.jpg"),
    ("Hornblende", "hbl.jpg"),
    ("Hypersthene", "hypersthene.jpg"),
    ("Jadeite", "Jadeite.jpg"),
    ("Kornerupine", "Kornerupine.jpg"),
    ("Muscovite", "Muscovite.jpg"),
    ("Osumilite", "osumilite.jpg"),
    ("Paragonite", "Paragonite.jpg"),
    ("Phlogopite", "fph2.jpg"),
    ("Plagioclase", "Plag1.jpg"),
    ("Pyrope_G10", "pyropeG10.jpg"),
    ("Sapphirine", "Sapphirine.jpg"),
    ("Scapolite", "scapolite.jpg"),
    ("Sillimanite", "Sillimanite.jpg"),
    ("Staurolite", "Staurolite.jpg"),
    ("Stilpnomelane", "Stilpnomelane.jpg"),
    ("Titanite", "Titanite.jpg"),
    ("Tremolite", "Tre1.jpg"),
    ("Tourmaline", "tur.jpg"),
    ("Topaz", "Topaz.jpg"),
    ("Vesuvianite", "vesuvianite.jpg"),
    ("Willemite", "willemite.jpg"),
    ("Wollastonite", "Woll.jpg"),
    ("Zircon", "zircon.jpg"),

    # SULFUROS
    ("Arsenopyrite", "apy.jpg"),
    ("Bismuthinite", "Bismuthinite.jpg"),
    ("Bornite", "Bornite.jpg"),
    ("Chalcocite", "chalcocite.jpg"),
    ("Chalcopyrite", "cpy.jpg"),
    ("Covellite", "CuS.jpg"),
    ("Enargite", "ena.jpg"),
    ("Galena", "galena.jpg"),
    ("Pyrrhotite", "FeS.jpg"),
    ("Pyrite", "FeS2.jpg"),
    ("Sphalerite", "ZnS.jpg"),
    ("Stibnite", "stibnite.jpg"),
    ("Stromeyerite", "Stromeyerite.jpg"),

    # SULFATOS
    ("Barite", "barite.jpg"),
    ("Celestite", "Celes.jpg"),

    # OXIDOS
    ("Brannerite", "brannerite.jpg"),
    ("Corundum", "Corundum.jpg"),
    ("Chromite", "Chromite.jpg"),
    ("Spinel", "Spinel.jpg"),
    ("Hematite", "Hematite.jpg"),
    ("Ilmenite", "ilmenite.jpg"),
    ("MnTiO3", "MnTiO3.jpg"),

    # CARBONATOS
    ("Ankerite", "Ankerite.jpg"),
    ("Calcite", "cal.jpg"),
    ("Dolomite", "Dolo.jpg"),
    ("Rhodochrosite", "Rhodochrosite.jpg"),

    # FOSFATOS
    ("Apatite", "Apa.jpg"),
    ("Beryllonite", "bep.jpg"),
    ("Monazite", "monazite.jpg"),
    ("Turquoise", "Turquoise.jpg"),

    # TUNGSTATOS
    ("Scheelite", "Scheelite.jpg"),
    ("Wolframite", "Wolframite.jpg"),
    ("Wulfenite", "Wulfenite.jpg"),

    # ARSENIUROS
    ("Nickeline", "NiAs.jpg"),

    # METALES/ALEACIONES
    ("Ag80Au20", "Ag80Au20.jpg"),
    ("Au80Ag20", "Au80Ag20.jpg"),
    ("Bismuth", "Bismuth.jpg"),
]

def download_spectra(output_dir: str = "espectros_externos/SFU"):
    """Descarga todos los espectros EDS de SFU."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = []

    print(f"Iniciando descarga de {len(MINERALES_SFU)} espectros EDS...")
    print(f"Destino: {output_path.absolute()}\n")

    for mineral, imagen in MINERALES_SFU:
        url = BASE_URL + imagen
        filename = f"EDS_{mineral}.jpg"
        filepath = output_path / filename

        # Si ya existe, saltar
        if filepath.exists():
            print(f"[SKIP] {mineral} - ya existe")
            downloaded += 1
            continue

        try:
            print(f"[GET]  {mineral}...", end=" ")

            # Configurar request con User-Agent
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()

                with open(filepath, 'wb') as f:
                    f.write(data)

                print(f"OK ({len(data)//1024} KB)")
                downloaded += 1

            # Pequeña pausa para no sobrecargar el servidor
            time.sleep(0.5)

        except Exception as e:
            print(f"ERROR: {e}")
            failed.append((mineral, str(e)))

    print(f"\n{'='*50}")
    print(f"Descarga completada:")
    print(f"  - Exitosos: {downloaded}/{len(MINERALES_SFU)}")
    print(f"  - Fallidos: {len(failed)}")

    if failed:
        print(f"\nMinerales con error:")
        for mineral, error in failed:
            print(f"  - {mineral}: {error}")

    return downloaded, failed


if __name__ == "__main__":
    import sys

    output_dir = "espectros_externos/SFU"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    download_spectra(output_dir)
