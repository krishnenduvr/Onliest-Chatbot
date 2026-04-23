import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import uuid

CURRENT_DIR = Path(__file__).resolve().parent
SEARCH_PATHS = [path for path in sys.path if Path(path).resolve() != CURRENT_DIR]
STREAMLIT_SPEC = importlib.machinery.PathFinder.find_spec("streamlit", SEARCH_PATHS)
if STREAMLIT_SPEC is None or STREAMLIT_SPEC.loader is None:
    raise ImportError("The Streamlit package is not installed in this environment.")
st = importlib.util.module_from_spec(STREAMLIT_SPEC)
sys.modules["streamlit"] = st
STREAMLIT_SPEC.loader.exec_module(st)

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from chatbot.engine import get_response


st.set_page_config(
    page_title="Aurora Chat",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def init_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"streamlit-{uuid.uuid4().hex[:8]}"
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Welcome! Ask me anything and I will help you in a conversational way.",
            }
        ]
    if "conversations" not in st.session_state:
        conversation_id = f"chat-{uuid.uuid4().hex[:8]}"
        st.session_state.conversations = {
            conversation_id: {
                "title": "New chat",
                "messages": list(st.session_state.messages),
            }
        }
        st.session_state.active_conversation_id = conversation_id
    if "active_conversation_id" not in st.session_state:
        st.session_state.active_conversation_id = next(iter(st.session_state.conversations))
    if "nav" not in st.session_state:
        st.session_state.nav = "Chat"
    if "draft_prompt" not in st.session_state:
        st.session_state.draft_prompt = ""
    if "queued_prompt" not in st.session_state:
        st.session_state.queued_prompt = ""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Light"


def conversation_title(messages):
    for message in messages:
        if message["role"] == "user":
            text = message["content"].strip()
            return text[:36] + ("..." if len(text) > 36 else "")
    return "New chat"


def queue_prompt():
    prompt = st.session_state.draft_prompt.strip()
    if prompt:
        st.session_state.queued_prompt = prompt
    st.session_state.draft_prompt = ""


def sync_active_conversation():
    active_id = st.session_state.active_conversation_id
    st.session_state.conversations[active_id] = {
        "title": conversation_title(st.session_state.messages),
        "messages": list(st.session_state.messages),
    }


def start_new_conversation():
    conversation_id = f"chat-{uuid.uuid4().hex[:8]}"
    fresh_messages = [
        {
            "role": "assistant",
            "content": "Fresh chat started. What would you like to explore?",
        }
    ]
    st.session_state.conversations[conversation_id] = {
        "title": "New chat",
        "messages": list(fresh_messages),
    }
    st.session_state.active_conversation_id = conversation_id
    st.session_state.messages = fresh_messages


def load_conversation(conversation_id):
    st.session_state.active_conversation_id = conversation_id
    st.session_state.messages = list(st.session_state.conversations[conversation_id]["messages"])


