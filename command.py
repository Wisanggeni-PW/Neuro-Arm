from ollama import chat
from pydantic import BaseModel
from typing import Literal

class Task(BaseModel):
    target_object: Literal['fork', 'spoon', 'bottle', 'cup', 'none']
    command: Literal['search', 'home']


def detect_task_from_speech(message: str, model: str = 'llama3.2:3b') -> Task:
    system_prompt = """
        You classify voice commands for a robot.

        command rules:
        - 'search' → user wants to find, search, locate, grab, pick up an object.
        - 'home' → user wants the robot to return to original position.

        object rules:
        - If user specifies fork/spoon/bottle/cup → use it.
        - If user does not specify any → target_object = 'none'.

        OUTPUT ONLY VALID JSON.
        """
    response = chat(
        model=model,
        messages=[
            { 'role': 'system', 'content': system_prompt },
            { 'role': 'user',   'content': message }
        ],
        format=Task.model_json_schema(),
    )

    task = Task.model_validate_json(response.message.content)

    if task.command == 'search':
        print(f"---SEARCH MODE: object={task.target_object}---")
    else:
        print(f"---RETURN HOME MODE---")

    return [task.target_object, task.command]

if __name__ == "__main__":
    detect_task_from_speech("Look for the fork")