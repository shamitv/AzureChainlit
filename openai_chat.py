from openai import AsyncAzureOpenAI
import chainlit as cl
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve API key, version, and endpoint from environment variables
api_key = os.getenv("AZURE_OPENAI_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION_2")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize the Azure OpenAI client
client = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)


settings = {
    "model": "gpt-4o",
    "max_tokens": 5000,
}


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:

        if part.choices and len(part.choices) > 0 and (token := part.choices[0].delta.content or ""):
            await msg.stream_token(token)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)