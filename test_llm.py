import requests

res = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "Fix this Python code:\na=10\nb=20\na+b",
        "stream": False
    }
)

print(res.text)