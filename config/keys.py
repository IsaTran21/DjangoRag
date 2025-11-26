from dotenv import load_dotenv
import os
from pathlib import Path
# Load the .env only once
# BASE_DIR = Path(__file__).resolve().parent
# ENV_PATH = BASE_DIR / "keys.env"
# 
# load_dotenv(ENV_PATH)
# together_key = os.getenv("together_isa")
# openai_key = os.getenv("openai_pro")
# tavily_key = os.getenv("tavily")
# llamaparse_key = os.getenv("llamaparse")
# unstructure_key = os.getenv("unstructure")

# Using env variables
openai_key = os.environ.get("OPENAI")
together_key = os.environ.get("TOGETHER")
tavily_key = os.environ.get("TAVILY")
llamaparse_key = os.environ.get("LLAMAPARSE")
unstructure_key = os.environ.get("UNSTRUCTURED")                                
