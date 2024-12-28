import backend
import streamlit as st
from streamlit_chat import message

st.set_page_config(
    page_title="Chatbot MDV",
    page_icon="🧊",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)

st.html(
    "<div style='display: flex; justify-content: space-between;'><div><h1>Chat Modelo de Ventas</h1><span>Puedes realizarme preguntas relacionadas a los materiales existentes</span></div><div><img width='130' src='https://ideeo.mx/bbva/chatbot/img/chat.png'></div></div>"
)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;} 
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

page_header_config = """
    <style>
    [data-testid="stHeader"]{  
        background-color: #072146;
        color: #fff; 
        height:60px;
        width: 100%;
    }

    [data-testid="stDecoration"]{
        position: fixed;
        background-image: url(https://ideeo.mx/bbva/chatbot/img/logoBBVA.png);
        width: 100px;
        z-index: 999990;
        height: 20px;
        background-size: contain;
        background-repeat: no-repeat;
        top: 18px;
        left: calc(30% - 50px);
    }
    
    </style>
"""
st.markdown(page_header_config, unsafe_allow_html=True)

if "preguntas" not in st.session_state:
    st.session_state.preguntas = []
if "respuestas" not in st.session_state:
    st.session_state.respuestas = []


def click():
    if st.session_state.user != "":
        pregunta = st.session_state.user
        respuesta = backend.consulta(pregunta)

        st.session_state.preguntas.append(pregunta)
        st.session_state.respuestas.append(respuesta)

        # Limpiar el input de usuario después de enviar la pregunta
        st.session_state.user = ""


with st.form("my-form"):
    query = st.text_input(
        "¿En qué te puedo ayudar?",
        key="user",
        help="Pulsa Enviar para hacer la pregunta",
    )
    submit_button = st.form_submit_button("Enviar", on_click=click)

if st.session_state.preguntas:
    for i in range(len(st.session_state.respuestas) - 1, -1, -1):
        message(st.session_state.respuestas[i], key=str(i))

    # Opción para continuar la conversación
    continuar_conversacion = st.checkbox("Quieres hacer otra pregunta?")
    if not continuar_conversacion:
        st.session_state.preguntas = []
        st.session_state.respuestas = []
