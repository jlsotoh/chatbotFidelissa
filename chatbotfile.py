import streamlit as st
from streamlit_chat import message
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.chains import ConversationalRetrievalChain
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
import chromadb
from uuid import uuid4

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="Chatbot Fidelissa",
    page_icon="®",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)

st.html(
    "<div style='display: flex; justify-content: space-between; align-items: center;'><div><h1>Chat Fidelissa</h1><span>Puedes realizarme preguntas relacionadas con la empresa</span></div><div><img width='130' src='https://media.devstech.net/images/fidelissa.png'></div></div>"
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

    
    
    </style>
"""
st.markdown(page_header_config, unsafe_allow_html=True)


# Load the PDF file
pdf_loader = PyMuPDFLoader("./fidelissa-presentacion.pdf")
data = pdf_loader.load()

# chroma_client = chromadb.Client()
client = chromadb.PersistentClient(path="presentacionFidelissa")
# Check if the collection already exists and use it; otherwise, create a new one
if len(client.list_collections()) == 0:
    collection = client.create_collection(name="fidelissa")
else:
    for campo in client.list_collections():
        print(campo)
        if "fidelissa" in campo.name:
            collection = client.get_collection(name="fidelissa")
            print("collection: ", collection)


# split the documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(data)

# Extract the text content from each Document object and ensure they are strings
text_contents = [str(text.page_content) for text in texts]

# Generate unique IDs for each document chunk
ids = [str(uuid4()) for _ in range(len(text_contents))]

embedding_model = OpenAIEmbeddings()

# Generate embeddings for each text content
embeddings = embedding_model.embed_documents(text_contents)

collection.add(documents=text_contents, embeddings=embeddings, ids=ids)

# Fine-tune the LLM on your PDF data
chat_openai = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
)


def conversational_chat(query):
    query_embedding = embedding_model.embed_query(query)

    # Perform a similarity search in the collection
    results = collection.query(query_embeddings=[query_embedding], n_results=2)
    # Extract relevant documents from the results
    retrieved_documents = results["documents"]

    # Ensure that retrieved_documents is a list of strings
    # If each document is a list, extract the text from each list
    text_contents = []
    for doc in retrieved_documents:
        if isinstance(doc, list):
            # If the document is a list of strings, join them
            text_contents.append(" ".join(doc))
        else:
            # Otherwise, assume it's a string and add it directly
            text_contents.append(str(doc))

    # Concatenate the retrieved documents into a single string
    context = "\n\n".join(text_contents)
    print("context: ", context)
    # Create the prompt for GPT-4 or GPT-3.5
    prompt = f"Here are some relevant documents related to the query:\n\n{context}\n\nBased on this information, please answer the following question: {query}"

    # Create messages for the conversation
    messages = [
        SystemMessage(
            content="""
                      You are an assistant. 
                      * if you have to make any clarification or return any text, always in Spanish
                      * if you don't have the answer, look for one that matches the question asked
                    """
        ),
        HumanMessage(content=prompt),
    ]

    # Generate the response
    response = chat_openai(messages)

    # Extract the content of the response
    answer = response.content

    # Display the answer
    print("Generated Response:")
    print(answer)

    return answer


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
