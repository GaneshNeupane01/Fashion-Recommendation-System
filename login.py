# login.py
import streamlit as st
from database import init_db, add_user, authenticate_user

# Ensure DB tables exist
init_db()

def do_rerun():
    """Call the appropriate rerun method for your Streamlit version."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.stop()

def login_page():
    st.set_page_config(page_title="Login / Sign Up", layout="centered")
    st.markdown("""
    <style>
        .stApp {
        background: linear-gradient(135deg,#0a0605 0%,#09062e 100%);;
      }
      .card {
        max-width: 400px; margin: auto; padding: 2rem;
                border:2px solid #0e084d;
        border-radius: 1rem; background: linear-gradient(135deg,#150a8f 0%,#0e084d 100%);
        
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }
        .card:hover{
                box-shadow:0 0px 8px 8px #1002ad;
                }
      .stButton>button { width: 100%; }
    </style>""", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("🔐 Login / Sign Up")

    choice = st.selectbox("Choose action", ["Login", "Sign Up"])
    if choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                uid, uname, _ = user
                st.session_state.logged_in = True
                st.session_state.user_id   = uid
                st.session_state.username  = uname
                st.success("✅ Logged in! Redirecting…")
                do_rerun()
            else:
                st.error("❌ Invalid credentials.")
    else:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        email = st.text_input("Email")
        if st.button("Sign Up"):
            ok = add_user(new_u, new_p, email)
            if ok:
                user = authenticate_user(new_u, new_p)
                if user:
                    uid, uname, _ = user
                    st.session_state.logged_in = True
                    st.session_state.user_id   = uid
                    st.session_state.username  = uname
                    st.success("🎉 Account created! Redirecting…")
                    do_rerun()
            else:
                st.error("⚠️ Username already exists.")
    st.markdown("</div>", unsafe_allow_html=True)
