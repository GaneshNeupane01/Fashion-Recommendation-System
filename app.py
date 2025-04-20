import streamlit as st
import sqlite3
import hashlib
import os
import uuid
import shutil
from PIL import Image
import numpy as np
from datetime import datetime
import pickle
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.models import Sequential
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm

# Page configuration
st.set_page_config(
    page_title="StyleVibe",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, interactive, and animated UI with themes
def load_css():
    theme = st.session_state.get('theme', 'light')
    if theme == 'dark':
        css = """
        <style>
            .stApp { background: #1a1a1a; color: #ecf0f1; }
            .main-header { background: linear-gradient(90deg, #34495e 0%, #2c3e50 100%); color: #ecf0f1; }
            .card { background: #2c3e50; color: #ecf0f1; }
            .custom-button { background: linear-gradient(90deg, #34495e 0%, #2c3e50 100%); color: #ecf0f1; }
            input[type=text], input[type=password], textarea { background: #2c3e50; color: #ecf0f1; border: 2px solid #34495e; }
            .stTextInput > label, .stTextArea > label { color: #ecf0f1 !important; }
            .login-section, .register-section { background: #2c3e50; color: #ecf0f1; }
            .gallery img { box-shadow: 0 4px 10px rgba(236, 240, 241, 0.1); }
            .css-1d391kg { background: #34495e; color: #ecf0f1; }
            #MainMenu, footer { visibility: hidden; }
        </style>
        """
    else:
        css = """
        <style>
         /* make all Streamlit buttons have white text */
        .stButton>button {
            color: white !important;
background:black ! important;
        }
            /* Global Styling */
            .stApp { background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%); font-family: 'Poppins', sans-serif; color: #2c3e50; }
            .main-header { background: linear-gradient(90deg, #ff7675 0%, #d63031 100%); padding: 30px; border-radius: 12px; color: white; text-align: center; margin-bottom: 40px; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15); animation: slideInHeader 0.8s ease-out; }
            @keyframes slideInHeader { 0% { transform: translateY(-50px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
            .card { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1); margin-bottom: 25px; transition: transform 0.3s ease, box-shadow 0.3s ease; }
            .card:hover { transform: translateY(-8px); box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2); }
            .custom-button { background: linear-gradient(90deg, #ff7675 0%, #d63031 100%); color: white; border: none; border-radius: 8px; padding: 12px 24px; font-size: 16px; cursor: pointer; transition: all 0.3s ease; text-transform: uppercase; font-weight: 600; animation: buttonSlideIn 1s ease-out; }
            .custom-button:hover { background: linear-gradient(90deg, #d63031 0%, #ff7675 100%); transform: scale(1.05); box-shadow: 0 4px 15px rgba(255, 118, 117, 0.4); }
            @keyframes buttonSlideIn { 0% { transform: translateX(-20px); opacity: 0; } 100% { transform: translateX(0); opacity: 1; } }
            input[type=text], input[type=password], textarea { width: 100%; padding: 14px; border: 2px solid #dfe6e9; border-radius: 8px; margin: 10px 0; font-size: 16px; background: #ffffff; color: #2c3e50; transition: border-color 0.3s ease, box-shadow 0.3s ease; }
            input:focus, textarea:focus { border-color: #ff7675; box-shadow: 0 0 8px rgba(255, 118, 117, 0.3); outline: none; }
            .stTextInput > label, .stTextArea > label { color: #2c3e50 !important; font-weight: 700; font-size: 18px; margin-bottom: 6px; opacity: 1 !important; }
            .login-section, .register-section { background: rgba(255, 255, 255, 0.98); border-radius: 12px; padding: 30px; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1); margin: 20px; animation: fadeInSection 1s ease-out; }
            .login-section { border-left: 5px solid #ff7675; }
            .register-section { border-right: 5px solid #d63031; }
            .section-title { font-size: 28px; font-weight: 700; margin-bottom: 20px; color: #2c3e50; }
            @keyframes fadeInSection { 0% { opacity: 0; transform: scale(0.95); } 100% { opacity: 1; transform: scale(1); } }
            .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; padding: 20px 0; }
            .gallery img { width: 100%; border-radius: 10px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease; }
            .gallery img:hover { transform: scale(1.05); }
            .notification { padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px; animation: slideInNotification 0.5s ease-out; }
            .success { background: #00b894; }
            .error { background: #d63031; }
            .info { background: #0984e3; }
            @keyframes slideInNotification { 0% { transform: translateY(-20px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
            .css-1d391kg { background: linear-gradient(180deg, #ff7675 0%, #d63031 100%); color: white; border-radius: 12px; padding: 20px; }
            .css-1d391kg h1, .css-1d391kg label { color: white !important; }
            #MainMenu, footer { visibility: hidden; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# Database Operations
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        created_at TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS favorites (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        file_path TEXT,
        favorited_at TEXT
    )
    ''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute(
            "INSERT INTO users (id, username, password, created_at) VALUES (?, ?, ?, ?)",
            (user_id, username, hashed_pw, created_at)
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user

def update_password(user_id, new_password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_pw, user_id))
    conn.commit()
    conn.close()

def add_to_favorites(user_id, image_path):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    fav_id = str(uuid.uuid4())
    favorited_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        c.execute(
            "INSERT INTO favorites (id, user_id, file_path, favorited_at) VALUES (?, ?, ?, ?)",
            (fav_id, user_id, image_path, favorited_at)
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def get_user_favorites(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT file_path FROM favorites WHERE user_id = ? ORDER BY favorited_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# Utility Functions
def create_directories():
    os.makedirs('uploads', exist_ok=True)

def save_uploaded_file(uploaded_file, user_id):
    user_dir = f"uploads/{user_id}"
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Recommendation System
def load_model_and_data():
    feature_list = np.array(pickle.load(open('embeddings.pkl', 'rb')))
    filenames = pickle.load(open('filenames.pkl', 'rb'))
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    model.trainable = False
    model = Sequential([model, GlobalMaxPooling2D()])
    return model, feature_list, filenames

def feature_extraction(img_path, model):
    img = keras_image.load_img(img_path, target_size=(224, 224))
    img_array = keras_image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result / norm(result)
    return normalized_result

def recommend(features, feature_list, filenames, n=6):
    neighbors = NearestNeighbors(n_neighbors=n, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)
    distances, indices = neighbors.kneighbors([features])
    return [filenames[i] for i in indices[0]]

# Session Management
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.logged_in = False
    st.session_state.page = "login"

def initialize():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'notification' not in st.session_state:
        st.session_state.notification = {'show': False, 'type': '', 'message': ''}
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    create_directories()
    init_db()

# UI Components
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>StyleVibe ✨</h1>
        <p>Your Fashion Inspiration Hub</p>
    </div>
    """, unsafe_allow_html=True)

