from sklearn.cluster import KMeans
import numpy as np

from models.fingerprint_model import Fingerprint


# 🔷 Convert DB fingerprints → numeric vectors
def get_fingerprint_data():
    records = Fingerprint.query.all()

    data = []

    for fp in records:
        try:
            width, height = fp.screen.split('x')
            vector = [int(width), int(height)]
            data.append(vector)
        except:
            continue

    return np.array(data)


# 🔷 Train model dynamically from DB
def train_model():
    data = get_fingerprint_data()

    # If not enough data, return None
    if len(data) < 3:
        return None

    model = KMeans(n_clusters=2, random_state=42)
    model.fit(data)

    return model


# 🔷 Detect outlier
def is_outlier(fp_vector):

    model = train_model()

    # If model not ready → no ML risk
    if model is None:
        return False

    distances = model.transform([fp_vector])

    # Take minimum distance to any cluster center
    min_distance = min(distances[0])

    # Threshold (tuneable)
    return min_distance > 800