# data_loader.py

import pandas as pd

def load_mock_data():
    return pd.DataFrame({
        "name": ["Player A", "Player B", "Player C"],
        "age": [18, 19, 20],
        "position": ["Forward", "Midfielder", "Defender"],
        "minutes": [1200, 1800, 1500],
        "rating": [65, 70, 75]
    })
