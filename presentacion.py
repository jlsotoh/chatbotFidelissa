import streamlit as st
from streamlit_chat import message
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from openai import OpenAI
import pymupdf

# create an OpenAI client using the API key
client = OpenAI()


os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="Presentación Fidelissa",
    page_icon="🧊",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.fidelissamarketing/help",
        "Report a bug": "https://www.fidelissamarketing.com/bug",
        "About": "Chatbot fidelisssa!",
    },
)

st.html(
    "<div style='display: flex; justify-content: space-between;'><div><h1>Fidelissa Marketing</h1><span>Puedes realizarme preguntas relacionadas a mi</span></div><div><img width='130' src='https://ideeo.mx/bbva/chatbot/img/chat.png'></div></div>"
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


def extract_text_from_pdf(pdf_path):
    """Read table content only of all pages in the document.

    Chatbots typically have limitations on the amount of data that can
    can be passed in (number of tokens).

    We therefore only extract information on the PDF's pages that are
    contained in tables.
    As we even know that the PDF actually contains ONE logical table
    that has been segmented for reporting purposes, our approach
    is the following:
    * The cell contents of each table row are joined into one string
      separated by ";".
    * If table segment on the first page also has an external header row,
      join the column names separated by ";". Also ignore any subsequent
      table row that equals the header string. This deals with table
      header repeat situations.
    """
    # open document
    doc = pymupdf.open(pdf_path)

    text = ""  # we will return this string
    row_count = 0  # counts table rows
    header = ""  # overall table header: output this only once!

    # iterate over the pages
    for page in doc:
        # only read the table rows on each page, ignore other content
        if page is not None:
            tables = page.find_tables()  # a "TableFinder" object
            if tables is not None:
                for table in tables:
                    # on first page extract external column names if present
                    if page.number == 0 and table.header.external:
                        # build the overall table header string
                        # technical note: incomplete / complex tables may have
                        # "None" in some header cells. Just use empty string then.
                        header = (
                            ";".join(
                                [
                                    name if name is not None else ""
                                    for name in table.header.names
                                ]
                            )
                            + "\n"
                        )
                        text += header
                        row_count += 1  # increase row counter

                    # output the table body
                    for row in table.extract():  # iterate over the table rows
                        # again replace any "None" in cells by an empty string
                        row_text = (
                            ";".join([cell if cell is not None else "" for cell in row])
                            + "\n"
                        )
                        if row_text != header:  # omit duplicates of header row
                            text += row_text
                            row_count += 1  # increase row counter

    doc.close()  # close document
    print(f"Loaded {row_count} table rows from file '{doc.name}'.\n")
    return text


# use model "gpt-3.5-turbo-instruct" for text
def generate_response_with_chatgpt(prompt):
    response = client.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Choose appropriate model
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()


filename = "fidelissa presentacion.pdf"
pdf_text = extract_text_from_pdf(filename)


def conversational_chat(query):
    prompt = pdf_text + "\n\n" + query
    response = generate_response_with_chatgpt(prompt)
    print("Response:\n")
    print("result", response)
    return response


if "history" not in st.session_state:
    st.session_state["history"] = []

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

# container for the chat history
response_container = st.container()
# container for the user's text input
container = st.container()

with container:
    with st.form(key="my_form", clear_on_submit=True):

        user_input = st.text_input(
            "¿En qué te puedo ayudar?:",
            placeholder="Pulsa Enviar para hacer la pregunta",
            key="input",
        )
        submit_button = st.form_submit_button(label="Enviar")

    if submit_button and user_input:
        output = conversational_chat(user_input)

        st.session_state["past"].append(user_input)
        st.session_state["generated"].append(output)

if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state["generated"])):
            message(
                st.session_state["past"][i],
                is_user=True,
                key=str(i) + "_user",
                avatar_style="initials",
                seed="Asesor",
            )
            message(
                st.session_state["generated"][i],
                key=str(i),
            )
