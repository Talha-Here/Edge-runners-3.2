import streamlit as st
import speech_recognition as sr
from together import Together
import os
from pygame import mixer
import time

# Initialize pygame mixer for playing audio
mixer.init()

# Set page config
st.set_page_config(page_title="Car Infotainment System", layout="wide")

# Initialize session state for temperature
if "current_temp" not in st.session_state:
    st.session_state.current_temp = 22  # Initial default value

# Custom styles
st.markdown("""
    <style>
    .title-text {
        font-size: 36px;
        font-weight: bold;
        color: white;
        text-align: center;
        background-color: #008cba;
        padding: 10px;
        border-radius: 5px;
    }
    .section {
        padding: 15px;
        border-radius: 10px;
        background-color: #333;
        margin-bottom: 20px;
    }
    .temperature {
        font-size: 50px;
        font-weight: bold;
        color: #00aced;
        text-align: center;
    }
    .destination-label {
        font-size: 18px;
        color: white;
    }
    .button-blue {
        background-color: #008cba;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Page title
st.markdown('<div class="title-text">Car Infotainment System</div>', unsafe_allow_html=True)

# Layout: Two columns
col1, col2 = st.columns([1, 1])

# Initialize the Together client
@st.cache_resource
def get_together_client():
    return Together(api_key='97d77defec520871d1e2d66980d1b37c350065417d8e3ca9f331c20a145bd9b2')

client = get_together_client()

# Function to process commands using Llama
def process_command(query, model="meta-llama/Llama-3.2-3B-Instruct-Turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant for controlling car systems like AC, Music, and Navigation."},
            {"role": "user", "content": query}
        ],
        max_tokens=100,
        temperature=0.7
    )
    return response.choices[0].message.content

# AC Control Section
def update_temperature(new_temp):
    st.session_state.current_temp = new_temp

# Music Handling Section
SONGS_DIR = "songs"  # Folder where songs are stored
available_songs = {
    "first song": "song1.mp3",
    "second song": "song2.mp3",
}

def play_song(song_name):
    song_path = os.path.join(SONGS_DIR, available_songs.get(song_name, ""))
    if os.path.exists(song_path):
        mixer.music.load(song_path)
        mixer.music.play()
        st.write(f"Now Playing: {song_name}")
    else:
        st.write("Sorry, song not found.")

def stop_song():
    mixer.music.stop()
    st.write("Music stopped.")
# Function to handle recognized voice command
def handle_command(command):
    st.write(f"Processing command: {command}")
    
    # Use Llama model to understand the command
    response = process_command(command)
    
    global current_temp  # Make sure to modify the global variable
    if "temperature" in command:
        if "set to" in command:
            temp_value = int(command.split("set to")[1].strip().replace("°C", ""))
            update_temperature(temp_value)
            st.write(f"Temperature set to {st.session_state.current_temp}°C.")
        elif "increase" in command:
            update_temperature(st.session_state.current_temp + 1)
            st.write(f"Temperature increased to {st.session_state.current_temp}°C.")
        elif "decrease" in command:
            update_temperature(st.session_state.current_temp - 1)
            st.write(f"Temperature decreased to {st.session_state.current_temp}°C.")
    
    elif "play" in command:
        # Handle music command
        for song_name in available_songs.keys():
            if song_name in command:
                play_song(song_name)
                break
        else:
            st.write("Sorry, song not recognized.")
    
    elif "stop" in command:
        # Handle stop song command
        stop_song()

    elif "directions" in command:
        st.write("Fetching directions...")

# AC Control Section
with col1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🌡️ AC Control")
    st.text("Temperature:")
    st.text("To increase or decrease Temperature: \n Say: 'temperature increase' or 'temperature decrease'")
    st.text("For particular Temperature: \n Say: 'temperature set to (desired temperature)'")
    # st.markdown(f'<div class="temperature">{current_temp}°C</div>', unsafe_allow_html=True)
    # Display updated temperature from session state
    st.markdown(f'<div class="temperature">{st.session_state.current_temp}°C</div>', unsafe_allow_html=True)
    
    col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
    with col_a2:
        if st.button("➖"):
            update_temperature(st.session_state.current_temp - 1)
    with col_a3:
        if st.button("➕"):
            update_temperature(st.session_state.current_temp + 1)
    st.markdown("</div>", unsafe_allow_html=True)

# Music Player Section
with col2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🎵 Music Player")
    # st.text("Now Playing:")
    st.text("Say the song name to play. For example: 'Play first song'")
    st.text("To stop the song, Say: 'Stop'")
# Voice command function
def listen_for_commands():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    st.write("Listening for voice commands...")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Listening...")
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                
                st.write(f"Command recognized: {command}")
                handle_command(command)
                
            except sr.UnknownValueError:
                st.write("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                st.write(f"Could not request results from Google Speech Recognition service; {e}")

# Run voice command listening in a separate thread
if st.button("Start Voice Assistant"):
    listen_for_commands()

# Footer
st.markdown('<div style="text-align: center; color: white; font-size: 14px;">@ in-car-ai-agent | lablab.ai | 2024</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: black; font-size: 14px;">edge-runners-3-point-2 hackathon</div>', unsafe_allow_html=True)
