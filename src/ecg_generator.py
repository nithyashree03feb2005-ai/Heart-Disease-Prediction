import numpy as np

def generate_ecg(length=200):
    t = np.linspace(0, 1, length)
    ecg = 0.6*np.sin(2*np.pi*5*t)
    ecg += 0.2*np.sin(2*np.pi*15*t)
    ecg += 0.05*np.random.randn(length)
    return ecg