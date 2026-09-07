from google import genai

# 1. Setup the API Key
my_api_key = "TODO: paste your Gemini API key here"
client = genai.Client(api_key=my_api_key)

print("Booting up BITTU...\n")

# 2. Create a continuous chat session so BITTU remembers the conversation
chat = client.chats.create(model='gemini-3.5-flash')

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