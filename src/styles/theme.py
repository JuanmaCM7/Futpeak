# src/streamlit/styles/theme.py

import streamlit as st
from pathlib import Path
import base64
from PIL import Image, ImageEnhance

def apply_background():
    assets_path = Path(__file__).parent.parent / "assets"
    original = assets_path / "bg_image.png"
    filtered = assets_path / "bg_image_filtered_2.png"

    if original.exists() and not filtered.exists():
        try:
            img = Image.open(original).convert("L")
            img = ImageEnhance.Brightness(img).enhance(0.6)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            img.save(filtered)
        except Exception as e:
            st.error(f"❌ Error processing image: {e}")
            return

    if not filtered.exists():
        st.warning("⚠️ Filtered background image not found or failed to create.")
        return

    try:
        with open(filtered, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()

        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: local;
                background-repeat: no-repeat;
                padding-top: 0 !important;
                margin-top: 0 !important;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.3);
                z-index: 0;
                margin: 0 !important;
                padding: 0 !important;
            }}
            .stApp > * {{
                position: relative;
                z-index: 1;
            }}
            </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Failed to apply background: {e}")










