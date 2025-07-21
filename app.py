import streamlit as st
from azure.ai.foundry import FoundryClient
from azure.identity import DefaultAzureCredential
import os

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

endpoint = os.getenv('REACT_APP_FOUNDRY_ENDPOINT')
client = FoundryClient(endpoint=endpoint, credential=DefaultAzureCredential())

st.title('Demo Servicios Sociales')

# Mock Calendar
events = st.session_state.get('events', [])
with st.expander('Calendario Mock'):
    date = st.date_input('Fecha nueva')
    title = st.text_input('Título evento')
    if st.button('Añadir evento'):
        events.append({'date': str(date), 'title': title})
        st.session_state['events'] = events
    for ev in events:
        st.write(f"- {ev['date']} — {ev['title']}")

# RAG Input
contexts = st.session_state.get('contexts', [])
with st.expander('Contexto (RAG)'):
    ctx = st.text_input('Nuevo contexto')
    if st.button('Añadir contexto'):
        contexts.append(ctx)
        st.session_state['contexts'] = contexts
    for c in contexts:
        st.write(f"• {c}")

# Transcripción
if st.button('Iniciar/Detener transcripción'):
    agent = client.get_agent('transcripcion-agent')
    stream = agent.invoke_streaming({})
    transcript = ''
    for chunk in stream:
        transcript += chunk
    st.text_area('Transcripción', transcript, height=200)

# Briefing
if st.button('Iniciar briefing'): 
    agent = client.get_agent('briefing-agent')
    stream = agent.invoke_streaming({'contexts': contexts, 'events': events})
    response = ''
    for chunk in stream:
        response += chunk
        st.experimental_rerun()
    st.text_area('Briefing', response, height=200)
