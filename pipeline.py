from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
import os
ENDPOINT_URL_WATSONX = os.environ.get("ENDPOINT_URL_WATSONX")
API_KEY_WATSONX = os.environ.get("API_KEY_WATSONX")



credentials = Credentials(
    url= ENDPOINT_URL_WATSONX,
    api_key_WASTONX=API_KEY_WATSONX
)
PROJECT_ID = "1873a12a-8ca5-4c20-be19-3337bbd97aa3"


model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "max_tokens": 200
      }
)

result = model.chat(messages=[{'role': 'user', 'content': "Placeholder"}])

print(result['choices'][0]['message']['content'])