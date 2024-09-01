import streamlit as st
import pathlib
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from etc import create_retriever
from langchain_ollama import ChatOllama
from langchain.memory import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
import tempfile

SESSION_ID = "1K"
FILES_PATH = pathlib.Path(__file__).parents[0] / "files"

@st.cache_resource
def create_ollama():
    return ChatOllama(base_url="http://217.196.62.39:11434",model="llama3.1")

def retriever(files):
    st.session_state.retriever = create_retriever(files)
    print("sucessful creation")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

prompt = PromptTemplate.from_template( """
    Answer this question: {question}
                                      
    Context: {context}
"""
)

contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is.\
If question starts with 'Nos documentos', ignore chat history and return the question as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

qa_system_prompt = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\
answer everything in brazilian portuguese.\
give the name of documents that you used to answer the question.\

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

@st.cache_resource
def create_chain():
    llm = create_ollama()

    history_aware_retriever = create_history_aware_retriever(llm, st.session_state.retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    rag_with_history = RunnableWithMessageHistory(
        rag_chain, 
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
        output_messages_key="answer",)
    
    return rag_with_history

def get_session_history(session_id):
    return st.session_state.messages

    

st.set_page_config(layout="centered")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
)

if not 'files' in st.session_state:
    st.session_state.files = []

# TODO: create layout

def main_chat():

    if not 'messages' in st.session_state:
        st.session_state.messages = ChatMessageHistory()


    container = st.container(border=True)
    

    
    if 'retriever' not in st.session_state:
        container.warning("Please upload a file first")
        st.stop()
    question = st.chat_input()
    mensagens = st.session_state.messages.messages
    print(mensagens)

    for message in mensagens:
        container.chat_message(message.type).write(message.content)

    if question:
        chain = create_chain()
        container.chat_message("user").write(question)
        container.chat_message("system").write("Thinking...")
        chain.invoke({"input": question}, config =  {'configurable': {'session_id': SESSION_ID}})
        st.rerun()

def sidebar():
    with st.sidebar:
        st.title("**Configuration**")
        with st.expander("Upload your pdf file", icon=":material/folder:"):
            uploaded_file = st.file_uploader("Choose a file", type=['pdf'], accept_multiple_files=True)
            st.button("Upload and ask", on_click=save_files, args=(uploaded_file,))

        with st.expander("Uploaded files", icon=":material/folder_open:",expanded=True):
            
            if any(st.session_state.files):
                for file in st.session_state.files:
                    st.write(f':page_facing_up: {file.name}')
                
                # for file in st.session_state.files:
                #     col1, col2 = st.columns([0.8, 0.2])
                #     with st.container():
                #         with col1:
                #             st.write(f':page_facing_up: {file.name}')
                #         with col2:
                #             st.button(f':x:', on_click=file.unlink,key=file.name)
            else:
                st.warning("No files uploaded yet")
            # st.button("Load files into database", on_click=retriever, args=(st.session_state.files,))
           

def save_files(uploaded_file):
    print("saving file!!!!")
    if uploaded_file:
        with tempfile.TemporaryDirectory() as tmpdirname:
            TEMPDIR_PATH = pathlib.Path(tmpdirname)
            for file in uploaded_file:
                st.session_state.files.append(file)
                with open(TEMPDIR_PATH / file.name, "wb") as f:
                    f.write(file.read())
            # create retriever with these files
            retriever(TEMPDIR_PATH.glob("*.pdf"))
                
        
    else:
        st.warning("Please upload a file")


if __name__ == "__main__":
    sidebar()
    main_chat()