def inject_styles():
    is_dark = st.session_state.theme_mode == "Dark"
    theme = {
        "app_bg": (
            "radial-gradient(circle at top left, rgba(220, 38, 38, 0.12), transparent 30%),"
            " radial-gradient(circle at bottom right, rgba(168, 85, 247, 0.16), transparent 28%),"
            " linear-gradient(135deg, #0f0f12 0%, #17111a 45%, #1b1116 100%)"
            if is_dark
            else "radial-gradient(circle at top left, rgba(220, 38, 38, 0.10), transparent 30%),"
            " radial-gradient(circle at bottom right, rgba(244, 114, 182, 0.14), transparent 28%),"
            " linear-gradient(135deg, #ffffff 0%, #fff7f7 45%, #fff1f2 100%)"
        ),
        "text": "#f7e9ee" if is_dark else "#31111a",
        "sidebar_bg": "linear-gradient(180deg, #181117 0%, #22131a 100%)" if is_dark else "linear-gradient(180deg, #fff5f5 0%, #ffe4e6 100%)",
        "sidebar_text": "#f7e9ee" if is_dark else "#31111a",
        "sidebar_border": "rgba(244, 114, 182, 0.10)" if is_dark else "rgba(220, 38, 38, 0.08)",
        "card_bg": "rgba(28, 18, 24, 0.88)" if is_dark else "rgba(255, 255, 255, 0.86)",
        "card_border": "rgba(244, 114, 182, 0.10)" if is_dark else "rgba(220, 38, 38, 0.08)",
        "card_shadow": "0 12px 32px rgba(0, 0, 0, 0.20)" if is_dark else "0 12px 32px rgba(220, 38, 38, 0.06)",
        "section_title": "#fda4af" if is_dark else "#991b1b",
        "mini_note": "#e9c7d1" if is_dark else "#6b3b46",
        "shell_bg": "rgba(28, 18, 24, 0.92)" if is_dark else "rgba(255,255,255,0.92)",
        "shell_border": "rgba(244, 114, 182, 0.12)" if is_dark else "rgba(220, 38, 38, 0.10)",
        "shell_shadow": "0 18px 35px rgba(0, 0, 0, 0.20)" if is_dark else "0 18px 35px rgba(220, 38, 38, 0.06)",
        "input_bg": "#140f13" if is_dark else "#ffffff",
        "input_border": "rgba(244, 114, 182, 0.16)" if is_dark else "rgba(220, 38, 38, 0.16)",
        "chat_border": "rgba(244, 114, 182, 0.08)" if is_dark else "rgba(220, 38, 38, 0.08)",
        "chat_shadow": "0 8px 22px rgba(0, 0, 0, 0.18)" if is_dark else "0 8px 22px rgba(220, 38, 38, 0.06)",
        "chat_user_bg": "linear-gradient(135deg, #3b0a19 0%, #5b1124 100%)" if is_dark else "linear-gradient(135deg, #ffe4e6 0%, #fecdd3 100%)",
        "chat_user_text": "#ffe4ea" if is_dark else "#881337",
        "chat_assistant_bg": "#181116" if is_dark else "#ffffff",
        "nav_caption": "rgba(251, 113, 133, 0.78)" if is_dark else "rgba(153, 27, 27, 0.72)",
        "secondary_bg": "rgba(255,255,255,0.05)" if is_dark else "rgba(255,255,255,0.72)",
        "secondary_hover": "rgba(255,255,255,0.10)" if is_dark else "rgba(255,255,255,0.92)",
        "secondary_text": "#f7e9ee" if is_dark else "#7f1d1d",
        "secondary_border": "rgba(244, 114, 182, 0.18)" if is_dark else "rgba(220, 38, 38, 0.16)",
        "secondary_hover_border": "rgba(251, 113, 133, 0.26)" if is_dark else "rgba(220, 38, 38, 0.24)",
        "secondary_shadow": "0 10px 24px rgba(0, 0, 0, 0.18)" if is_dark else "0 10px 24px rgba(220, 38, 38, 0.08)",
        "settings_bg": "rgba(35, 22, 29, 0.78)" if is_dark else "rgba(255,255,255,0.68)",
        "settings_border": "rgba(244, 114, 182, 0.14)" if is_dark else "rgba(220, 38, 38, 0.10)",
        "settings_title": "#fda4af" if is_dark else "#991b1b",
        "status_bg": "rgba(244, 114, 182, 0.14)" if is_dark else "rgba(220, 38, 38, 0.10)",
        "status_text": "#fecdd3" if is_dark else "#991b1b",
        "divider": "rgba(244, 114, 182, 0.12)" if is_dark else "rgba(220, 38, 38, 0.10)",
    }
    css = f"""
    <style>
    .stApp {{
        background: {theme["app_bg"]};
        color: {theme["text"]};
    }}
    [data-testid="stSidebar"] {{
        background: {theme["sidebar_bg"]};
        color: {theme["sidebar_text"]};
        border-right: 1px solid {theme["sidebar_border"]};
        min-width: 260px;
        max-width: 260px;
    }}
    [data-testid="stSidebar"] * {{
        color: {theme["sidebar_text"]} !important;
    }}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1080px;
    }}
    .hero-card {{
        padding: 1.3rem 1.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.96), rgba(220, 38, 38, 0.88));
        color: #ffffff;
        box-shadow: 0 20px 45px rgba(220, 38, 38, 0.16);
        border: 1px solid rgba(255,255,255,0.16);
    }}
    .hero-title {{
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        letter-spacing: -0.03em;
    }}
    .hero-subtitle {{
        font-size: 1rem;
        line-height: 1.7;
        color: rgba(255,255,255,0.86);
    }}
    .chip-row {{
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }}
    .chip {{
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.15);
        font-size: 0.85rem;
    }}
    .glass-card,
    .company-card {{
        padding: 1.2rem;
        border-radius: 22px;
        background: {theme["card_bg"]};
        backdrop-filter: blur(10px);
        border: 1px solid {theme["card_border"]};
        box-shadow: {theme["card_shadow"]};
    }}
    .section-title,
    .company-title {{
        color: {theme["section_title"]};
    }}
    .section-title {{
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }}
    .company-title {{
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }}
    .mini-note {{
        color: {theme["mini_note"]};
        font-size: 0.95rem;
        line-height: 1.6;
    }}
    .input-shell {{
        padding: 0.9rem;
        border-radius: 22px;
        background: {theme["shell_bg"]};
        border: 1px solid {theme["shell_border"]};
        box-shadow: {theme["shell_shadow"]};
    }}
    .stTextInput > div > div > input {{
        background: {theme["input_bg"]};
        color: {theme["text"]};
        border: 1px solid {theme["input_border"]};
        border-radius: 16px;
        min-height: 50px;
    }}
    .stButton > button {{
        border-radius: 16px;
        font-weight: 600;
        min-height: 50px;
        transition: all 0.2s ease;
    }}
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #dc2626 0%, #fb7185 100%);
        color: #ffffff !important;
        border: 0;
        box-shadow: 0 14px 26px rgba(220, 38, 38, 0.18);
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #b91c1c 0%, #e11d48 100%);
        color: #ffffff !important;
        transform: translateY(-1px);
    }}
    .stButton > button[kind="secondary"] {{
        background: {theme["secondary_bg"]};
        color: {theme["secondary_text"]} !important;
        border: 1px solid {theme["secondary_border"]};
        box-shadow: {theme["secondary_shadow"]};
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: {theme["secondary_hover"]};
        color: {theme["secondary_text"]} !important;
        border-color: {theme["secondary_hover_border"]};
        transform: translateY(-1px);
    }}
    .stChatMessage,
    .chat-bubble {{
        border-radius: 20px;
        border: 1px solid {theme["chat_border"]};
        box-shadow: {theme["chat_shadow"]};
    }}
    .chat-bubble {{
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
    }}
    .chat-user {{
        background: {theme["chat_user_bg"]};
        color: {theme["chat_user_text"]};
    }}
    .chat-assistant {{
        background: {theme["chat_assistant_bg"]};
        color: {theme["text"]};
    }}
    .chat-role {{
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.75;
        margin-bottom: 0.45rem;
        font-weight: 700;
    }}
    .nav-caption {{
        padding: 0.3rem 0 1rem 0;
        color: {theme["nav_caption"]};
        font-size: 0.92rem;
        line-height: 1.6;
    }}
    .theme-label {{
        margin: 1rem 0 0.55rem 0;
        color: {theme["settings_title"]};
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("## Aurora Chat")
        st.markdown(
            '<div class="nav-caption">An AI chatbot powered by your backend, ready to answer questions and keep every conversation flowing.</div>',
            unsafe_allow_html=True,
        )
        st.session_state.nav = st.radio(
            "Navigation",
            ["Chat", "About", "Contact"],
            index=["Chat", "About", "Contact"].index(st.session_state.nav),
            label_visibility="collapsed",
        )
        st.markdown('<div class="theme-label">&#9881; Theme</div>', unsafe_allow_html=True)
        light_col, dark_col = st.columns(2)
        with light_col:
            if st.button(
                "Light Mode",
                key="theme_light",
                type="primary" if st.session_state.theme_mode == "Light" else "secondary",
                use_container_width=True,
            ):
                if st.session_state.theme_mode != "Light":
                    st.session_state.theme_mode = "Light"
                    safe_rerun()
        with dark_col:
            if st.button(
                "Dark Mode",
                key="theme_dark",
                type="primary" if st.session_state.theme_mode == "Dark" else "secondary",
                use_container_width=True,
            ):
                if st.session_state.theme_mode != "Dark":
                    st.session_state.theme_mode = "Dark"
                    safe_rerun()


def render_hero():
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">ONLIEST CHATBOT</div>
            <div class="hero-subtitle">
                A polished assistant experience inspired by Onliest World's blend of luxury fashion
                and advanced technology.
            </div>
            <div class="chip-row">
                <div class="chip">Luxury Fashion Tech</div>
                <div class="chip">AI-led Experience</div>
                <div class="chip">Conversation Memory</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_company_details():
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(
            """
            <div class="company-card">
                <div class="company-title">About Onliest World</div>
                <div class="mini-note">
                    Onliest World presents itself as a luxury fashion technology company focused on
                    timeless elegance through advanced technology, AI-powered 3D modelling, AR,
                    virtual try-on, and smart manufacturing.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="company-card">
                <div class="company-title">Focus Areas</div>
                <div class="mini-note">
                    Apparel, footwear, leather goods, jewelry, furniture, accessories,
                    AI design intelligence, integrated systems, and premium customer experience.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_quick_prompts():
    st.markdown('<div class="section-title">Popular Questions</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    prompts = [
        "What does Onliest World do?",
        "What products and services does Onliest World offer?",
        "Where are Onliest World's office locations?",
        "How can I contact Onliest World?",
    ]
    for col, prompt in zip(cols, prompts):
        with col:
            if st.button(prompt, use_container_width=True):
                handle_prompt(prompt)


