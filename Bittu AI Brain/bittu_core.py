import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# 1. Setup the API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in your .env file.")
    raise SystemExit(1)

client = genai.Client(api_key=api_key)

print("Booting up BITTU...\n")

# 2. Create a continuous chat session so BITTU remembers the conversation
chat = client.chats.create(model='gemini-2.5-flash')

# 3. Set the persona and get the first greeting
initial_prompt = "You are Bittu, a highly advanced and polite AI assistant. Introduce yourself in one short sentence."
response = chat.send_message(initial_prompt)
print("Bittu:", response.text)

# 4. The Conversation Loop
while True:
    user_input = input("\nYou: ")

    # Give yourself a way to turn it off
    if user_input.lower() in ['quit', 'exit', 'stop', 'power down']:
        print("Bittu: Powering down. Goodbye.")
        break

    # Send your typed message to Bittu
    response = chat.send_message(user_input)
    print("Bittu:", response.text)