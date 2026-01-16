import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 1. KONFIGURATION & SICHERHEIT ---
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


# --- 2. VERFEINERTER SENIOR RE PROMPT ---
SYSTEM_PROMPT = """Du bist ein Senior Requirements Engineer. 
Dein Ziel ist die perfekte Anforderung nach der SOPHIST-Masterschablone.

SCHABLONE: [Bedingung] + [Systemname] + [Muss/Soll/Kann] + [Prozess] + [Objekt].

DEIN EXPERTEN-VERHALTEN:
1. Prüfe den Input: Fehlt ein Teil der Schablone? Frage gezielt nach EINEM Teil.
2. Eliminiere Vagheiten: Verwandle Adjektive wie 'schnell', 'sicher' oder 'benutzerfreundlich' in messbare Zahlen (z.B. 'unter 200ms').
3. Formuliere Aktiv: Keine Passivsätze ("Die Rechnung wird erstellt" -> "Das System muss die Rechnung erstellen").
4. Abschluss: Wenn fertig, gib die Anforderung fett aus, erstelle 3 Akzeptanzkriterien und einen Score (1-10).

Antworte immer auf Deutsch."""

# --- 3. UI INITIALISIERUNG ---
st.set_page_config(page_title="Senior RE-Bot (Resilient Gemini)", page_icon="🤖")

if check_password():
    st.title("Senior RE-Assistant (Gemini) 🤖")
    st.markdown("---")

    # API-Key Logik
    google_api_key = st.secrets.get("GOOGLE_API_KEY") or st.sidebar.text_input("Google API Key", type="password")

    with st.sidebar:
        if "GOOGLE_API_KEY" in st.secrets:
            st.success("Key aus Secrets geladen ✅")
        if st.button("Chat zurücksetzen"):
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.rerun()

    if not google_api_key:
        st.warning("Bitte API Key hinterlegen.")
    else:
        # --- DYNAMISCHE MODELL-AUSWAHL (RESILIENZ) ---
        if "llm" not in st.session_state:
            with st.spinner("Verbindung zu Gemini wird aufgebaut..."):
                # Wir testen zuerst das stabilste Basis-Modell
                model_to_test = "gemini-1.5-flash"
                try:
                    llm_test = ChatGoogleGenerativeAI(
                        model=model_to_test,
                        google_api_key=google_api_key,
                        temperature=0.2
                    )
                    # Der entscheidende Test-Aufruf
                    llm_test.invoke([HumanMessage(content="Hi")])
                    st.session_state.llm = llm_test
                    st.success(f"Verbunden mit {model_to_test}")
                except Exception as e:
                    st.error(f"Kritischer Verbindungsfehler: {str(e)}")
                    st.info(
                        "Tipp: Prüfe in Google AI Studio, ob dein Key aktiv ist und ob Billing (auch für Free Tier) eingerichtet sein muss.")
                    st.stop()

        # Chat-Historie
        if "messages" not in st.session_state:
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                st.chat_message("user").write(msg.content)
            elif isinstance(msg, AIMessage):
                st.chat_message("assistant").write(msg.content)

        if prompt := st.chat_input("Was soll das System können?"):
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.chat_message("user").write(prompt)

            with st.chat_message("assistant"):
                response = st.session_state.llm.invoke(st.session_state.messages)
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))

                if "Score" in response.content:
                    st.download_button("📥 Export .md", response.content, "req.md", "text/markdown")