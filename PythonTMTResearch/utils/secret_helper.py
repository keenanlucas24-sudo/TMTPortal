"""Secret helper utility.

Provides a safe get_secret function that prefers Streamlit secrets (when running under
streamlit) and falls back to environment variables. This avoids hardcoding or committing
secrets into source control.
"""
from typing import Any, Optional


def get_secret(key: str, default: Optional[Any] = None) -> Optional[Any]:
    """Return a secret value.

    Tries Streamlit secrets first (st.secrets[...] ) if Streamlit is available. If not
    present, falls back to environment variables. Returns `default` if not found.
    """
    try:
        import streamlit as st
        # st.secrets behaves like a dict; check membership first
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        # Not running under Streamlit or streamlit not installed/initialised
        pass

    import os
    return os.environ.get(key, default)
