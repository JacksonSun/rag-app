from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings


OPENAI_API_BASE = "https://prd-gpt-scus.openai.azure.com/"
OPENAI_API_TYPE = "azure"
OPENAI_API_KEY = ""
OPENAI_API_VERSION = "2023-05-15"
DEPLOYMENT = "text-embedding-ada-002"
MODEL_DEPLOYMENT = "gpt-35-turbo-0301"
EVAL_DEPLOYMENT = "gpt-4-8k-0314"
CONN_STR = ""
CONTAINER_NAME = "rd-expert"

embed_model = OpenAIEmbeddings(
    deployment=DEPLOYMENT,
    openai_api_base=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    openai_api_key=OPENAI_API_KEY,
)
gpt3 = AzureChatOpenAI(
    deployment_name=MODEL_DEPLOYMENT,
    openai_api_base=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    openai_api_key=OPENAI_API_KEY,
    openai_api_version=OPENAI_API_VERSION,
    temperature=0,
)
gpt4 = AzureChatOpenAI(
    deployment_name=EVAL_DEPLOYMENT,
    openai_api_base=OPENAI_API_BASE,
    openai_api_type=OPENAI_API_TYPE,
    openai_api_key=OPENAI_API_KEY,
    openai_api_version=OPENAI_API_VERSION,
    temperature=0,
)
