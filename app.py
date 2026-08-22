"""ParcelPilot AI Support Copilot entry point."""

import streamlit as st

st.set_page_config(
    page_title="ParcelPilot AI Support Copilot",
    page_icon="📦",
    layout="wide",
)

st.title("📦 ParcelPilot AI Support Copilot")
st.caption("Reliable answers across policies, agreements, orders, and support tickets")

with st.sidebar:
    st.header("Session context")
    role = st.selectbox("Role", ["Internal Support", "Customer"])
    account = st.selectbox(
        "Account",
        ["Northstar Logistics", "LumenWorks", "Beacon Retail", "Axis Labs"],
        disabled=role == "Internal Support",
    )
    st.divider()
    st.success("Project setup complete")

st.info(
    "The application shell is running. In the next checkpoint, we will connect the supplied "
    "documents and structured data."
)

if prompt := st.chat_input("Ask ParcelPilot a question..."):
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        st.write("Data tools are not connected yet. This is the setup checkpoint.")
