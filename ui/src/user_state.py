from uuid import uuid4
import streamlit as st
from streamlit_cookies_manager import CookieManager

def get_user_id():
    """Get a user id from cookies if possible, otherwise instantiate a new user_id

    Returns:
        str: User ID (UUID4 string)
    """
    cookies = CookieManager()
    # Get cookies
    if not cookies.ready():
        st.stop()
    if "user_id" not in cookies:
        cookies["user_id"] = str(uuid4())
        cookies.save()
    return cookies["user_id"]