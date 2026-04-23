import numpy as np
from ecg_generator import generate_ecg

def get_ecg():
    return generate_ecg()

def extract_features(signal):
    return [np.mean(signal), np.std(signal), np.max(signal), np.min(signal)]