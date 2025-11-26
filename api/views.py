from rest_framework.response import Response
# The Response take serialized python data that we render out as json data
from rest_framework.decorators import api_view, permission_classes
# For the ai response
# from source.llm_models import llm_openai
from source.vector_database import create_user_db, add_docs_parents
from source.utils import pdf_cut, parser
from source.llm_functions import response_agent, get_app
from source.graph import QAState
from pathlib import Path

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from langgraph.graph import StateGraph, END
# from django.conf import settings

from rest_framework.permissions import AllowAny

current_locations = Path(__file__).parent
env_path = current_locations.parent/"config"/"keys.env" # Need to use string
medial_dir = current_locations.parent/"media"/"uploads"


# app = graph.compile()

# ==============================================================================

def getTokenInfor(ai_msg):
    if ai_msg:
        model_name = ai_msg.response_metadata.get("model_name")
        output_tokens = ai_msg.response_metadata.get("token_usage", {}).get("completion_tokens", {})
        prompt_tokens = ai_msg.response_metadata.get("token_usage", {}).get("prompt_tokens", {})
        total_ai_resp_token = ai_msg.response_metadata.get("token_usage", {}).get("total_tokens", {})


        return output_tokens, prompt_tokens, total_ai_resp_token, model_name
    else:
        print("No AI message found")
        return None
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def getData(request):
    """Handles POST requests to LangGraph agent."""
    user_message = request.data.get('userText')
    print(f"THE USERS TEXT IS {user_message}")
    if not user_message:
        return Response({"error": "Message cannot be empty."}, status=400)

    visitor_id = request.data.get("sessionID")
    print(f'THE VISITOR ID: {visitor_id}')
    config = {"configurable": {"thread_id": visitor_id}}

    try:
        app = get_app()
        response_text = app.invoke({"query": user_message}, config=config)
        print(f'**********************THE TOKENS INFO**********************')
        from langchain.schema import AIMessage
        ai_msg = next(
            (m for m in response_text["all_messages"] if isinstance(m, AIMessage)),
            None)
        resp_info = getTokenInfor(ai_msg)
        if resp_info:
            output_tokens, prompt_tokens, total_ai_resp_token, model_name = resp_info

            if "all_messages" in response_text and response_text["all_messages"]:
                ai_resp = response_text["all_messages"][-1].content
                return Response({
                    'response': ai_resp, 
                    'token': total_ai_resp_token,
                    'prompt_tokens': prompt_tokens,
                    'model_name': model_name,
                    'output_tokens': output_tokens
                    
                    })
        else:
            raise ValueError("No response, please try again later.")

    except Exception as e:
        print(f"Error invoking graph: {e}")
        return Response({"error": "An internal server error occurred: {e}"}, status=500)

@api_view(['GET','POST']) 
@permission_classes([AllowAny])
def upload_files(request):#Use for the upload too
    if request.method == "POST":
        visitor_id = request.data.get("sessionID")
        print(f"This is your SESSION ID: {visitor_id}")


        upload_files = request.FILES.getlist('pdf_files') #To get a list of files, if one file: request.FILES
        fs = FileSystemStorage()
        for upload_file in upload_files[:4]:  # limit to 4 files max
            user_media = medial_dir/f'{visitor_id}/'#f'uploads/{visitor_id}/'
            filename = user_media / upload_file.name
            print(upload_file.name)
            print(upload_file.size)
            fs.save(filename, upload_file)
        file_count = len(upload_files)
        # If the visitor_id is not in the session, this is their first visit.
        # Cut the files
        # Each user folder
        medial_dir_per_visitor = medial_dir / f"{visitor_id}"
        cut_pdfs_path, total_pages = pdf_cut(medial_dir_per_visitor, visitor_id=visitor_id)
        # The pdf_cut is saved into the current_locations.parent/"media"/"process_pdfs"/visitor_id/"pdfs_cut" folder for each visitor
        # Then parse the pdf, the default method is llamaparse, then unstructured

        docs_list, pickle_name, parseMethod = parser(cut_pdfs_path=cut_pdfs_path)
        print(f"Total pages being parsed is {total_pages}")
        retriever_main, persist_directory_main = create_user_db(thread_id=visitor_id)
        add_docs_parents(retriever_main, thread_id=visitor_id, docs=docs_list)
        
        
        return JsonResponse({
            'status': 'success', 
            'message': f'{file_count} file(s) uploaded successfully!',
            'user_id': visitor_id,
            'total_parsed_pages': total_pages,
            'parse_method': parseMethod
        })