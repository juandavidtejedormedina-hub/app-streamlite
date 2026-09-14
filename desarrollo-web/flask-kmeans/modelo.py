from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from joblib import dump

# Datos de ejemplo (ingresos, gastos)
X = np.array([
    [1, 1],
    [2, 1.5],
    [4, 3],
    [7, 5],
    [5, 3.5],
    [5, 4.5]
])

# Entrenar modelo KMeans (k=2)
kmeans = KMeans(n_clusters=2, random_state=0)
kmeans.fit(X)

dump(kmeans, Path(__file__).resolve().parent / 'modelo_kmeans.pkl')