def show_notification():
    if st.session_state.notification['show']:
        st.markdown(f"""
        <div class="notification {st.session_state.notification['type']}">
            {st.session_state.notification['message']}
        </div>
        """, unsafe_allow_html=True)
        st.session_state.notification['show'] = False

def set_notification(type_name, message):
    st.session_state.notification = {
        'show': True,
        'type': type_name,
        'message': message
    }

# Page Renderers
def render_login_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='login-section'>", unsafe_allow_html=True)
        st.markdown("<h2 class='section-title'>Login</h2>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_password")
        if st.button("Login", key="login_button", type="primary"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.logged_in = True
                st.session_state.page = "dashboard"
                set_notification("success", "Welcome back!")
                st.rerun()
            else:
                set_notification("error", "Invalid credentials.")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='register-section'>", unsafe_allow_html=True)
        st.markdown("<h2 class='section-title'>Register</h2>", unsafe_allow_html=True)
        reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
        reg_password = st.text_input("Password", placeholder="Create a password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", placeholder="Confirm your password", type="password", key="confirm_password")
        if st.button("Register", key="register_button", type="primary"):
            if not reg_username or not reg_password:
                set_notification("error", "All fields are required.")
            elif reg_password != confirm_password:
                set_notification("error", "Passwords do not match.")
            else:
                success = create_user(reg_username, reg_password)
                if success:
                    set_notification("success", "Registered! Please login.")
                else:
                    set_notification("error", "Username taken.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def render_dashboard():
    st.sidebar.title(f"Hi, {st.session_state.username}! 👋")
    menu = st.sidebar.radio("Menu", ["Home", "Recommend", "Uploads", "Favorites", "Settings"])
    if st.sidebar.button("Logout", type="primary"):
        logout()
        set_notification("info", "See you soon!")
        st.rerun()

    if menu == "Home":
        st.markdown("<div class='card'><h2>Welcome!</h2><p>Upload an image to discover styles from our collection.</p></div>", unsafe_allow_html=True)

    elif menu == "Recommend":
        st.markdown("<div class='card'><h2>Get Recommendations</h2><p>Upload an image to find similar styles.</p></div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = save_uploaded_file(uploaded_file, st.session_state.user_id)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("<h3>Your Image</h3>", unsafe_allow_html=True)
                st.image(uploaded_file, width=250)
            with col2:
                st.markdown("<h3>Similar Styles</h3>", unsafe_allow_html=True)
                with st.spinner("Finding matches..."):
                    model, feature_list, filenames = load_model_and_data()
                    features = feature_extraction(file_path, model)
                    recommendations = recommend(features, feature_list, filenames)
                st.markdown("<div class='gallery'>", unsafe_allow_html=True)
                rec_cols = st.columns(3)
                for i, rec in enumerate(recommendations):
                    with rec_cols[i % 3]:
                        st.image(rec)
                        if st.button("❤️ Favorite", key=f"fav_{i}"):
                            if add_to_favorites(st.session_state.user_id, rec):
                                set_notification("success", "Added to Favorites!")
                            else:
                                set_notification("info", "Already in Favorites.")
                st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Uploads":
        st.markdown("<div class='card'><h2>My Uploads</h2></div>", unsafe_allow_html=True)
        uploads = [os.path.join(f"uploads/{st.session_state.user_id}", f) for f in os.listdir(f"uploads/{st.session_state.user_id}") if os.path.isfile(os.path.join(f"uploads/{st.session_state.user_id}", f))] if os.path.exists(f"uploads/{st.session_state.user_id}") else []
        if not uploads:
            st.markdown("<div ><h2>No Uploads Yet</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='gallery'>", unsafe_allow_html=True)
            cols = st.columns(4)
            for i, file_path in enumerate(uploads):
                with cols[i % 4]:
                    st.image(file_path, width=150)
                    if st.button("Delete", key=f"delete_{i}", type="primary"):
                        os.remove(file_path)
                        set_notification("info", "Image deleted.")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Favorites":
        st.markdown("<div class='card'><h2>My Favorites</h2></div>", unsafe_allow_html=True)
        favs = get_user_favorites(st.session_state.user_id)
        if not favs:
            st.markdown("<div><h3>No favorites yet.</h3></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='gallery'>", unsafe_allow_html=True)
            cols = st.columns(4)
            for i, fp in enumerate(favs):
                with cols[i % 4]:
                    st.image(fp, width=150)
                    if st.button("Remove", key=f"unfav_{i}"):
                        conn = sqlite3.connect('users.db')
                        c = conn.cursor()
                        c.execute("DELETE FROM favorites WHERE user_id = ? AND file_path = ?", (st.session_state.user_id, fp))
                        conn.commit()
                        conn.close()
                        set_notification("info", "Removed from Favorites.")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Settings":
        st.markdown("<div class='card'><h2>Settings</h2></div>", unsafe_allow_html=True)
        st.subheader("Change Password")
        old_pw = st.text_input("Current Password", type="password", key="old_pw")
        new_pw = st.text_input("New Password", type="password", key="new_pw")
        confirm_pw = st.text_input("Confirm New Password", type="password", key="confirm_pw")
        if st.button("Update Password", key="update_pw"):
            user = authenticate_user(st.session_state.username, old_pw)
            if not user:
                set_notification("error", "Current password incorrect.")
            elif new_pw != confirm_pw:
                set_notification("error", "New passwords do not match.")
            else:
                update_password(st.session_state.user_id, new_pw)
                set_notification("success", "Password updated successfully!")
                st.rerun()

        st.subheader("Theme")
        theme_choice = st.selectbox(" ", ["light", "dark"], index=0 if st.session_state.theme=='light' else 1)
        if st.button("Apply Theme", key="apply_theme"):
            st.session_state.theme = theme_choice
            set_notification("success", f"Theme set to {theme_choice.title()} mode.")
            st.rerun()

# Main App
def main():
    initialize()
    load_css()
    render_header()
    show_notification()
    if not st.session_state.logged_in:
        render_login_page()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
