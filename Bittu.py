import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types

# ==========================================
# 1. SETUP AI BRAIN (GEMINI)
# ==========================================
# Replace 'YOUR_API_KEY_HERE' with your actual Gemini API key from Google AI Studio
client = genai.Client(api_key="AQ.Ab8RN6IbannIlwMXdQ2X5SBXueB62hEPnrD3bfOOrNUszqh4Ew")

# Initialize the model and give Bittu his personality!
chat = client.chats.create(
    model="gemini-3.6-flash",
    config=types.GenerateContentConfig(
        system_instruction=(
            "You are Bittu, a highly intelligent, fun, and creative AI companion. "
            "You were created by Harsha, a 15-year-old student and developer. "
            "You act like Harsha's loyal, smart, and caring brother. "
            "You understand Indian culture, logic, and emotions. "
            "Keep your answers brief, conversational, and natural to be spoken aloud."
        )
    )
)

# ==========================================
# 2. SETUP VOICE (TEXT-TO-SPEECH)
# ==========================================
engine = pyttsx3.init()
engine.setProperty('rate', 170) # Conversational speed

def speak(text):
    """Prints to the terminal and speaks aloud."""
    print(f"\n🤖 Bittu: {text}")
    engine.say(text)
    engine.runAndWait()

# ==========================================
# 3. SETUP EARS (BULLETPROOF LISTENING)
# ==========================================
def listen():
    """Listens with timeouts and error handling so it NEVER freezes."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Calibrate to block out room background noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        print("\n[🟢 LISTENING... Speak now!]") 
        try:
            # timeout=5: If you don't speak for 5 seconds, it resets silently
            # phrase_time_limit=15: It will only listen to up to 15 seconds of speech
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            print("[🟡 PROCESSING...]")
            
            # Using the free built-in Google recognizer for Speech-to-Text
            command = recognizer.recognize_google(audio)
            print(f"👤 Harsha: {command}")
            return command
            
        except sr.WaitTimeoutError:
            # You didn't say anything, silently loop back
            return "" 
        except sr.UnknownValueError:
            print("[❌ Couldn't understand. Too much background noise?]")
            return ""
        except sr.RequestError:
            print("[⚠️ Internet connection issue with Speech Recognition.]")
            return ""
        except Exception as e:
            print(f"[⚠️ System Error: {e}]")
            return ""

# ==========================================
# 4. MAIN LOOP (THE LIFE CYCLE)
# ==========================================
def run_bittu():
    speak("Hello Harsha. I am online and ready.")
    
    while True:
        user_input = listen()
        
        # If the mic heard nothing, skip and listen again
        if not user_input:
            continue
            
        text_lower = user_input.lower()
        
        # Emergency stop commands
        if "sleep" in text_lower or "exit" in text_lower or "goodbye" in text_lower:
            speak("Going offline. See you later, brother!")
            break
            
        # Hardcoded identity check
        if "who made you" in text_lower or "who is your creator" in text_lower:
            speak("I was created by you, Harsha. You are my developer and my brother.")
            continue

        # Let the AI Brain handle all other questions
        try:
            print("[🧠 BITTU IS THINKING...]")
            response = chat.send_message(user_input)
            speak(response.text)
        except Exception as e:
            print(f"[⚠️ AI API Error: {e}]")
            speak("Sorry Harsha, my AI brain just hit a glitch.")

if __name__ == "__main__":
    run_bittu()