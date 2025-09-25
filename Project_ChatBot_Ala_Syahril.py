import streamlit as st
import requests
import json

# ===============================
# FUNCTION: Call API OpenRouter
# ===============================
def get_ai_response(messages_payload, model, debug=False):
    api_key = st.secrets["openrouter"]["api_key"]

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        data=json.dumps({
            "model": model,
            "messages": messages_payload,
            "max_tokens": 1000,
            "temperature": 0.7,
        })
    )

    if response.status_code != 200:
        st.error(f"Error API ({response.status_code}): {response.text[:200]}...")
        return None

    try:
        resp_json = response.json()
        if debug:
            st.write("🔎 Debug JSON:", resp_json)

        if "choices" in resp_json and len(resp_json["choices"]) > 0:
            if "message" in resp_json["choices"][0]:
                return resp_json["choices"][0]["message"]["content"]
            elif "text" in resp_json["choices"][0]:
                return resp_json["choices"][0]["text"]

        st.error("⚠️ Format respons AI tidak sesuai.")
    except Exception as e:
        st.error(f"Gagal parsing JSON: {e}")
        if debug:
            st.write(response.text)
    return None


# ===============================
# APP TITLE
# ===============================
st.title("🤖 Chatbot ala Syahril")

# ===============================
# OPTIONS: Personality
# ===============================
personality_options = {
    "Ceria & Humor": "Kamu adalah asisten yang ceria, sopan, dan humoris. Jawabanmu ramah dan mudah dimengerti.",
    "Serius & Profesional": "Kamu adalah asisten yang serius, profesional, dan menjawab dengan jelas dan tepat.",
    "Guru Sabar": "Kamu adalah guru yang sabar, menjelaskan dengan rinci dan memberi contoh yang mudah dimengerti."
}

selected_personality = st.selectbox(
    "Pilih Personality AI",
    options=list(personality_options.keys()),
    index=0
)

# ===============================
# OPTIONS: Model
# ===============================
model_options = {
    "Mistral 7B (Free)": "mistralai/mistral-7b-instruct:free",
    "DeepSeek V3 (Free)": "deepseek/deepseek-chat-v3-0324:free",
    "Llama 3.1 8B (Free)": "meta-llama/llama-3.1-8b-instruct:free"
}

selected_model_name = st.selectbox(
    "Pilih Model",
    options=list(model_options.keys()),
    index=0,
)
selected_model = model_options[selected_model_name]

# ===============================
# DEBUG MODE
# ===============================
debug = st.sidebar.checkbox("Debug Mode")

# ===============================
# SESSION STATE INIT
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_personality" not in st.session_state:
    st.session_state.selected_personality = selected_personality

# Reset chat kalau personality berubah
if st.session_state.selected_personality != selected_personality:
    st.session_state.messages = []
    st.session_state.selected_personality = selected_personality

# System message (hanya sekali)
system_message = {
    "role": "system",
    "content": personality_options[selected_personality]
}


# ===============================
# Tombol Reset 
# ===============================
if st.button("🔄 Reset Chat"):
    st.session_state.messages = []
    st.rerun()


# ===============================
# DISPLAY CHAT HISTORY
# ===============================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===============================
# HANDLE USER INPUT
# ===============================
if prompt := st.chat_input("Tulis pesan..."):
    # simpan user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})

    # tampilkan user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # dapatkan respons AI
    with st.chat_message("assistant"):
        with st.spinner("Berpikir..."):
            messages_for_api = [system_message] + st.session_state.messages.copy()
            ai_response = get_ai_response(messages_for_api, selected_model, debug)

            if ai_response:
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            else:
                st.error("Error: Gagal mendapatkan respons dari AI")
