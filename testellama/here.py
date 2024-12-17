# This example is the new way to use the OpenAI lib for python
from openai import OpenAI

client = OpenAI(
    api_key="LA-17fd50dacb4a45288ea892d6769a6ddd89340018688447fda07038790a29b5f6",
    base_url="https://api.llama-api.com"
)

response = client.chat.completions.create(
    model="llama3.1-70b",
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "Who were the founders of Microsoft?"}
    ],
)

# print(response)
print(response.model_dump_json(indent=2))
print(response.choices[0].message.content)

