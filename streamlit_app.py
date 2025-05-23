import os
import sys

# Asegúrate de que src/ está en el path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Importa app.py como un módulo
from app import main

if __name__ == "__main__":
    main()
