# recommend.py
import os
import streamlit as st
from io import BytesIO
from PIL import Image
import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm
from database import add_image

# 1) Load the raw list from the correct file name:
#    if your repo has 'filename.pkl', use that. If it's 'filenames.pkl', use that.
raw_names   = pickle.load(open('filename.pkl', 'rb'))   

# 2) Prepend the images folder so paths exist on Streamlit Cloud
filenames   = [os.path.join("images", fn) for fn in raw_names]

# 3) Load your embeddings
feature_list = np.array(pickle.load(open('embeddings.pkl', 'rb')))

# 4) Build the ResNet50 + pooling model
base         = ResNet50(weights='imagenet', include_top=False, input_shape=(224,224,3))
base.trainable = False
model        = tf.keras.Sequential([base, GlobalMaxPooling2D()])

def extract_features(img_bytes: bytes):
    buf = BytesIO(img_bytes)
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
        .stApp { background: linear-gradient(135deg,#f0f2f6 0%,#c3cfe2 100%); }
        .stButton>button { width:100px; margin-right:10px; }
      </style>
    """, unsafe_allow_html=True)

    cols = st.columns([1,1,8])
    with cols[0]:
        if st.button("Logout"):
            for k in ["logged_in","user_id","username","redirect_to_profile"]:
                st.session_state.pop(k, None)
            st.experimental_rerun()
    with cols[1]:
        if st.button("Profile"):
            st.session_state.redirect_to_profile = True
            st.experimental_rerun()

    st.markdown("## 👗 Fashion Recommendation")
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first.")
        return

    uploaded = st.file_uploader("Upload image", type=["png","jpg","jpeg","gif"])
    if uploaded:
        img_bytes = uploaded.getvalue()
        add_image(st.session_state.user_id, uploaded.name, img_bytes)
        st.success(f"Saved **{uploaded.name}** to your profile.")
        st.image(BytesIO(img_bytes), caption="You uploaded:", use_container_width=True)

        vec   = extract_features(img_bytes)
        picks = get_recommendations(vec)

        st.markdown("---\n### Recommendations for you")
        rec_cols = st.columns(5)
        for i, col in enumerate(rec_cols):
            # filenames[i] now points to images/yourfile.jpg
            col.image(filenames[picks[i]], use_container_width=True)
