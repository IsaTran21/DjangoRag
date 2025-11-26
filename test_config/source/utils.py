import os
from pypdf import PdfReader, PdfWriter # This is for limiting the pdf number of pages.
from pathlib import Path
import glob
from llama_parse import LlamaParse
from langchain_core.documents import Document

# Use the online api
import unstructured_client
from unstructured_client.models import operations, shared


from langchain_community.vectorstores.utils import filter_complex_metadata
import pickle # For storing to disk the Document object.

from unstructured_client.models.errors import SDKError
from httpx import HTTPStatusError
import time
import requests # for mock limit rate 429 error :>

current_locations = Path(__file__).parent
medial_dir = current_locations.parent/"media"/"uploads"

# load_dotenv(env_path)
from config.keys import (
    llamaparse_key,
    unstructure_key
)
doc_pick_path = ""
def pdf_cut(file_paths, visitor_id=None,  max_pages_to_parse=5):
    """This function helps to parse the pdf files.
    Inputs: the paths of the files.
    The parsing method is used is llamparse and the unstructured. The llamaparse is the default value.
    The visitor_id here is also the thread_id.
    The unstructured is a fallback option if the llamaparse is failed (run out of credit).
    The files can be at most 3 files and at most 20 pages per files.
    The output is converted into the Document object of langchain.
    the cut files will be saved into the output_dir.
    It returns output_dir where the cut pdfs are saved. """
    # Define output directory and filename
    assert visitor_id, "visitor_id must be not None"
    output_dir = current_locations.parent/"media"/"process_pdfs"/visitor_id/"pdfs_cut"
    total_pages = 0
    


    # Create the temp paths to save the file
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    pdf_files_in_file_paths = file_paths.glob('*.pdf')
    for file_path in pdf_files_in_file_paths:
        
        try:
            directory, filename = os.path.split(file_path)
            # read the original pdf
            reader = PdfReader(file_path)
            writer = PdfWriter()
            # Get the total number of pages to avoid errors
            num_pages_in_original = len(reader.pages)
            pages_to_add = min(max_pages_to_parse, num_pages_in_original)
            total_pages += pages_to_add

            # Add the specified number of pages to the new pdf
            for i in range(pages_to_add):
                writer.add_page(reader.pages[i])
            print(f"Created temporary PDF with the first {pages_to_add} pages")
            print(type(writer))
            # Save it to a PDF file
            # Write the PDF to the directory

            # This helps to save a file which does exist,
            # and we create a new file with k++ instead.
            k = 0
            file_name = f'file_{k}_{filename}'
            
            temp_file_path = os.path.join(output_dir, file_name)

            while os.path.exists(temp_file_path):
                k+=1
                file_name_full = f'file_{k}_{filename}'
                temp_file_path = os.path.join(output_dir, file_name_full)
                
            with open(temp_file_path, "wb") as f:
                writer.write(f)
                
                    
            print(f"Saved the temporary {temp_file_path} file!")
            
        except Exception as e:
            print(f'Error encountered: {e}')
    return output_dir, total_pages


