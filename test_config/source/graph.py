from typing import Annotated, Sequence, TypedDict, Optional
from langchain_core.messages import (BaseMessage,
                                    HumanMessage, 
                                    AIMessage)
from langgraph.graph.message import add_messages
from langchain_core.documents import Document
# The state for history
class QAState(TypedDict):

    # Documents
    pdf: Sequence[Document]
    # 'question' stores the user's input question. It can be a string or None if not provided.
    query: Annotated[Sequence[HumanMessage], add_messages]
    # 'context' stores relevant context about the guided project, if the question pertains to it.
    # If the question isn't related to the project, this will be None. 
    # Context that is REPLACED each turn.
    # It is a list of LangChain Document objects.
    #context: List[Document] # I DON'T THINK THAT WE NEED THIS, IT SHOULD BE GET OUT OF THE QUERY

    # 'answer' stores the generated response or answer. It can be None until the answer is generated.
    answer: Annotated[Sequence[AIMessage], add_messages]
    # reflect stores the reflection of the llm's feedback to the response from the initial llm
    reflect: Optional[str]
    # This stores queries and ai answers, useful for history
    all_messages: Sequence[BaseMessage] #Don't use add_messages here
    # QUERY NUM
    k: int
    user_name: Optional[str]
    # To save the colleciton name only 

    
    