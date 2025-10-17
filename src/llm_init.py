from openai import AzureOpenAI, OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings


API_KEY = ''
ORG_ID = ''


def init_openai(api_key=API_KEY,
                organization_id=ORG_ID):
    client = OpenAI(
        api_key=api_key,
        organization=organization_id
    )
    return client


def init_azure():
    client = AzureOpenAI(
        api_key="____",
        api_version="",
        azure_endpoint=""
    )
    return client


def init_langchain(
        openai_api_key=API_KEY,
        openai_organization=ORG_ID,
        model="gpt-4-0125-preview"):
    llm = ChatOpenAI(
        temperature=0,
        model=model,
        openai_api_key=openai_api_key,
        openai_organization=openai_organization
    )
    return llm


def init_langchain_embedding(
        openai_api_key=API_KEY,
        openai_organization=ORG_ID):
    embedding_model = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        openai_organization=openai_organization
    )
    return embedding_model
