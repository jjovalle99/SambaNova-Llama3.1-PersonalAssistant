import json
from pathlib import Path
from typing import Any, Dict


def save_json_chat_history(
    conversation_id: str, chat_history: Dict[str, Any], directory: Path = Path("history")
) -> None:
    """
    Saves chat history as a JSON file.

    Args:
        conversation_id (str): Unique identifier of the conversation.
        chat_history (Dict[str, Any]): Content of the JSON file that will be written.
            - 'conversation_id'
            - 'content'
                - 'messages'
                - 'metadata'
            - 'temperature'
            - 'stream'
        directory (Path): Path that stores the JSON file.

    Return:
        None
    """
    # Make directory or skip if it already exists.
    directory.mkdir(parents=True, exist_ok=True)

    # Make path of JSON file.
    file_path = directory / f"{conversation_id}.json"

    # Save JSON file.
    with open(file_path, mode="w") as fp:
        json.dump(chat_history, fp, indent=4)
