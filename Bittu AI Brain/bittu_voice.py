import os
import time
import sounddevice as sd
import numpy as np
import wavio
import speech_recognition as sr
import pyttsx3
from google import genai

# 1. Setup the AI Brain
my_api_key = "AQ.Ab8RN6ICHcK6_XRAqS6SZszDUF2yT_Dbtx97sgeLCXHh4wLfeg"  # Paste your Gemini API key here
client = genai.Client(api_key=my_api_key)
chat = client.chats.create(model='gemini-3.5-flash')

# 2. Setup Bittu's Voice (Text-to-Speech)
engine = pyttsx3.init()
engine.setProperty('rate', 175)

def bittu_speak(text):
    print(f"\nBittu: {text}")
    engine.say(text)
    engine.runAndWait()

# 3. Audio Recording Settings
duration = 5  # Seconds to record your voice
fs = 44100    # Sample rate
filename = "temp_voice.wav"

# 4. Initialize Persona
bittu_speak("Voice systems online. I am Bittu.")
chat.send_message("You are Bittu, a highly advanced, polite, and brief AI assistant. Keep your responses under 2 sentences.")

recognizer = sr.Recognizer()

# 5. The Continuous Voice-to-Voice Loop
print("\n--- Bittu is ready! Press Enter, speak, and wait for the reply. ---")

while True:
    try:
        input("\nPress [Enter] and start speaking your command...")
        
        print("[Listening... Speak now for 5 seconds]")
        # Record audio from your microphone
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait until the recording is finished
        
        # Save recording temporarily
        wavio.write(filename, audio_data, fs, sampwidth=2)
        print("[Processing your voice...]")

        # Convert audio file to text using Google Speech Recognition
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)
            print(f"You said: {user_text}")

        # Check for shutdown commands
        if user_text.lower() in ['quit', 'exit', 'stop', 'power down']:
            bittu_speak("Powering down systems. Goodbye.")
            break

        # Send text to Gemini AI brain
        response = chat.send_message(user_text)
        
        # Make Bittu speak the response out loud
        bittu_speak(response.text)

    except sr.UnknownValueError:
        bittu_speak("I couldn't quite catch that. Please try again.")
    except sr.RequestError:
        bittu_speak("Network error connecting to speech recognition.")
    except Exception as e:
        print(f"[Error: {e}]")
        print("Continuing loop... Press Enter to try again.")