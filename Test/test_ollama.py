import ollama

try:
    # Test connection and model response using llama3.1
    response = ollama.chat(
        model='llama3.1',
        messages=[
            {'role': 'user', 'content': 'Respond with just the word "ONLINE".'}
        ]
    )
    print("[+] Connection Successful!")
    print("Model Response:", response['message']['content'])

except Exception as e:
    print("[-] Connection Failed:", str(e))