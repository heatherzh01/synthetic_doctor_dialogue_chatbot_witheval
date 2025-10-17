import streamlit as st
from PIL import Image
import sys
sys.path.append('..')
import os



st.set_page_config(
    page_title="Welcome to NovoNordisk ChatHCP",
    page_icon="👋",
)

st.write(os.getcwd())

image = Image.open('./static/gammalogo.png')
st.sidebar.image(image, width=150)
st.sidebar.info(f'''Logged in: **Edgar Cao**\ncao.edgar@bcg.com''')