import numpy as np
import pandas as pd
from geometry import load_surfaces, load_obstacles
from mapping import map_surface_to_RE2020
from irradiance import irradiance_surface_RE2020

# ======================
# 1. Loading data
# ======================

meteo = pd.read_csv("meteo_Trappes.csv", sep=';')
surfaces_df = load_surfaces("surfaces.csv")
obstacles = load_obstacles("obstacles.csv")

# ======================
# 2. Geometric mapping → RE2020 parameters
# ======================

surfaces_RE2020 = []

for _, row in surfaces_df.iterrows():
    surface = {
        "id": row.id,
        "center": np.array([row.cx, row.cy, row.cz]),
        "normal": np.array([row.nx, row.ny, row.nz]),
        "vertices": np.array(
            list(map(float, row.vertices.split(";")))
        ).reshape(-1, 3)
    }
    params = map_surface_to_RE2020(surface, obstacles)
    params["id"] = row.id
    surfaces_RE2020.append(params)

print(f"{len(surfaces_RE2020)} RE2020 mapped surfaces")

# ======================
# 3. RE2020 temporal loop
# ======================

results = []
total = len(meteo) * len(surfaces_RE2020)
counter = 0

for _, m in meteo.iterrows():
    gamma = np.deg2rad(m.gamma)
    psi = np.deg2rad(m.psi)

    IDn = m.DNI
    Idi = m.DHI
    IDh = IDn * np.sin(gamma)

    for surf in surfaces_RE2020:
        E, FfDir = irradiance_surface_RE2020(
            surface=surf,
            IDn=IDn,
            Idi=Idi,
            IDh=IDh,
            gamma=gamma,
            psi=psi
        )

        results.append({
            "time": m.time,
            "surface_id": surf["id"],
            "irradiance_W": round(E, 2),
            "FfDir": round(FfDir, 4)
        })

        counter += 1
        if counter % 2000 == 0:
            print(f"Progress: {counter}/{total} ({counter/total*100:.1f}%)")

# ======================
# 4. Export CSV
# ======================

pd.DataFrame(results).to_csv("irradiance_RE2020.csv", index=False)
print("RE2020 calculation completed – irradiance_RE2020.csv file generated")
