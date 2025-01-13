import os
import torch
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline

def summarize_and_generate_knowledge_graph(file_path, output_file, model_name="facebook/bart-large-cnn", summary_length=300):
    """
    Summarize content from a .txt file using LangChain and generate a detailed knowledge graph.
    """
    try:
        # Step 1: Load the text file
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()

        # Check if documents are empty
        if len(documents) == 0:
            print("The document is empty.")
            return

        # Step 2: Split the text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Adjust chunk size
        texts = text_splitter.split_documents(documents)

        # Check if texts are empty
        if len(texts) == 0:
            print("The document couldn't be split into chunks.")
            return

        # Step 3: Embed the text for semantic search
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(texts, embeddings)

        # Step 4: Set up the HuggingFace summarization pipeline
        summarizer = pipeline("summarization", model=model_name, device=0 if torch.cuda.is_available() else -1)

        # Step 5: Create a RetrievalQA chain for summarization
        llm = HuggingFacePipeline(pipeline=summarizer)
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

        # Step 6: Query for a longer summary
        query = f"Summarize this text in about {summary_length} words, keeping key details intact."
        summary = qa_chain.invoke({"query": query})

        # Validate summary response
        if not summary or 'result' not in summary:
            print("Summary could not be generated.")
            return

        # Step 7: Save the summary to a .txt file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary['result'])
        
        print(f"Summary saved to {output_file}")

        # Step 8: Generate Knowledge Graph
        print("Generating knowledge graph...")
        nlp = spacy.load("en_core_web_sm")  # Ensure the spaCy model is downloaded
        doc = nlp(" ".join([t.page_content for t in texts]))

        # Extract detailed relations and entities
        edges = []
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in ("nsubj", "dobj") and token.head.is_alpha and token.text != token.head.text:
                    edges.append((token.text, token.head.text, token.dep_))

        # Validate edges
        if not edges:
            print("No valid relationships found for knowledge graph.")
            return

        # Create a graph with detailed edge relationships
        graph = nx.DiGraph()
        for edge in edges:
            graph.add_edge(edge[0], edge[1], label=edge[2])

        # Plot the graph with enhanced visuals
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(graph, seed=42)
        nx.draw(graph, pos, with_labels=True, node_size=4000, node_color="lightgreen", font_size=10, font_weight="bold", edge_color="gray")
        edge_labels = nx.get_edge_attributes(graph, 'label')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red', font_size=9)
        plt.title("Knowledge Graph", fontsize=16)
        plt.show()

        print("Knowledge graph generated successfully.")

    except FileNotFoundError:
        print("Input file not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example Usage
file_path = "file2.txt"  # Provide the path to your input file
output_file = "output_summary.txt"    # Provide the output file path for the summary

summarize_and_generate_knowledge_graph(file_path, output_file)
