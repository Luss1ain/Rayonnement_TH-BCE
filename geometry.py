# geometry.py
import numpy as np
import pandas as pd

# ==========================
# Chargement CSV
# ==========================

def load_surfaces(csv_file):
    """
    Charge les surfaces étudiées SketchUp
    """
    return pd.read_csv(csv_file)


def load_obstacles(csv_file):
    """
    Charge tous les obstacles (sans notion proche/lointain)
    """
    obstacles = []
    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():
        verts = list(map(float, row.vertices.split(";")))
        vertices = np.array(verts).reshape(-1, 3)
        obstacles.append({
            "id": row.id,
            "vertices": vertices
        })

    return obstacles

# ==========================
# Geometric tools
# ==========================

def normalize(v):
    return v / np.linalg.norm(v)


def azimuth_from_normal(n):
    """
    Convention RE2020 :
    - α = 0 : Sud
    - α > 0 : Ouest
    """
    return np.arctan2(n[0], -n[1])


def inclination_from_normal(n):
    """
    β = 90° pour paroi verticale
    """
    return np.arccos(np.clip(n[2], -1.0, 1.0))


def surface_dimensions(vertices):
    """
    Paroi équivalente RE2020 :
    largeur = plus grande distance horizontale
    hauteur = étendue verticale
    """
    z = vertices[:, 2]
    hpb = z.max() - z.min()

    xy = vertices[:, :2]
    dists = np.linalg.norm(xy[:, None] - xy[None, :], axis=2)
    lpb = dists.max()

    return lpb, hpb


def min_distance(point, vertices):
    """
    Distance minimale point → polygone (approchée par sommets)
    """
    return np.min(np.linalg.norm(vertices - point, axis=1))
