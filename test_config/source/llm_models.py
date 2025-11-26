from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pathlib import Path

current_locations = Path(__file__).parent
env_path = current_locations.parent/"config"/"keys.env" # Need to use string
from config.keys import (
    openai_key,
)

def get_model(model, api):
    
    llm = ChatOpenAI(
            model=model,
            temperature=0.5,
            max_tokens=256,
            api_key=api)

    return llm
llm_openai = get_model("gpt-4o-mini", openai_key) # $0.15 and $0.60
llm_summarize = get_model("gpt-4.1-nano", openai_key) # $0.10 $0.025 $0.40

# Openai embedding model
embedding_openai = OpenAIEmbeddings(
    model="text-embedding-3-large",#"text-embedding-3-small", #The new one is costlier (6x), but it is better
    api_key=openai_key
)