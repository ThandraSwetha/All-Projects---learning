import os

import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Set the GEMINI_API_KEY environment variable.")
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name = "gemini-2.0-flash")

chat = model.start_chat(history=[])

while True:
    prmt = input("Enter Prompt")
    if (prmt =="exit"):
        break

    res = chat.send_message(prmt)

    print(res.text)