def handle_prompt(prompt):
    prompt = prompt.strip()
    if not prompt:
        return
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = get_response(st.session_state.user_id, prompt)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    sync_active_conversation()
    safe_rerun()


def render_chat():
    outer_left, center_col, outer_right = st.columns([1.2, 4.6, 1.2])
    with center_col:
        intro_message = None
        remaining_messages = list(st.session_state.messages)
        if (
            remaining_messages
            and remaining_messages[0]["role"] == "assistant"
            and "welcome" in remaining_messages[0]["content"].lower()
        ):
            intro_message = remaining_messages[0]
            remaining_messages = remaining_messages[1:]

        if intro_message is not None:
            st.markdown(
                f"""
                <div class="chat-bubble chat-assistant">
                    <div class="chat-role">Assistant</div>
                    <div>{intro_message["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        input_col, refresh_col = st.columns([6, 1])
        with input_col:
            st.text_input(
                "Ask anything...",
                key="draft_prompt",
                on_change=queue_prompt,
                placeholder="Type your question and press Enter",
                label_visibility="collapsed",
            )
        with refresh_col:
            if st.button("Refresh", key="refresh_main", use_container_width=True):
                safe_rerun()
        if st.session_state.queued_prompt:
            prompt = st.session_state.queued_prompt
            st.session_state.queued_prompt = ""
            handle_prompt(prompt)

        chat_blocks = []
        pending_user = None
        for message in remaining_messages:
            if message["role"] == "user":
                if pending_user is not None:
                    chat_blocks.append((pending_user, None))
                pending_user = message
            else:
                if pending_user is not None:
                    chat_blocks.append((pending_user, message))
                    pending_user = None
                else:
                    chat_blocks.append((None, message))
        if pending_user is not None:
            chat_blocks.append((pending_user, None))

        with st.container():
            for user_message, assistant_message in reversed(chat_blocks):
                for message in (user_message, assistant_message):
                    if message is None:
                        continue
                    if hasattr(st, "chat_message"):
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
                    else:
                        role_label = "You" if message["role"] == "user" else "Assistant"
                        role_class = "chat-user" if message["role"] == "user" else "chat-assistant"
                        st.markdown(
                            f"""
                            <div class="chat-bubble {role_class}">
                                <div class="chat-role">{role_label}</div>
                                <div>{message["content"]}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


def render_about():
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">About This App</div>
            <div class="mini-note">
                ONLIEST CHATBOT is designed around the vision of Onliest World, a company focused on
                crafting timeless elegance through advanced technology. Their public site highlights
                AI-powered 3D modelling, AR, virtual try-on, smart manufacturing, integrated systems,
                and customer-first luxury fashion experiences across apparel, footwear, leather goods,
                jewelry, furniture, and accessories.
                <br><br>
                Website:
                <a href="https://onliestworld.com/" target="_blank" style="color:#d9b08c;">https://onliestworld.com/</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_contact():
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Contact</div>
            <div class="mini-note">
                <strong>Email:</strong> hr@onliestworld.com | <strong>Mobile:</strong> +91 6303271104<br><br>
                <strong>Corporate Office:</strong> 9711 Washingtonian Blvd suite 550 Gaithersburg MD, 20878, United States<br><br>
                <strong>Technology Center:</strong> 7th Floor, Building No. 32, RMZ Ecoworld, Devarabisanahalli, Bengaluru, Karnataka 560103<br><br>
                <strong>Operations Center:</strong> D No: 50-28-23, Opp. Lane of Karur Vysya Bank, TPT Colony, Balayya Sastri Layout, Seethammadara, Visakhapatnam 530013<br><br>
                <strong>Manufacturing Facility:</strong> UAE (Coming soon)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    init_state()
    inject_styles()
    render_sidebar()
    render_hero()
    st.write("")

    if st.session_state.nav == "Chat":
        render_quick_prompts()
        st.write("")
        render_chat()
    elif st.session_state.nav == "About":
        render_about()
    else:
        render_contact()


if __name__ == "__main__":
    main()
