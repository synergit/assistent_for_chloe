import openai
import os
from dotenv import load_dotenv

# Get the root path of the project
root_path = os.path.dirname(os.path.abspath(__file__))

# Load the .env file from the root path
load_dotenv(os.path.join(root_path, "..", ".env"))
# load_dotenv()

def check_openai_api_key_list_model(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True

def is_api_key_valid():
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt="This is a test.",
            max_tokens=5
        )
    except:
        return False
    else:
        return True

api_key = os.getenv("OPENAI_API_KEY") 
openai.api_key = api_key
print(openai.api_key)
# is_valid = is_api_key_valid()

# if is_valid:
#     print("Valid OpenAI API key.")
# else:
#     print("Invalid OpenAI API key.")


from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    messages=[{
        "role": "user",
        "content": "Say this is a test",
    }],
    model="gpt-4o-mini",
)

print(response._request_id)