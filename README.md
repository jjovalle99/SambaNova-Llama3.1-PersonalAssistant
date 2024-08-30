# SambaNova | Llama 3.1 405B | Personal Assistant Agent

![img](assets/sambanova-logo-black.png)

## Description
This repository contains a personal assistant agent built using Llama 3.1 405B, served by SambaNova. SambaNova holds a world performance record of 114 tokens per second on this [model](https://sambanova.ai/blog/speed-record-on-llama-3.1-405b). This, combined with the strengths of Llama 3.1, creates a powerful combination for building impressive applications. Additionally, as an open-source model, it offers an attractive approach for companies concerned about data privacy.

While frameworks like LangChain are useful, building from scratch can greatly improve coding skills and LLM understanding. This project uses only the OpenAI Python SDK and Pydantic to develop an agent-based personal assistant. Try it yourself! If you can't get an API key from SambaNova, you can explore other alternatives (with potential minor code changes) such as Groq.

## Repository

| Artifact | Description |
|----------|-------------|
| `app.py` | Main module to interact with the Llama 3.1 405B powered assistant. |
| `src/chat.py` | Contains functions to handle model streaming. |
| `src/client.py` | Contains the custom `SambaAsync` class based on OpenAI's `AsyncOpenAI`, used to invoke the model. |
| `src/google_tools.py` | Contains functions that allow the model to fetch emails and calendar data. |
| `src/persistence.py` | Contains functions to save chat history as a JSON file. |
| `src/pydantic_classes.py` | Contains `Metadata` class, used for tracing. |
| `src/settings.py` | Pydantic settings to handle environment variables. |
| `src/tools.py` | Contains the function to fetch news from NewsAPI. |
| `src/utils.py` | Contains a function to extract JSON schema from Pydantic models. |

## Requirements
The code was developed using Python 3.11. You'll need these Python libraries:
- Poetry
- OpenAI
- Pydantic

No additional frameworks are required !! Keep it simple!

## Setup
You'll need the following environment variables:
- `SAMBA_API_KEY`: [SambaNova API Key](https://sambanova.ai/blog/speed-record-on-llama-3.1-405b)
- `SAMBA_URL`: [SambaNova URL](https://sambanova.ai/blog/speed-record-on-llama-3.1-405b)
- `NEWS_API`: [NewsAPI key](https://newsapi.org/register)

You'll also need an OAuth 2.0 Client with access to Gmail API and Calendar API. You can create one in Google Cloud Platform (GCP) and save it as a JSON file named `credentials.json` in the root folder.

After obtaining all keys and credentials:

1. Install the environment:
   ```bash
   poetry install --no-root
   ```

2. Start chatting with your assistant:
    ```bash
    poetry run python app.py
    ```