from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from sentence_transformers import SentenceTransformer
import faiss
# Initialize the embedding model
model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(model_name)
model_name_dimensions = 384

index = faiss.IndexFlatL2(model_name_dimensions)
embeddend = "hi!! this is Ansh"

def embed_it(text):
    return embedding_model.encode(text)

docstore = InMemoryDocstore()

vector_faiss = FAISS(embed_it, index= index, docstore=docstore, index_to_docstore_id={})

ids = vector_faiss.add_texts(["hi", "name", "Colour", "Ansh"])

query_embeddings = embedding_model.encode([embeddend])

search =  vector_faiss.index.search(query_embeddings, 2)


