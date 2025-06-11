<p align="center">
  <a href="https://futpeak.streamlit.app/">
    <img src="Recursos_gráficos/Banner.png" alt="Futpeak Banner">
  </a>
</p>

<h1 align="center">
  <a href="https://futpeak.streamlit.app/" style="text-decoration: none; color: inherit;">⚽ Futpeak</a>
</h1>

<p align="center">
  <strong>Predict Potential. Reach the Peak.</strong><br>
  Herramienta de scouting que proyecta el rendimiento futuro de jóvenes futbolistas.<br>
  <em>(Haz click en el nombre de la app, el banner o la demo visual para acceder a la página)</em>
</p>

---

## 🎙️ Presentación del proyecto

> En el mundo del fútbol, se invierte antes de conocer el rendimiento real de un fichaje.  
> ¿Y si se pudiera anticipar qué jugador joven llegará lejos… y cuándo?

En 2023, los clubes gastaron más de **8.500 millones de euros** en fichajes internacionales.  
Gran parte de ese gasto se destinó a jugadores **menores de 24 años**: apuestas sin garantías de rendimiento inmediato.  
Y lo más preocupante: según *The Times*, entre el **30 % y el 50 %** de los fichajes **no cumplen las expectativas deportivas**.

🎯 **Futpeak nace para reducir ese riesgo.**

Es una herramienta de predicción que analiza datos reales —**minutos, edad, impacto ofensivo**— y proyecta la evolución de un jugador comparándola con trayectorias profesionales reales. Agrupa automáticamente a cada jugador por patrones de desarrollo y anticipa su **año de mayor rendimiento**.

Ya hemos desarrollado un **MVP funcional** que permite seleccionar un jugador y visualizar su perfil, su curva de rendimiento y una proyección ajustada.  
En pruebas internas, el modelo ha mostrado una **precisión en torno al 75 %** al predecir si un jugador triunfará y cuándo.  
Jugadores como **Lamine Yamal, Désiré Doué o Jamal Musiala** ya han pasado por nuestro sistema.

💼 **¿Nuestro modelo de negocio?**  
Licencias **SaaS** para clubes, agencias y analistas, con planes por volumen y uso, así como un plan *freemium* con una pequeña base de datos de prueba.

🧠 **Y esto es solo el comienzo.**

La misma lógica de Futpeak puede aplicarse en otros sectores: startups, talento digital o inversión en personas.  
Donde hay datos y riesgo, hay oportunidad de anticipar.  
**Futpeak convierte datos en decisiones, antes de que el talento hable.**

---


## 🧭 Tabla de Contenidos

- [🔍 Descripción](#-descripción)
- [🎥 Demo visual](#-demo-visual)
- [✨ Funcionalidades](#-funcionalidades)
- [🛠️ Instalación](#-instalación)
- [📁 Estructura del proyecto](#-estructura-del-proyecto)
- [🧠 Modelo de predicción](#-modelo-de-predicción)
- [🚧 Roadmap](#-roadmap)
- [🤝 Contribuciones](#-contribuciones)
- [📄 Licencia](#-licencia)

---

## 🔍 Descripción

**Futpeak** es una aplicación interactiva que ayuda a evaluar y proyectar el potencial de jóvenes futbolistas basándose en datos de carrera y trayectorias similares. Utiliza técnicas de machine learning y curvas de evolución promedio para predecir el desarrollo futuro de un jugador.

> 💡 Pensado para clubes, analistas y agencias que buscan tomar decisiones de scouting basadas en evidencia.

---

## 🎥 Demo visual

<p align="center">
  <a href="https://futpeak.streamlit.app/">
    <img src="Recursos_gráficos/App_LamineYamal.png" alt="Demo de la app" width="100%">
  </a>
</p>

---

## ✨ Funcionalidades

- 📈 Proyección del rendimiento ajustada por trayectoria
- 🧬 Comparación con grupos de jugadores similares
- 🔍 Visualización de producción ofensiva, minutos y rating por 90 minutos
- 🧑‍💻 App desplegada en Streamlit con diseño responsivo
- 🛡️ Curvas con percentiles y bandas de confianza (25–75)

---

## 🛠️ Instalación

```bash
# Clona el repositorio
git clone https://github.com/JuanmaCM7/Futpeak.git
cd Futpeak

# Crea un entorno virtual
python -m venv venv
source venv/bin/activate  # o .\venv\Scripts\activate en Windows

# Instala las dependencias
pip install -r requirements.txt

# Ejecuta la app
streamlit run src/app.py
```
---

## 📁 Estructura del proyecto
```
Futpeak/
├── model/
│ └── curvas_promedio.joblib
├── notebooks/
├── src/
│ ├── app.py
│ ├── model_runner.py
│ ├── stats.py
│ ├── assets/
│ │ └── player_faces/
├── requirements.txt
├── README.md
├── Banner.png
└── App.png
```
---

## 🧠 Modelo de predicción

🎯 Clasificador multiclase RandomForest entrenado con trayectorias de cientos de jugadores

📊 Ajuste de proyección basado en rating real vs. curva promedio

🔄 Análisis temporal desde el debut profesional

📉 Incorporación futura de variables como lesiones, traspasos y minutos acumulados

---

## 🚧 Roadmap

 ✅ Visualización de rendimiento por temporada

 ✅ Proyección automática con ajuste personalizado

 📅 Incorporación de traspasos y lesiones

 📅 Nuevos modelos por posición específica

 📅 Exportación de informes PDF

 📅Dashboard para clubes y agentes

---

## 🤝 Contribuciones

¿Ideas o mejoras? Abre un issue o déjame un correo en juacanom@gmail.com
Toda ayuda es bienvenida para mejorar la herramienta.

---

## 📄 Licencia

Este proyecto no está licenciado como software libre.

Todos los derechos reservados © 2025 JuanmaCM7.  
No está permitido copiar, modificar ni redistribuir el código sin consentimiento previo por escrito del autor.

---