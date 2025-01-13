from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
import torch 

def summarize_with_langchain(file_path, model_name="facebook/bart-large-cnn", num_sentences=3):
    """
    Summarize content from a .txt file using LangChain and HuggingFace pipeline.

    Parameters:
        file_path (str): Path to the .txt file.
        model_name (str): HuggingFace model for summarization.
        num_sentences (int): Number of sentences to include in the summary.

    Returns:
        str: The summarized content.
    """
    try:
        # Step 1: Load the text file
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        # Step 2: Split the text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)

        # Step 3: Embed the text for semantic search
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(texts, embeddings)

        # Step 4: Set up the HuggingFace summarization pipeline
        summarizer = pipeline("summarization", model=model_name, device=0 if torch.cuda.is_available() else -1)

        # Step 5: Create a RetrievalQA chain for summarization
        llm = HuggingFacePipeline(pipeline=summarizer)
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
        
        # Step 6: Query for a summary
        query = f"Summarize this text into {num_sentences} sentences."
        summary = qa_chain.run(query)
        
        return summary

    except FileNotFoundError:
        return "File not found. Please check the file path."
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
file_path = "file1.txt"  # Replace with your .txt file path
summary = summarize_with_langchain(file_path)
print("Summary:")
print(summary)
