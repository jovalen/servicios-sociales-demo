import os
import json
import datetime
import glob
import streamlit as st
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.cognitiveservices.speech import (
    SpeechConfig, AudioInputStream, AudioStreamFormat, SpeechRecognizer, AudioConfig
)
from streamlit_webrtc import webrtc_streamer
from azure.cognitiveservices.speech.conversation import ConversationTranscriber, ConversationConfig

# 1. Cargar variables de entorno
load_dotenv('.env.local')

# 2. Configurar clientes
speech_config = SpeechConfig(
    subscription=os.getenv('SPEECH_KEY'),
    region=os.getenv('SPEECH_REGION')
)
project_client = AIProjectClient(
    endpoint=os.getenv('PROJECT_ENDPOINT'),
    credential=DefaultAzureCredential()
)
agent = project_client.agents.get_agent('briefing-agent')

# 3. Cargar repositorio de documentos de casos (RAG)
docs = []
for file in glob.glob('repository/*.json'):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        docs.append(data)

# 4. Interfaz Streamlit
st.title('Demo Servicios Sociales (RAG + Voz)')

# Selector de caso
case_ids = [doc['id'] for doc in docs]
if not case_ids:
    st.error('No hay documentos en repository/. Añade JSON con casos de ejemplo.')
    st.stop()
case_id = st.sidebar.selectbox('Selecciona caso', case_ids)
doc = next(d for d in docs if d['id'] == case_id)
st.sidebar.markdown(f"**{doc['name']}**  
{doc['details']}")

# Calendario mock con hora
def show_calendar():
    if 'events' not in st.session_state:
        st.session_state['events'] = []
    with st.sidebar.expander('Calendario Mock'):
        date = st.date_input('Fecha')
        time = st.time_input('Hora')
        text = st.text_input('Evento')
        if st.button('Añadir evento'):
            dt = datetime.datetime.combine(date, time).isoformat()
            st.session_state['events'].append({'datetime': dt, 'title': text})
        for ev in sorted(st.session_state['events'], key=lambda x: x['datetime']):
            st.write(f"- {ev['datetime']}: {ev['title']}")
show_calendar()

# Función de invocación al agente con contexto RAG y chat
def ask_agent(prompt):
    state = {
        'historial': doc['details'],
        'events': st.session_state.get('events', [])
    }
    messages = [
        {'role': 'system', 'content': 'Eres un asistente de trabajador social con acceso a historial y calendario.'},
        {'role': 'user', 'content': prompt},
        {'role': 'system', 'content': f"Historial: {state['historial']}"},
        {'role': 'system', 'content': f"Eventos: {state['events']}"}
    ]
    return agent.invoke_streaming({'messages': messages})

# Chat conversacional de texto
st.header('Chat en tiempo real')
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Pregunta automática sobre la siguiente visita
if st.button('¿Qué visita me toca ahora?'):
    now = datetime.datetime.now().isoformat()
    prompt = f"¿Qué visita me toca ahora? Fecha y hora: {now}."
    stream = ask_agent(prompt)
    response = ''.join(stream)
    st.session_state['chat_history'].append(('IA', response))

# Mostrar historial de chat
for speaker, text in st.session_state['chat_history']:
    if speaker == 'Tú': st.markdown(f"**Tú:** {text}")
    else: st.markdown(f"**IA:** {text}")

# Entrada libre de usuario
user_input = st.text_input('Pregunta libre...')
if st.button('Enviar') and user_input:
    st.session_state['chat_history'].append(('Tú', user_input))
    stream = ask_agent(user_input)
    response = ''.join(stream)
    st.session_state['chat_history'].append(('IA', response))

# Conversación por voz en hilo real-time
st.header('Diálogo de voz en tiempo real')
if 'transcriber' not in st.session_state:
    st.session_state['transcriber'] = None
if 'voice_history' not in st.session_state:
    st.session_state['voice_history'] = []

# Start/Stop transcriber buttons
if st.button('Iniciar Diálogo'):
    st.session_state['voice_history'].clear()
    audio_cfg = AudioConfig(use_default_microphone=True)
    trans_cfg = ConversationConfig()
    conv = ConversationTranscriber(speech_config, audio_cfg)
    conv.transcribing.connect(lambda evt: st.session_state['voice_history'].append(('partial', evt.result.text)))
    conv.transcribed.connect(lambda evt: st.session_state['voice_history'].append(('final', evt.result.text)))
    conv.start_transcribing()
    st.session_state['transcriber'] = conv
if st.button('Detener Diálogo') and st.session_state['transcriber']:
    st.session_state['transcriber'].stop_transcribing()
    # Mostrar y enviar a agente la última voz
    full_text = ' '.join([txt for typ, txt in st.session_state['voice_history'] if typ=='final'])
    st.write('**Tú (voz):**', full_text)
    st.session_state['chat_history'].append(('Tú', full_text))
    # Enviar al agente
    stream = ask_agent(full_text)
    response = ''.join(stream)
    st.session_state['chat_history'].append(('IA', response))

st.write('---')
