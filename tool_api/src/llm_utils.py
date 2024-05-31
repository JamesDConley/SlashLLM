from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_API_BASE, MODEL_NAME

def call_model(messages, temperature=0.5):
    client = OpenAI(
        api_key = OPENAI_API_KEY,
        base_url = OPENAI_API_BASE,
    )

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
        temperature=temperature
    )
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
            
def simple_model_call(prompt, temperature=0.5, extra_body=None):
    client = OpenAI(
        api_key = OPENAI_API_KEY,
        base_url = OPENAI_API_BASE,
    )
    if extra_body is None:
        extra_body = {}
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role" : "user", "content" : prompt}],
        temperature=temperature,
        extra_body = extra_body
    )
    return completion.choices[0].message.content