import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap'
        );

        :root {
            --navy: #14243A;
            --navy-soft: #203650;
            --slate: #526276;
            --teal: #247B79;
            --teal-dark: #1A6462;
            --teal-soft: #E9F3F2;
            --surface: #FFFFFF;
            --background: #F4F6F8;
            --border: #DCE2E8;
            --text: #17202B;
            --muted: #647386;
            --warning-bg: #FFF8E8;
            --warning-border: #E8CB81;
            --danger-bg: #FFF1F1;
            --danger-border: #E4A3A3;
        }

        html,
        body,
        .stApp {
            font-family: "Manrope", Arial, sans-serif;
        }

        .stApp button,
        .stApp input,
        .stApp textarea,
        .stApp label,
        .stApp p,
        .stApp div,
        .stApp span {
            font-family: "Manrope", Arial, sans-serif;
        }

        /*
        Restore Streamlit's Material icon font.
        Without this, icon names such as keyboard_double_arrow_left
        appear as visible text.
        */
        [data-testid="stIconMaterial"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons {
            font-family: "Material Symbols Rounded",
                         "Material Symbols Outlined",
                         "Material Icons" !important;
            font-weight: normal !important;
            font-style: normal !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: "liga" !important;
            -webkit-font-smoothing: antialiased !important;
            font-feature-settings: "liga" !important;
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

        /*
        Apply light text only to normal sidebar content.
        Select controls are overridden separately below.
        */
        [data-testid="stSidebar"] {
            color: #F8FAFC;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #F8FAFC;
        }

        [data-testid="stSidebar"] label {
            color: #D8E0E8 !important;
            font-size: 0.82rem;
            font-weight: 500;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.13);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1.8rem;
            padding-bottom: 4rem;
        }

        .brand-kicker {
            color: var(--teal);
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.13rem;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .brand-title {
            color: var(--navy);
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.04rem;
            line-height: 1.12;
            margin: 0;
        }

        .brand-description {
            color: var(--muted);
            font-size: 0.98rem;
            margin-top: 0.6rem;
            margin-bottom: 1.45rem;
        }

        .context-bar {
            background: var(--surface);
            border: 1px solid var(--border);
            border-left: 4px solid var(--teal);
            border-radius: 8px;
            padding: 0.9rem 1.05rem;
            margin-bottom: 1rem;
            color: var(--slate);
            font-size: 0.88rem;
        }

        .section-title {
            color: var(--navy);
            font-size: 1rem;
            font-weight: 650;
            margin-top: 1.15rem;
            margin-bottom: 0.6rem;
        }

        .sidebar-brand {
            color: #FFFFFF !important;
            font-size: 1.22rem;
            font-weight: 650;
            padding-top: 0.55rem;
            margin-bottom: 0.2rem;
        }

        .sidebar-caption {
            color: #AFBDCB !important;
            font-size: 0.81rem;
            line-height: 1.45;
            margin-bottom: 1.35rem;
        }

        .role-note {
            color: #AFC0D1 !important;
            font-size: 0.78rem;
            line-height: 1.5;
            margin-top: 0.8rem;
        }

        .answer-meta {
            color: var(--muted);
            font-size: 0.74rem;
            margin-top: 0.65rem;
        }

        .source-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.82rem 0.9rem;
            margin-bottom: 0.55rem;
        }

        .source-title {
            color: var(--navy);
            font-weight: 650;
            font-size: 0.88rem;
        }

        .source-meta {
            color: var(--muted);
            font-size: 0.76rem;
            margin-top: 0.2rem;
        }

        .confirmation-panel {
            background: var(--warning-bg);
            border: 1px solid var(--warning-border);
            border-radius: 8px;
            padding: 0.95rem 1rem;
            margin-top: 0.7rem;
            margin-bottom: 0.8rem;
        }

        .confirmation-title {
            color: #6B5418;
            font-weight: 650;
            font-size: 0.9rem;
        }

        .confirmation-text {
            color: #76632C;
            font-size: 0.82rem;
            margin-top: 0.25rem;
        }

        div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.9rem 1rem;
        }

        div[data-testid="stMetric"] label {
            color: var(--muted);
            font-size: 0.74rem;
            text-transform: uppercase;
            letter-spacing: 0.04rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--navy);
            font-weight: 650;
        }

        div[data-testid="stChatMessage"] {
            background: transparent;
            padding-top: 0.55rem;
            padding-bottom: 0.55rem;
        }

        div[data-testid="stChatMessageContent"] {
            color: var(--text);
            line-height: 1.65;
        }

        div[data-testid="stExpander"] {
            background: #FAFBFC;
            border: 1px solid var(--border);
            border-radius: 8px;
        }

        .stButton > button {
            background: var(--navy);
            border: 1px solid var(--navy);
            border-radius: 7px;
            color: white;
            font-weight: 550;
            min-height: 2.55rem;
        }

        /* Sidebar secondary buttons (Start new conversation) */
