import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# --- 1. KONFIGURATION & SICHERHEIT ---
# In der Produktion würden wir das über Umgebungsvariablen lösen.
# Hier ein simpler Passwort-Schutz für den Zugang.
ACCESS_PASSWORD = "mein_geheimnis"  # Ändere das für dein Team


def check_password():
    """Gibt True zurück, wenn der Nutzer das richtige Passwort eingegeben hat."""
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
4. Führe AUTOMATISCH ein Review durch (Kriterien: Keine Passivsätze, keine vagen Adjektive wie 'schnell' oder 'effizient', Testbarkeit).
5. Gib am Ende einen Score von 1-10 für die Qualität der Anforderung an.

WICHTIG: Antworte immer auf Deutsch und bleibe in der Rolle des Experten.
"""

# --- 3. UI INITIALISIERUNG ---
st.set_page_config(page_title="SOPHIST RE-Bot", page_icon="📝")

if check_password():
    st.title("Senior RE-Assistant 🤖")
    st.markdown("---")

    # API Key Handling in der Sidebar
    with st.sidebar:
        st.header("Einstellungen")
        api_key = st.text_input("OpenAI API Key", type="password")
        st.info("Dieser Bot nutzt die SOPHIST-Methode zur Anforderungserhebung.")

        if st.button("Chat zurücksetzen"):
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
            st.rerun()

    if not api_key:
        st.warning("Bitte gib deinen OpenAI API Key in der Sidebar ein.")
    else:
        # LLM Setup
        llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key, temperature=0.2)

        # Chat-Historie verwalten
        if "messages" not in st.session_state:
            st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

        # Chat anzeigen
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                st.chat_message("user").write(msg.content)
            elif isinstance(msg, AIMessage):
                st.chat_message("assistant").write(msg.content)

        # Input-Logik
        if prompt := st.chat_input("Beschreibe deine Anforderung..."):
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.chat_message("user").write(prompt)

            with st.chat_message("assistant"):
                response = llm.invoke(st.session_state.messages)
                st.write(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))

                # Prüfen, ob die Anforderung "fertig" ist (Trigger im Prompt)
                # Falls ja, zeigen wir einen Export-Button an
                if "Gesamt-Score" in response.content:
                    st.download_button(
                        label="📥 Anforderung als Markdown exportieren",
                        data=response.content,
                        file_name="requirement_export.md",
                        mime="text/markdown"
                    )