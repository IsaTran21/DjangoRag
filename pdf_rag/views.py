from django.shortcuts import render
from source.utils import get_visitor_id
# Create your views here.

def index_view(request):
    
    request.session.flush()
    visitor_id = get_visitor_id(request)
    print(f'This is the NEW visitor id on refresh: {visitor_id}')
    return render(request, 'pdf_rag/index.html', {'visitor_id': visitor_id})
def demo(request):
    return render(request, 'pdf_rag/index_demo.html')