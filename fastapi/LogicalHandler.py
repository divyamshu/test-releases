from config import EXPECTED_ENV_KEYS
from imports import StringIO
from dotenv import load_dotenv, dotenv_values

def get_environment_variables(env_contents: str):
    env_vars = dotenv_values(stream=StringIO(env_contents))
    # Get the single expected key (handle string or iterable)
    key = EXPECTED_ENV_KEYS

    if key in env_vars:
        value = env_vars.get(key)
        return value
    else:
        print(f"Missing environment variable: {key}")
        return {}

def get_previous_tag(data, current_tag):
    # find index of the current tag
    index = next((i for i, item in enumerate(data) if item['tag_name'] == current_tag), None)

    if index is None:
        return None  # tag not found

    # check if a previous index exists
    if index + 1 < len(data):
        return data[index + 1]['tag_name']
    
    return None  # no previous tag