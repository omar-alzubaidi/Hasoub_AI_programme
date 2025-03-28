import os
import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores.faiss import FAISS
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

# Page Configuration
st.set_page_config(page_title="Hasoub Books - Personal Assistant", layout="wide")

# Title
st.title("Hasoub Books - Personal Assistant")
st.divider()
data_file = "Chatbot.txt"

request_container = st.container()
response_container = st.container()

# Initialize Session State
if 'history_list' not in st.session_state:
    st.session_state['history_list'] = []

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = [{"message": "Hello! How can we help you through our store?",
                                      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]

if 'past' not in st.session_state:
    st.session_state['past'] = [{"message": "Hey!", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]

if 'edit_mode' not in st.session_state:
    st.session_state['edit_mode'] = None

# Text Loader and Index Creator
loader = TextLoader(data_file)
docs = loader.load()

# Create embeddings and index
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts([doc.page_content for doc in docs], embeddings)

# Initialize the conversational retrieval chain
chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=vectorstore.as_retriever()
)


# Function to Handle Conversation
def conversational_chat(prompt):
    result = chain({"question": prompt, "chat_history": st.session_state['history']})
    st.session_state['history'].append((prompt, result["answer"]))
    return result["answer"]


# Save Conversation Function
def save_conversation():
    if st.session_state['history']:
        st.session_state['history_list'].append({
            'name': f"Conversation {len(st.session_state['history_list']) + 1}",
            'history': st.session_state['history'],
            'past': st.session_state['past'],
            'generated': st.session_state['generated'],
            'timestamp': datetime.now()
        })


# Categorize Conversations By Date
def categorize_conversations():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    categorized = {"Today": [], "Yesterday": [], "Previous 7 Days": []}

    for conv in st.session_state['history_list']:
        conv_date = conv['timestamp'].date()
        if conv_date == today:
            categorized["Today"].append(conv)
        elif conv_date == yesterday:
            categorized["Yesterday"].append(conv)
        elif conv_date >= today - timedelta(days=7):
            categorized["Previous 7 Days"].append(conv)

    return categorized


# Sidebar for Conversation History
with st.sidebar:
    st.markdown("## **Conversation History**")

    # New Conversation Button
    if st.button("➕ New Chat", key='new_conv'):
        save_conversation()
        st.session_state['history'] = []
        st.session_state['past'] = []
        st.session_state['generated'] = []

    conversations = categorize_conversations()
    for category, convs in conversations.items():
        if convs:
            st.markdown(f"### {category}")
            for i, conversation in enumerate(convs):
                conv_index = st.session_state['history_list'].index(conversation)

                if st.session_state['edit_mode'] == conv_index:
                    # Editing Mode: Show Input Box
                    new_name = st.text_input("Edit Name", value=conversation['name'], key=f"edit_{conv_index}")

                    if st.button("Save", key=f"save_{conv_index}"):
                        st.session_state['history_list'][conv_index]['name'] = new_name
                        st.session_state['edit_mode'] = None  # Exit edit mode

                else:
                    # Display Mode: Show Name As Button
                    col1, col2, col3 = st.columns([6, 1, 1])

                    with col1:
                        if st.button(conversation['name'], key=f"load_{conv_index}"):
                            st.session_state['history'] = conversation['history']
                            st.session_state['past'] = conversation['past']
                            st.session_state['generated'] = conversation['generated']

                    with col2:
                        if st.button("✏️", key=f"rename_{conv_index}"):
                            st.session_state['edit_mode'] = conv_index  # Enable editing mode

                    with col3:
                        if st.button("🗑️", key=f"delete_{conv_index}"):
                            del st.session_state['history_list'][conv_index]
                            st.experimental_rerun()

# Chat Input and Interaction
with request_container:
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Prompt", placeholder="Message HsoubBot....", key='input')
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversational_chat(user_input)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.session_state['past'].append({"message": user_input, "timestamp": timestamp})
            st.session_state['generated'].append({"message": output, "timestamp": timestamp})

# Display the conversation
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            user_msg = st.session_state['past'][i]["message"]
            user_time = st.session_state['past'][i]["timestamp"]
            bot_msg = st.session_state['generated'][i]["message"]
            bot_time = st.session_state['generated'][i]["timestamp"]

            message(f"{user_msg} \n*{user_time}*", is_user=True, key=str(i) + '_user', avatar_style="adventurer",
                    seed=13)
            message(f"{bot_msg} \n*{bot_time}*", key=str(i) + '_bot', avatar_style="bottts", seed=2)
