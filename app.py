# app.py
import streamlit as st
from database import init_db
from login import login_page
from recommend import recommendation_page
from profile import profile_page

# --- DB & Session Initialization ---
init_db()  # ensure users & images tables exist

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "redirect_to_profile" not in st.session_state:
    st.session_state.redirect_to_profile = False

# --- Navigation Logic ---
if st.session_state.redirect_to_profile:
    profile_page()
else:
    if not st.session_state.logged_in:
        login_page()
    else:
        recommendation_page()
