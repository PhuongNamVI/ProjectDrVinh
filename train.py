from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

DATA_PATH = "data/"
DB_FAISS_PATH = "vectorstores/db_faiss"


def create_vector_db():
    loader = PyPDFDirectoryLoader("data")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )

    db = FAISS.from_documents(texts, embeddings)
    db.save_local(DB_FAISS_PATH)

    if not documents:
        print("No documents loaded. Please check the PDF directory.")
        return


if __name__ == "__main__":
    create_vector_db()
