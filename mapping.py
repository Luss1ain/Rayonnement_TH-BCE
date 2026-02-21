import numpy as np
from geometry import (
    azimuth_from_normal,
    inclination_from_normal,
    surface_dimensions,
    min_distance
)

# ==========================
# Classification obstacles
# ==========================

def classify_obstacles(surface, obstacles, d_seuil=500.0):
    proches, lointains = [], []

    for obs in obstacles:
        d = min_distance(surface["center"], obs["vertices"])
        if d < d_seuil:
            proches.append(obs)
        else:
            lointains.append(obs)

    return proches, lointains

# ==========================
# Masques proches verticaux
# ==========================

def vertical_masks(surface, obstacles):
    alpha = surface["alpha"]
    center = surface["center"]

    vd = None
    vg = None

    for obs in obstacles:
        obs_center = obs["vertices"].mean(axis=0)
        rel = obs_center - center

        phi = np.arctan2(rel[0], rel[1]) - alpha
        dist_h = np.linalg.norm(rel[:2])
        if dist_h < 1e-3:
            continue

        depth = np.max(
            np.linalg.norm(obs["vertices"][:, :2] - center[:2], axis=1)
        )

        if phi >= 0:
            vd = {"dvd": depth, "dpd": dist_h}
        else:
            vg = {"dvg": depth, "dpg": dist_h}

    return vd, vg

# ==========================
# Masque proche horizontal
# ==========================

def horizontal_mask(surface, obstacles):
    zc = surface["center"][2]
    hpb = surface["hpb"]

    dhm = None
    dhp = None

    for obs in obstacles:
        zmin = obs["vertices"][:, 2].min()
        if zmin > zc:
            dhm = zmin - zc
            dhp = hpb / 2.0
            break

    if dhm is None:
        return None

    return {"dhm": dhm, "dhp": dhp}

# ==========================
# Masques lointains E_AZ
# ==========================

def azimuthal_horizon(surface, obstacles, n_az=36):
    center = surface["center"]
    gammas = np.zeros(n_az)

    for i in range(n_az):
        az = 2.0 * np.pi * i / n_az
        max_gamma = 0.0

        for obs in obstacles:
            rel = obs["vertices"] - center
            horiz = np.linalg.norm(rel[:, :2], axis=1)
            vert = rel[:, 2]

            valid = horiz > 1e-3
            if not np.any(valid):
                continue

            gamma = np.arctan2(vert[valid], horiz[valid])
            max_gamma = max(max_gamma, gamma.max(initial=0.0))

        gammas[i] = max_gamma

    return gammas.tolist()

# ==========================
# Mapping surface → RE2020
# ==========================

def map_surface_to_RE2020(surface, obstacles):
    proches, lointains = classify_obstacles(surface, obstacles)
    
    alpha = azimuth_from_normal(surface["normal"])
    beta = inclination_from_normal(surface["normal"])
    lpb, hpb = surface_dimensions(surface["vertices"])

    # Initialisation des paramètres de masque
    res = {
        "alpha": alpha,
        "beta": beta,
        "lpb": lpb,
        "hpb": hpb,
        "vd_phi": None,
        "vg_phi": None,
        "h_alt": None,
        "E_AZ": None,
        "Id_masque": []
    }

    for obs in proches:
        rel = obs["vertices"].mean(axis=0) - surface["center"]
        # Angle relatif horizontal : si > 0 c'est à droite, si < 0 c'est à gauche
        phi = np.arctan2(rel[0], rel[1]) - alpha
        
        # On normalise l'angle entre -pi et pi
        phi = (phi + np.pi) % (2 * np.pi) - np.pi
        
        dist_h = np.linalg.norm(rel[:2])
        alt = np.arctan2(rel[2], dist_h)

        # Détection Masque Droit
        if 0.1 < phi < np.pi/2: 
            res["vd_phi"] = max(res["vd_phi"] or 0, phi)
        # Détection Masque Gauche
        elif -np.pi/2 < phi < -0.1:
            res["vg_phi"] = max(res["vg_phi"] or 0, abs(phi))
        # Détection Masque Horizontal (Casquette)
        if rel[2] > 0.5: # Si l'obstacle est nettement plus haut que le centre
            res["h_alt"] = max(res["h_alt"] or 0, alt)

    # Remplissage de la liste des IDs présents
    for key in ["vd_phi", "vg_phi", "h_alt"]:
        if res[key] is not None:
            res["Id_masque"].append(key.split('_')[0])

    # Horizon lointain
    if lointains:
        res["E_AZ"] = azimuthal_horizon(surface, lointains)
        res["Id_masque"].append("E_AZ")

    return res