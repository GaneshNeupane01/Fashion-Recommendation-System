# recommend.py
import streamlit as st
from io import BytesIO
from PIL import Image
import numpy as np
import os
import ntpath
import pickle, tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm
from database import add_image

# Preload embeddings & model

import os, pickle

raw_names  = pickle.load(open('filenames.pkl','rb'))
filenames  = [os.path.join("images", ntpath.basename(fn)) for fn in raw_names]

feature_list = np.array(pickle.load(open('embeddings.pkl','rb')))

base         = ResNet50(weights='imagenet', include_top=False, input_shape=(224,224,3))
base.trainable = False
model = tf.keras.Sequential([base, GlobalMaxPooling2D()])

def do_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.stop()

def extract_features(b: bytes):
    buf = BytesIO(b)
    img = Image.open(buf).convert("RGB").resize((224,224))
    arr = image.img_to_array(img)
    arr = np.expand_dims(arr, axis=0)
    arr = preprocess_input(arr)
    vec = model.predict(arr).flatten()
    return vec / norm(vec)

def get_recommendations(vec):
    nn = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
    nn.fit(feature_list)
    _, idx = nn.kneighbors([vec])
    return idx[0]

def recommendation_page():
    st.set_page_config(page_title="Fashion Recommender", layout="wide", page_icon="👗")
    st.markdown("""
    <style>
      .stApp { background: linear-gradient(135deg,#0a0605 0%,#09062e 100%); }
      .topbar { display:flex; justify-content:flex-end; gap:1rem; }
      .stButton>button { width:100px; }
    </style>
    """, unsafe_allow_html=True)

    # Top‑right controls
    cols = st.columns([1,1,8])
    with cols[0]:
        if st.button("Logout"):
            for k in ["logged_in","user_id","username","redirect_to_profile"]:
                st.session_state.pop(k, None)
            do_rerun()
    with cols[1]:
        if st.button("Profile"):
            st.session_state.redirect_to_profile = True
            do_rerun()

    st.markdown("Fashion Recommendation")
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first.")
        return

    uploaded = st.file_uploader("Upload image", type=["png","jpg","jpeg","gif"])
    if uploaded:
        # Turn that memoryview into real bytes
        img_bytes = uploaded.getvalue()
        add_image(st.session_state.user_id, uploaded.name, img_bytes)
        st.success(f"Saved **{uploaded.name}** to your profile.")

        # Display immediately
        st.image(BytesIO(img_bytes), caption="You uploaded:", use_container_width=True)  # :contentReference[oaicite:2]{index=2}

        # Recommend & show
        vec   = extract_features(img_bytes)
        picks = get_recommendations(vec)

        st.markdown("---\n### Recommendations for you")
        rec_cols = st.columns(5)
        for i, c in enumerate(rec_cols):
            img_path = filenames[picks[i]]
            if not os.path.exists(img_path):
                c.error(f"❌ File not found: {img_path}")
            else:
                c.image(img_path, use_container_width=True)
