import google.generativeai as genai

#1. Seting up the API Key
my_api_key = "AQ.Ab8RN6JRZlW6dZI1sMK85tRXpP8wHS0VGQow60be3iHyMk3QIQ"
genai.configure(api_key=my_api_key)

#2. Initialize the AI Model
model = genai.GenerativeModel('gemini-1.5-flash')

#3. Give JARVIS a command
print("Booting up JARVIS...\n")
prompt = "You are JARVIS, a highly advanced and polite AI assistant. Introduce yourself in one short sentence."

#4. Get the response and print it
response = model.generate_content(prompt)
print("JARVIS:", response.text)