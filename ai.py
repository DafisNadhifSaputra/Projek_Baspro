import os
import google.generativeai as genai

os.environ["GEMINI_API_KEY"] = "AIzaSyBSTFXFnjRBFt8G6GhIfeEv0NLbUDpzxBU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "halo apa kabar",
      ],
    },
    {
      "role": "model",
      "parts": [
        "The user greeted me in Indonesian, asking \"how are you?\". The most appropriate and natural response in Indonesian would be to return the greeting and offer a similar polite inquiry. Therefore, I should respond with \"Baik, terima kasih. Kamu sendiri?\". This translates to \"Good, thank you. And you?\".",
        "Baik, terima kasih. Kamu sendiri?\n",
      ],
    },
  ]
)
response = model.generate_content("siapa presiden indonesia sekarang?")

print(response.text)