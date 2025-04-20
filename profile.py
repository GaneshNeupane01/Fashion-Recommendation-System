import streamlit as st
from database import get_images_for_user
from io import BytesIO

def do_rerun():
    """Rerun the app, compatible across Streamlit versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.stop()

def profile_page():
    st.set_page_config(page_title="My Profile", layout="wide", page_icon="👤")
    st.markdown("""
    <style>
      .stApp {
        background: linear-gradient(135deg,#0a0605 0%,#09062e 100%);;
      }
      .topbar {
        display: flex;
        justify-content: flex-end;
        gap: 2rem;
        margin-bottom: 1rem;
      }
      .stButton>button {
        width: 120px;
      }
      .profile-card {
       background: black;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
      }
    </style>
    """, unsafe_allow_html=True)

    # Top‑nav buttons
    with st.container():
        cols = st.columns([1,1,8])
        with cols[0]:
            if st.button("Home"):
                st.session_state.redirect_to_profile = False
                do_rerun()
        with cols[1]:
            if st.button("Logout"):
                for key in ["logged_in","user_id","username","redirect_to_profile"]:
                    st.session_state.pop(key, None)
                do_rerun()
        cols[2].markdown("")  # spacer

    # Check login
    if not st.session_state.get("logged_in", False):
        st.warning("🔒 You need to log in to view your profile.")
        return

    # Greeting card
    st.markdown(
        f"<div class='profile-card'>"
        f"<h2>Hello, <span style='color:#e76f51;'>{st.session_state.username}</span>!</h2>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Fetch & display user images
    images = get_images_for_user(st.session_state.user_id)
    if not images:
        st.info("You haven’t uploaded any images yet.")
        return

    st.markdown("### 📸 Your Uploads")
    cols = st.columns(3)
    for i, (fname, blob) in enumerate(images):
        with cols[i % 3]:
            st.image(BytesIO(blob), caption=fname, use_container_width=True)
