import streamlit as st
from transformers import pipeline
import requests
from transformers import AutoTokenizer
from huggingface_hub import login

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
HF_TOKEN = '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'

@st.cache_resource  # 👈 Add the caching decorator
def login_e_tokenizer(token):
    login(token = token)
    return AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

tokenizer = login_e_tokenizer(HF_TOKEN)
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{'role':'system','content':"Ola, sou o chatbot em que posso ajudar você?"}]
def query(payload):
    response = requests.post(API_URL, headers=headers,json=payload)
    return response.json()

def append_text():
    st.session_state.mensagens.append({'role':'user','content':st.session_state.pergunta})
    pergunta = tokenizer.apply_chat_template(st.session_state.mensagens, tokenize=False, add_generation_prompt=True)
    data = query({"inputs": pergunta, "parameters": {"max_new_tokens": 500}})
    st.session_state.mensagens.append({'role':'assistant','content':data[0]["generated_text"].split('<|start_header_id|>assistant<|end_header_id|>\n')[-1]})
    # st.session_state.mensagens.append({'name':'assistant','content':data['generated_text']})

# data = query({"inputs": "The answer to the universe is", "parameters": {"max_new_tokens": 500}})
area_texto = st.empty()

with area_texto.container():
    for mensagem in st.session_state.mensagens[::-1]:
        chat = st.chat_message(f"{mensagem['role']}")
        chat.markdown(f"{mensagem['content']}")
    
st.chat_input("Digite sua pergunta", on_submit=append_text, key="pergunta")