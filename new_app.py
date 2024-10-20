import streamlit as st
import speech_recognition as sr
from together import Together
import os

# Set page config
st.set_page_config(page_title="Car Infotainment System", layout="wide")

# Initialize session state for temperature and music
if "current_temp" not in st.session_state:
    st.session_state.current_temp = 22  # Initial default value
if "music_playing" not in st.session_state:
    st.session_state.music_playing = False
if "current_song" not in st.session_state:
    st.session_state.current_song = ""

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

# Music Player Section: Play and stop music
def play_music(song_path):
    st.session_state.current_song = song_path
    st.session_state.music_playing = True
    audio_file = open(song_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes)

def stop_music():
    st.session_state.music_playing = False
    st.session_state.current_song = ""

# Function to handle recognized voice command
def handle_command(command):
    st.write(f"Processing command: {command}")
    
    # Use Llama model to understand the command
    response = process_command(command)
    
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
    
    # Music playback
    elif "play" in command and "song" in command:
        # For example, use keywords to choose songs
        if "song one" in command.lower():
            play_music('songs/song1.mp3')  # Replace with the actual path to your song file
            st.write("Playing song one.")
        elif "song two" in command.lower():
            play_music('songs/song2.mp3')
            st.write("Playing song two.")
    
    elif "stop music" in command:
        stop_music()
        st.write("Music stopped.")
    
    # Add other commands (like directions) here

# AC Control Section UI
with col1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🌡️ AC Control")
    st.text("Temperature:")
    
    # Display updated temperature from session state
    st.markdown(f'<div class="temperature">{st.session_state.current_temp}°C</div>', unsafe_allow_html=True)
    
    # Buttons to adjust temperature
    col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
    with col_a2:
        if st.button("➖"):
            update_temperature(st.session_state.current_temp - 1)
    with col_a3:
        if st.button("➕"):
            update_temperature(st.session_state.current_temp + 1)
    st.markdown("</div>", unsafe_allow_html=True)

# Music Player Section UI
with col2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🎵 Music Player")
    
    # Display the current song if playing
    if st.session_state.music_playing:
        st.text(f"Now Playing: {os.path.basename(st.session_state.current_song)}")
    else:
        st.text("No song is playing.")
    
    # Music control buttons
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b1:
        if st.button("Stop Music"):
            stop_music()

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
