import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 1. KONFIGURATION & SICHERHEIT ---
# Das Passwort für den Zugang zur Web-App
ACCESS_PASSWORD = "mein_geheimnis"


def check_password():
    """Prüft das Passwort und gibt den App-Inhalt nur bei Erfolg frei."""
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


# --- 2. DER SENIOR RE PROMPT (SOPHIST LOGIK) ---
SYSTEM_PROMPT = """Du bist ein Senior Requirements Engineer. 
Dein Ziel ist es, Anforderungen exakt nach der SOPHIST-Masterschablone zu formulieren.

DIE SCHABLONE:
[Bedingung] + [Systemname] + [Modalverb: muss/soll/kann] + [Prozess/Funktion] + [Objekt].

DEIN WORKFLOW:
1. Analysiere den Input des Nutzers.
2. Wenn Informationen fehlen, frage HÖFLICH nach genau EINEM fehlenden Teil der Schablone.
3. Wenn alle Informationen vorliegen, gib die finale Anforderung fettgedruckt aus.
4. Führe ein Review durch: Prüfe auf Passivsätze und vage Begriffe (z.B. 'schnell', 'benutzerfreundlich').
5. Gib am Ende einen Qualitäts-Score von 1-10 an.

Antworte immer auf Deutsch und bleibe professionell."""

# --- 3. UI INITIALISIERUNG ---
st.set_page_config(page_title="SOPHIST RE-Bot (Gemini)", page_icon="🤖")

if check_password():
    st.title("Senior RE-Assistant (Gemini) 🤖")
    st.markdown("---")

    # API-Key Logik: Erst Secrets prüfen, dann Sidebar-Input
    google_api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        google_api_key = st.secrets["GOOGLE_API_KEY"]

    with st.sidebar:
        st.header("Einstellungen")
        if not google_api_key:
            google_api_key = st.text_input("Google API Key", type="password")
        else:
            st.success("API Key aus Secrets geladen ✅")

        if st.button("Chat zurücksetzen"):
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.rerun()

    if not google_api_key:
        st.warning("Bitte gib einen Google API Key ein, um zu starten.")
    else:
        try:
            # Gemini Modell initialisieren
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=google_api_key,
                temperature=0.2
            )

            # Chat-Verlauf im Speicher halten
            if "messages" not in st.session_state:
                st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

            # Verlauf anzeigen
            for msg in st.session_state.messages:
                if isinstance(msg, HumanMessage):
                    st.chat_message("user").write(msg.content)
                elif isinstance(msg, AIMessage):
                    st.chat_message("assistant").write(msg.content)

            # Nutzer-Eingabe verarbeiten
            if prompt := st.chat_input("Was soll das System können?"):
                st.session_state.messages.append(HumanMessage(content=prompt))
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    response = llm.invoke(st.session_state.messages)
                    st.write(response.content)
                    st.session_state.messages.append(AIMessage(content=response.content))

                    # Export-Option bei fertiger Anforderung
                    if "Score" in response.content:
                        st.download_button(
                            label="📥 Anforderung exportieren",
                            data=response.content,
                            file_name="requirement.md",
                            mime="text/markdown"
                        )
        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")