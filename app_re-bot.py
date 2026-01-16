import streamlit as st
import os

# WICHTIG: Dies zwingt Google-Bibliotheken auf die stabile Version 1
os.environ["GOOGLE_API_VERSION"] = "v1"

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 1. SICHERHEIT ---
ACCESS_PASSWORD = "2681Dtc7978@"


def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    placeholder = st.empty()
    with placeholder.container():
        st.title("RE-Bot Login 🔐")
        pwd = st.text_input("Bitte Passwort eingeben", type="password")
        if st.button("Anmelden"):
            if pwd == ACCESS_PASSWORD:
                st.session_state.password_correct = True
                placeholder.empty()
                st.rerun()
            else:
                st.error("Falsches Passwort")
    return False


# --- 2. RE-LOGIK (SOPHIST) ---
SYSTEM_PROMPT = """Du bist ein Senior RE. Nutze die SOPHIST-Schablone: 
[Bedingung] + [Systemname] + [Muss/Soll/Kann] + [Prozess] + [Objekt]. 
Antworte immer auf Deutsch."""

st.set_page_config(page_title="RE-Bot Stable Fix", page_icon="🤖")

if check_password():
    st.title("Senior RE-Assistant (Gemini) 🤖")

    # API-Key aus Secrets (bevorzugt) oder Sidebar
    google_api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Google API Key", type="password")

    if not google_api_key:
        st.warning("Bitte API Key hinterlegen.")
    else:
        if "llm" not in st.session_state:
            try:
                # Wir erzwingen REST-Transport, das ist in Cloud-Umgebungen stabiler
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=google_api_key,
                    temperature=0.2,
                    transport="rest"
                )
                # Sofortiger Verbindungstest
                llm.invoke([HumanMessage(content="Hi")])
                st.session_state.llm = llm
                st.sidebar.success("Verbindung steht! ✅")
            except Exception as e:
                st.error(f"Technischer Fehler: {str(e)}")
                st.info("Falls dieser Fehler bleibt: Lösche die App in Streamlit und erstelle sie neu.")
                st.stop()

        if "messages" not in st.session_state:
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

        for msg in st.session_state.messages:
            if not isinstance(msg, SystemMessage):
                role = "user" if isinstance(msg, HumanMessage) else "assistant"
                st.chat_message(role).write(msg.content)

        if prompt := st.chat_input("Was soll das System können?"):
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.chat_message("user").write(prompt)
            with st.chat_message("assistant"):
                response = st.session_state.llm.invoke(st.session_state.messages)
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))