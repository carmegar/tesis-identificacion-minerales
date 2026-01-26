"""
Script para descargar espectros EDS de Simon Fraser University (SFU) - v2
Intenta múltiples variaciones de nombres de archivo
"""

import os
import urllib.request
import time
from pathlib import Path

BASE_URL = "https://www.sfu.ca/~marshall/sem/"

# Lista de minerales con múltiples posibles nombres de archivo
MINERALES_SFU = [
    # SILICATOS
    ("Adularia", ["adul.jpg", "Adularia.jpg", "adularia.jpg"]),
    ("Albite", ["albite.jpg", "Albite.jpg"]),
    ("Almandine", ["Almandine.jpg", "almandine.jpg", "alm.jpg"]),
    ("Andalusite", ["andradite.jpg", "Andalusite.jpg", "andalusite.jpg"]),
    ("Anorthite", ["an1.jpg", "Anorthite.jpg", "anorthite.jpg"]),
    ("Anorthoclase", ["anorthoclase.jpg", "Anorthoclase.jpg"]),
    ("Augite", ["augite.jpg", "Augite.jpg", "aug.jpg"]),
    ("Axinite", ["axinite.jpg", "Axinite.jpg"]),
    ("Benitoite", ["Ben2.jpg", "benitoite.jpg", "Benitoite.jpg"]),
    ("Beryl", ["beryl.jpg", "Beryl.jpg"]),
    ("Biotite", ["Bio.jpg", "bio.jpg", "Biotite.jpg", "biotite.jpg"]),
    ("Chlorite", ["Chl.jpg", "chl.jpg", "Chlorite.jpg", "chlorite.jpg"]),
    ("Chloritoid", ["Chloritoid.jpg", "chloritoid.jpg"]),
    ("Cordierite", ["Cordierite.jpg", "cordierite.jpg", "cord.jpg"]),
    ("Diopside", ["Dio6.jpg", "diopside.jpg", "Diopside.jpg", "dio.jpg"]),
    ("Epidote", ["epi.jpg", "Epidote.jpg", "epidote.jpg"]),
    ("Fayalite", ["Olivine.jpg", "fayalite.jpg", "Fayalite.jpg"]),
    ("Forsterite", ["forsterite.jpg", "Forsterite.jpg", "fo.jpg"]),
    ("Glaucophane", ["Glaucophane.jpg", "glaucophane.jpg", "glauc.jpg"]),
    ("Grandidierite", ["Grandidierite.jpg", "grandidierite.jpg"]),
    ("Hornblende", ["hbl.jpg", "Hornblende.jpg", "hornblende.jpg"]),
    ("Hypersthene", ["hypersthene.jpg", "Hypersthene.jpg", "hyp.jpg"]),
    ("Jadeite", ["Jadeite.jpg", "jadeite.jpg", "jade.jpg"]),
    ("Kornerupine", ["Kornerupine.jpg", "kornerupine.jpg"]),
    ("Muscovite", ["Muscovite.jpg", "muscovite.jpg", "mus.jpg", "musc.jpg"]),
    ("Osumilite", ["osumilite.jpg", "Osumilite.jpg"]),
    ("Paragonite", ["Paragonite.jpg", "paragonite.jpg"]),
    ("Phlogopite", ["fph2.jpg", "Phlogopite.jpg", "phlogopite.jpg"]),
    ("Plagioclase", ["Plag1.jpg", "plagioclase.jpg", "Plagioclase.jpg"]),
    ("Pyrope", ["pyropeG10.jpg", "Pyrope.jpg", "pyrope.jpg"]),
    ("Sapphirine", ["Sapphirine.jpg", "sapphirine.jpg"]),
    ("Scapolite", ["scapolite.jpg", "Scapolite.jpg"]),
    ("Sillimanite", ["Sillimanite.jpg", "sillimanite.jpg", "sill.jpg"]),
    ("Staurolite", ["Staurolite.jpg", "staurolite.jpg", "stau.jpg"]),
    ("Stilpnomelane", ["Stilpnomelane.jpg", "stilpnomelane.jpg"]),
    ("Titanite", ["Titanite.jpg", "titanite.jpg", "tit.jpg"]),
    ("Tremolite", ["Tre1.jpg", "tremolite.jpg", "Tremolite.jpg"]),
    ("Tourmaline", ["tur.jpg", "Tourmaline.jpg", "tourmaline.jpg"]),
    ("Topaz", ["Topaz.jpg", "topaz.jpg"]),
    ("Vesuvianite", ["vesuvianite.jpg", "Vesuvianite.jpg"]),
    ("Willemite", ["willemite.jpg", "Willemite.jpg"]),
    ("Wollastonite", ["Woll.jpg", "wollastonite.jpg", "Wollastonite.jpg"]),
    ("Zircon", ["zircon.jpg", "Zircon.jpg"]),

    # SULFUROS
    ("Arsenopyrite", ["apy.jpg", "Arsenopyrite.jpg", "arsenopyrite.jpg"]),
    ("Bismuthinite", ["Bismuthinite.jpg", "bismuthinite.jpg"]),
    ("Bornite", ["Bornite.jpg", "bornite.jpg"]),
    ("Chalcocite", ["chalcocite.jpg", "Chalcocite.jpg"]),
    ("Chalcopyrite", ["cpy.jpg", "Chalcopyrite.jpg", "chalcopyrite.jpg"]),
    ("Covellite", ["CuS.jpg", "covellite.jpg", "Covellite.jpg"]),
    ("Enargite", ["ena.jpg", "Enargite.jpg", "enargite.jpg"]),
    ("Galena", ["galena.jpg", "Galena.jpg"]),
    ("Pyrrhotite", ["FeS.jpg", "pyrrhotite.jpg", "Pyrrhotite.jpg", "po.jpg"]),
    ("Pyrite", ["FeS2.jpg", "pyrite.jpg", "Pyrite.jpg", "py.jpg"]),
    ("Sphalerite", ["ZnS.jpg", "sphalerite.jpg", "Sphalerite.jpg"]),
    ("Stibnite", ["stibnite.jpg", "Stibnite.jpg"]),
    ("Stromeyerite", ["Stromeyerite.jpg", "stromeyerite.jpg"]),

    # SULFATOS
    ("Barite", ["barite.jpg", "Barite.jpg"]),
    ("Celestite", ["Celes.jpg", "celestite.jpg", "Celestite.jpg"]),

    # OXIDOS
    ("Brannerite", ["brannerite.jpg", "Brannerite.jpg"]),
    ("Corundum", ["Corundum.jpg", "corundum.jpg"]),
    ("Chromite", ["Chromite.jpg", "chromite.jpg", "chr.jpg"]),
    ("Spinel", ["Spinel.jpg", "spinel.jpg"]),
    ("Hematite", ["Hematite.jpg", "hematite.jpg", "hem.jpg"]),
    ("Ilmenite", ["ilmenite.jpg", "Ilmenite.jpg", "ilm.jpg"]),
    ("MnTiO3", ["MnTiO3.jpg"]),

    # CARBONATOS
    ("Ankerite", ["Ankerite.jpg", "ankerite.jpg"]),
    ("Calcite", ["cal.jpg", "Calcite.jpg", "calcite.jpg"]),
    ("Dolomite", ["Dolo.jpg", "dolomite.jpg", "Dolomite.jpg"]),
    ("Rhodochrosite", ["Rhodochrosite.jpg", "rhodochrosite.jpg"]),

    # FOSFATOS
    ("Apatite", ["Apa.jpg", "apatite.jpg", "Apatite.jpg"]),
    ("Beryllonite", ["bep.jpg", "Beryllonite.jpg", "beryllonite.jpg"]),
    ("Monazite", ["monazite.jpg", "Monazite.jpg"]),
    ("Turquoise", ["Turquoise.jpg", "turquoise.jpg"]),

    # TUNGSTATOS
    ("Scheelite", ["Scheelite.jpg", "scheelite.jpg"]),
    ("Wolframite", ["Wolframite.jpg", "wolframite.jpg"]),
    ("Wulfenite", ["Wulfenite.jpg", "wulfenite.jpg"]),

    # ARSENIUROS
    ("Nickeline", ["NiAs.jpg", "nickeline.jpg", "Nickeline.jpg"]),

    # METALES
    ("Ag80Au20", ["Ag80Au20.jpg"]),
    ("Au80Ag20", ["Au80Ag20.jpg"]),
    ("Bismuth", ["Bismuth.jpg", "bismuth.jpg"]),
]

def download_spectra(output_dir: str = "espectros_externos/SFU"):
    """Descarga todos los espectros EDS de SFU."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = []

    print(f"Descargando {len(MINERALES_SFU)} espectros EDS de SFU...")
    print(f"Destino: {output_path.absolute()}\n")

    for mineral, variantes in MINERALES_SFU:
        filename = f"EDS_{mineral}.jpg"
        filepath = output_path / filename

        if filepath.exists():
            print(f"[SKIP] {mineral}")
            downloaded += 1
            continue

        success = False
        for variante in variantes:
            url = BASE_URL + variante
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = response.read()
                    with open(filepath, 'wb') as f:
                        f.write(data)
                    print(f"[OK]   {mineral} ({variante}, {len(data)//1024}KB)")
                    downloaded += 1
                    success = True
                    time.sleep(0.3)
                    break
            except:
                continue

        if not success:
            print(f"[FAIL] {mineral}")
            failed.append(mineral)

    print(f"\n{'='*50}")
    print(f"Descargados: {downloaded}/{len(MINERALES_SFU)}")
    print(f"Fallidos: {len(failed)}")
    if failed:
        print(f"No encontrados: {', '.join(failed)}")

    return downloaded, failed

if __name__ == "__main__":
    download_spectra()
