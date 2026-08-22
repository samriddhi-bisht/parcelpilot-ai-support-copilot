import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --navy: #14243A;
            --navy-soft: #1C304A;
            --slate: #526276;
            --teal: #247B79;
            --teal-soft: #E9F3F2;
            --surface: #FFFFFF;
            --background: #F4F6F8;
            --border: #DCE2E8;
            --text: #17202B;
            --muted: #647386;
        }

        .stApp {
            background: var(--background);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: var(--navy);
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC;
        }

        [data-testid="stSidebar"] label {
            color: #D8E0E8 !important;
            font-size: 0.82rem;
            font-weight: 500;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }

        .brand-kicker {
            color: var(--teal);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.12rem;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .brand-title {
            color: var(--navy);
            font-size: 2.15rem;
            font-weight: 680;
            letter-spacing: -0.04rem;
            line-height: 1.1;
            margin: 0;
        }

        .brand-description {
            color: var(--muted);
            font-size: 1rem;
            margin-top: 0.65rem;
            margin-bottom: 1.8rem;
        }

        .context-bar {
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 4px solid var(--teal);
            border-radius: 8px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 1.2rem;
            color: var(--slate);
            font-size: 0.9rem;
        }

        .section-title {
            color: var(--navy);
            font-size: 1.05rem;
            font-weight: 650;
            margin-top: 1.25rem;
            margin-bottom: 0.6rem;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 9px;
            padding: 1rem 1.05rem;
        }

        div[data-testid="stMetric"] label {
            color: var(--muted);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.04rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--navy);
            font-weight: 650;
        }

        .stButton > button {
            background: var(--navy);
            border: 1px solid var(--navy);
            border-radius: 7px;
            color: white;
            font-weight: 550;
            min-height: 2.7rem;
        }

        .stButton > button:hover {
            background: var(--navy-soft);
            border-color: var(--navy-soft);
            color: white;
        }

        div[data-baseweb="select"] > div,
        .stTextInput input {
            background: white;
            border-color: var(--border);
            border-radius: 7px;
        }

        .status-active {
            display: inline-block;
            background: var(--teal-soft);
            color: #17615F;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.76rem;
            font-weight: 650;
        }

        .sidebar-brand {
            color: white;
            font-size: 1.25rem;
            font-weight: 650;
            padding-top: 0.6rem;
            margin-bottom: 0.2rem;
        }

        .sidebar-caption {
            color: #AFBDCB;
            font-size: 0.82rem;
            margin-bottom: 1.4rem;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
