import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    engine="gpt-3.5-turbo",
    message=[
        {"role": "user", "content": "How are you today?"}
        ],
    max_tokens=100
)

print(response.choices[0].text.strip())