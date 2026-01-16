import streamlit as st
# NEU: Google Gemini Integration
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 1. KONFIGURATION & SICHERHEIT ---
ACCESS_PASSWORD = "mein_geheimnis"


def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True

    placeholder = st.empty()
    with placeholder.container():
        st.title("RE-Bot Login")
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
2. Wenn Informationen fehlen, frage HÖFLICH nach genau EINEM fehlenden Teil.
3. Wenn alle Teile da sind, gib die finale Anforderung fettgedruckt aus.
4. Führe ein Review durch (Keine Passivsätze, keine vagen Adjektive, Testbarkeit).
5. Gib am Ende einen Score von 1-10 an.

Antworte immer auf Deutsch."""

# --- 3. UI INITIALISIERUNG ---
st.set_page_config(page_title="SOPHIST RE-Bot (Gemini)", page_icon="🤖")

if check_password():
    st.title("Senior RE-Assistant (Gemini Edition) 🤖")
    st.markdown("---")

    with st.sidebar:
        st.header("Einstellungen")
        # NEU: Google API Key Abfrage
        google_api_key = st.text_input("Google AI Studio API Key", type="password")
        st.info("Hol dir deinen Key hier: https://aistudio.google.com/")

        if st.button("Chat zurücksetzen"):
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.rerun()

    if not google_api_key:
        st.warning("Bitte gib deinen Google API Key in der Sidebar ein.")
    else:
        try:
            # NEU: Initialisierung von Gemini
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=google_api_key,
                temperature=0.2
            )

            if "messages" not in st.session_state:
                st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

            for msg in st.session_state.messages:
                if isinstance(msg, HumanMessage):
                    st.chat_message("user").write(msg.content)
                elif isinstance(msg, AIMessage):
                    st.chat_message("assistant").write(msg.content)

            if prompt := st.chat_input("Beschreibe deine Anforderung..."):
                st.session_state.messages.append(HumanMessage(content=prompt))
                st.chat_message("user").write(prompt)

                with st.chat_message("assistant"):
                    response = llm.invoke(st.session_state.messages)
                    st.write(response.content)
                    st.session_state.messages.append(AIMessage(content=response.content))

                    if "Score" in response.content:
                        st.download_button(
                            label="📥 Als Markdown exportieren",
                            data=response.content,
                            file_name="requirement.md",
                            mime="text/markdown"
                        )
        except Exception as e:
            st.error(f"Fehler bei der Verbindung zu Gemini: {e}")