# The parsing methods
def parser(cut_pdfs_path, language="en"):
    """
    Input: the path of the pdf files.
    Args:
    method: default='unstructured', other choice is: 'llamaparse'. The defaul value of llamaparse chunking method is by page.
    Meanwhile, the unstructured I use split by title, it does not support by_page(this is for the api and ui version only).
    file_path: of a single pdf file or multiple pdf files. Since llamaparse accept multiple pdf files, and unstructured accept 1 pdf file.
    This function save the processed docs into pickle and return the documetn objects at the same time.
    This funtion also save the path of the picke file.
    
    """

    file_list = list(glob.glob(f'{cut_pdfs_path}/*.pdf'))
    print(f'Number of PDF files being parsed is {len(file_list)}')


    filtered_docs = [] # To avoid being out of scope
    all_elements = []
    method=''
    for attempt in range(5): # 5 attempts
            try:
                print("Use llamaparse")
                method='llamaparse'
                parser = LlamaParse(
                api_key=llamaparse_key,
                result_type="markdown",  # other choise may be "markdown" and "text" are available
                verbose=True,
                language=language)
                
                documents = parser.load_data(file_list)
                filtered_docs = [doc.to_langchain_format() for doc in documents]
                # Force fallback if nothing usable
                if not filtered_docs:
                    raise ValueError("LlamaParse returned no documents")
                print('LlamaParse succeeded!')
                break
            except HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt
                    print(f"Rate limit hit. waiting {wait}s before trying...")
                    time.sleep(wait)
                else:
                    print(f"HTTP error {e.response.status_code}: {e.response.text}")
                    documents = None
                    break
            except Exception as e:
                print(f"Unexpected error: {e}")
                wait = 2 ** attempt
                print(f"Rate limit hit. waiting {wait}s before trying...")
                time.sleep(wait)
                documents = None
                # break
                    
            
   
    if not documents:
            print(f"Use unstructured to parse because unstructured method is chosen.")
            try:
                #########################################
                method='unstructured'
                client = unstructured_client.UnstructuredClient(
                api_key_auth=unstructure_key)
                
                #########################################
                
                total_pages = 0

                for filename_full_path in file_list:
                    # To catch rate limit error:
                    for attempt in range(5):
                        try:
                   
                            req = operations.PartitionRequest(
                            partition_parameters=shared.PartitionParameters(
                                        files=shared.Files(
                            content=open(filename_full_path, "rb"),
                            file_name=filename_full_path,
                            ),
                            strategy=shared.Strategy.HI_RES,  # or FAST for simpler PDF
                            languages=['eng']
                                )
                            )
                            print("*************************************Attempting to partition...*************************************")
                            response = client.general.partition(request=req)
                            
                            elements = response.elements  # This is a list of element dicts
                            # with open("docs_list.pkl", "w", encoding="utf-8") as f:
                            #     f.write(str(elements))
                            total_pages += int(elements[-1]['metadata']["page_number"])
                            print(f"########################################################################The total pages: {total_pages}")

                            
                            all_elements.extend(elements)  # Collect all elements from all PDFs
                            # docs = [Document(page_content=el.text, metadata=el.metadata.__dict__) for el in all_elements if el.text]
                            print("Partition successful.")
                            break  # success, stop retrying
                        

                        except SDKError as e:
                            if hasattr(e, "status_code") and e.status_code == 429:
                                wait = 2 ** attempt  # exponential backoff: 1, 2, 4, 8, 16s
                                print(f"Rate limit reached. Retrying in {wait} seconds...")
                                time.sleep(wait)
                            else:
                                print(f"Error: {e}")
                                documents = None
                                raise
                    if all_elements:
                        docs = [
                                Document(
                                    page_content=el["text"],
                                    metadata=el["metadata"]
                                )
                                for el in all_elements
                                if "text" in el and el["text"].strip()  # ignore empty text
                            ]
                                        
                        # 2. Filter out the complex metadata objects
                        print(f'This is the number of total pages {total_pages}')
                            
                        filtered_docs = filter_complex_metadata(docs) # Each element here is an element
                        print(f'Number of vector embeddings being saved is {len(filtered_docs)}')
                    
            except Exception as e:
                print(f"Failed using unstructured to parse {e}")
                
    # Save each doc in pickel, in the same foler as the process_pdfs
    # Save the entire list to a file
    # pickle name
    if filtered_docs:
        try:
            pickle_name = os.path.join(cut_pdfs_path, f"docs_pickle_list_{method}.pkl")
            doc_pickle_path = os.path.join(cut_pdfs_path, f"doc_pickle_path_{method}.txt")
            with open(pickle_name, "wb") as f:
                pickle.dump(filtered_docs, f)
            with open(doc_pickle_path, "w") as f:
                f.write(str(doc_pickle_path))
            print(f"Saved {len(filtered_docs)} documents to docs_list.pkl")
            return filtered_docs, pickle_name, method
        except Exception as e:
            print(f"Failed to save to pickles {e}, use the mocked one instead")
    else:
        print('Use mock instead')
        return None
        

def load_docs_pickle(process_pdfs):
    # 2. Load the ENTIRE LIST back from the file
    try:
        pickle_path = glob.glob(f'{process_pdfs}/*.pkl')[0]
        with open(pickle_path, "rb") as f:
            loaded_docs = pickle.load(f)
        return loaded_docs
    except Exception as e:
        print(f'Failed to load pickle file {e}')
def get_visitor_id(request) -> str:
        visitor_id = request.session.get('visitor_id') # This will be the thread_id / user_id
        if not visitor_id:
            # We need to create a session if one doesn't exist yet.
            # Django often does this automatically, but being explicit is safe.
            if not request.session.session_key:
                request.session.create()
            
            # Use the session's unique key as our permanent visitor_id for this session.
            visitor_id = request.session.session_key
            request.session['visitor_id'] = visitor_id
            print("New session started. Visitor ID created:", visitor_id)
        return visitor_id


def rate_429_mock():

    # build a Response-like object
    resp = requests.Response()
    resp.status_code = 429
    resp._content = b'{"error":"rate limit"}'           # optional body
    resp.headers['Retry-After'] = '10'                  # optional helpful header
    # create and raise the HTTPError carrying that response
    err = requests.exceptions.HTTPError("429 Too Many Requests", response=resp)
    return err

resp = rate_429_mock()
    
    
    