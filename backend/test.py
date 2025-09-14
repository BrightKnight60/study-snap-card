import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    temperature=1,
    system="You are a diligent, hard working student that is trying to learn new course content by creating notecards to learn the most important information. For instance, important information to be quizzed could include equations. List the extracted information in small chunks to optimize learning.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": "<base64_encoded_image>"
                    }
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Here are the core concepts, parsed into small atomic tidbits of information for optimal learning"
                }
            ]
        }
    ]
)
print(message.content)