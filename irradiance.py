import numpy as np

def irradiance_surface_RE2020(surface, IDn, Idi, IDh, gamma, psi):
    alpha = surface["alpha"] # Déjà en rad via geometry.py
    beta = surface["beta"]   # Déjà en rad via geometry.py

    # 1. Calcul de l'incidence (tout en radians)
    psi_rel = (psi - alpha + np.pi) % (2 * np.pi) - np.pi
    cosθ = np.cos(gamma) * np.sin(beta) * np.cos(psi_rel) + np.sin(gamma) * np.cos(beta)
    cosθ = np.max([0, cosθ])

    # 2. Application du facteur de masque FfDir
    FfDir = 1.0
    
    if cosθ > 0:
        # Masque lointain (Horizon)
        if surface.get("E_AZ") is not None:
            # On utilise l'azimut en degrés pour trouver l'index dans la liste (0-35)
            idx = int((np.degrees(psi) % 360) // 10)
            # On compare gamma (rad) à l'angle de l'horizon converti en rad
            if gamma < np.deg2rad(surface["E_AZ"][idx]):
                FfDir = 0.0

        # Masques proches (si pas déjà masqué par l'horizon)
        if FfDir > 0:
            if surface.get("vd_phi") and psi_rel > surface["vd_phi"]:
                FfDir = 0.0
            elif surface.get("vg_phi") and psi_rel < -surface["vg_phi"]:
                FfDir = 0.0
            elif surface.get("h_alt") and gamma < surface["h_alt"]:
                FfDir = 0.0

    # Rayonnement direct masqué
    Drp = cosθ * IDn * FfDir
    # Rayonnement diffus (RE2020 : non masqué par les obstacles proches/lointains)
    Dfp = Idi * 0.5 * (1 + np.cos(beta))
    # Rayonnement réfléchi (Albédo)
    alb = 0.2
    Rrp = (IDh + Idi) * alb * 0.5 * (1 - np.cos(beta))

    return (Drp + Dfp + Rrp), FfDir