[data-testid="stSidebar"] .stButton > button {
    background: #FFFFFF !important;
    color: #17202B !important;
    border: 1px solid #CBD4DE !important;
    font-weight: 600;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #F5F7FA !important;
    color: #17202B !important;
    border: 1px solid #AEB8C4 !important;
}

[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div {
    color: #17202B !important;
}

        .stButton > button:hover {
            background: var(--navy-soft);
            border-color: var(--navy-soft);
            color: white;
        }

        .stButton > button[kind="secondary"] {
            background: white;
            color: var(--navy);
            border-color: var(--border);
        }

        .stButton > button[kind="secondary"]:hover {
            background: #F1F4F7;
            color: var(--navy);
            border-color: #BFC9D3;
        }

        /*
        Sidebar select boxes: force all selected values and text dark.
        */
        [data-testid="stSidebar"] div[data-baseweb="select"] {
            background: #FFFFFF !important;
            border-radius: 8px !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #FFFFFF !important;
            border: 1px solid #CBD4DE !important;
            border-radius: 8px !important;
            color: #17202B !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] span,
        [data-testid="stSidebar"] div[data-baseweb="select"] div,
        [data-testid="stSidebar"] div[data-baseweb="select"] input {
            color: #17202B !important;
            -webkit-text-fill-color: #17202B !important;
        }

        [data-testid="stSidebar"]
        div[data-baseweb="select"]
        [data-testid="stMarkdownContainer"] p {
            color: #17202B !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] svg {
            fill: #526276 !important;
            color: #526276 !important;
        }

        /*
        Select dropdown menu shown outside the sidebar DOM.
        */
        div[data-baseweb="popover"] {
            background: #FFFFFF !important;
        }

        div[data-baseweb="popover"] ul {
            background: #FFFFFF !important;
        }

        div[role="listbox"] {
            background: #FFFFFF !important;
            border: 1px solid var(--border) !important;
        }

        div[role="option"],
        div[role="option"] span,
        div[role="option"] div {
            background: #FFFFFF;
            color: #17202B !important;
            -webkit-text-fill-color: #17202B !important;
        }

        div[role="option"]:hover,
        div[role="option"]:hover span,
        div[role="option"]:hover div {
            background: #EEF2F5 !important;
            color: #17202B !important;
        }

        div[role="option"][aria-selected="true"],
        div[role="option"][aria-selected="true"] span,
        div[role="option"][aria-selected="true"] div {
            background: var(--teal-soft) !important;
            color: var(--teal-dark) !important;
            -webkit-text-fill-color: var(--teal-dark) !important;
        }

        .stTextInput input,
        .stTextArea textarea {
            background: #FFFFFF !important;
            border: 1px solid #CBD4DE !important;
            border-radius: 7px;
            color: var(--text) !important;
        }

        [data-testid="stChatInput"] textarea {
            background: #FFFFFF !important;
            border: 1px solid var(--border);
            color: var(--text) !important;
        }

        [data-testid="stChatInput"] textarea::placeholder,
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #7A8797 !important;
            opacity: 1;
        }

        .status-current {
            display: inline-block;
            background: var(--teal-soft);
            color: var(--teal-dark);
            border-radius: 999px;
            padding: 0.2rem 0.55rem;
            font-size: 0.7rem;
            font-weight: 650;
        }

        .radar-card {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 9px;
    padding: 1rem 1.05rem;
    margin-bottom: 0.75rem;
}

.radar-card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
}

.radar-ticket {
    color: var(--navy);
    font-size: 0.92rem;
    font-weight: 700;
}

.radar-account {
    color: var(--muted);
    font-size: 0.74rem;
    margin-top: 0.12rem;
}

.radar-badges {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.radar-subject {
    color: var(--text);
    font-size: 0.9rem;
    font-weight: 600;
    margin-top: 0.75rem;
}

.radar-detail {
    color: var(--muted);
    font-size: 0.76rem;
    margin-top: 0.4rem;
}

.radar-workaround {
    background: #F4F7F8;
    border-left: 3px solid var(--teal);
    color: var(--slate);
    font-size: 0.78rem;
    margin-top: 0.65rem;
    padding: 0.55rem 0.7rem;
}

.risk-critical,
.risk-warning,
.risk-normal {
    display: inline-block;
    border-radius: 999px;
    padding: 0.22rem 0.58rem;
    font-size: 0.68rem;
    font-weight: 700;
}

.risk-critical {
    background: #FCE8E8;
    color: #A33838;
}

.risk-warning {
    background: #FFF4D8;
    color: #84621A;
}

.risk-normal {
    background: var(--teal-soft);
    color: var(--teal-dark);
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