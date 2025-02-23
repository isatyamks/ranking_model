from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv('API_KEY')
client = Groq(api_key=GROQ_API_KEY)



chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    top_p=1,
    stop=None,
    stream=False,
)

print(chat_completion.choices[0].message.content)





