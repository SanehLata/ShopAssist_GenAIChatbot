import os
from chromadb.utils import embedding_functions
from groq import Groq
import pandas
from app.config import FAQS_PATH, EMBEDDING_MODEL
from chromadb import PersistentClient

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )

# create persistent client function
def get_chroma_client():
    # Returns persistent Chroma client. Ensures DB is reused across Streamlit reruns and app restarts.
    return PersistentClient(path="./chroma_db")

groq_client = Groq()
collection_name_faq = 'faqs'


def ingest_faq_data(path, chroma_client):
    print("path =", path)
    existing_collections = [c.name for c in chroma_client.list_collections()]
    print("Existing collections:", existing_collections)  # ✅ ADDED debug
    if collection_name_faq not in existing_collections:
        print("Ingesting FAQ data into Chromadb...")
        collection = chroma_client.create_collection(
            name=collection_name_faq,
            embedding_function=ef
        )

        df = pandas.read_csv(path)

        docs = df['question'].to_list()
        metadata = [{'answer': ans} for ans in df['answer'].to_list()]

        ids = [f"id_{i}" for i in range(len(docs))]

        collection.add(
            documents=docs,
            metadatas=metadata,
            ids=ids
        )

        print(f"FAQ Data successfully ingested into Chroma collection: {collection_name_faq}")

    else:
        print(f"Collection: {collection_name_faq} already exists")


def get_relevant_qa(query, chroma_client):
    collection = chroma_client.get_collection(
        name=collection_name_faq,
        embedding_function=ef
    )
    result = collection.query(
        query_texts=[query],
        n_results=2
    )
    return result


def generate_answer(query, context):
    prompt = f'''You are a helpful and professional ecommerce customer support assistant.

        Your goal is to answer customer questions using the provided CONTEXT.
        
        Instructions:
        - Use the context to provide the best possible helpful answer.
        - Even if the exact words in the question are not present, use related information from the context.
        - Be polite, clear, and customer-friendly.
        - If the context partially answers the question, provide the relevant information and explain clearly.
        - Only say you don't know if the context contains absolutely no relevant information.
    
    CONTEXT: {context}
    
    QUESTION: {query}
    '''
    completion = groq_client.chat.completions.create(
        model=os.environ['GROQ_MODEL'],
        messages=[
            {
                "role": "system",
                "content": "You are a helpful and professional ecommerce customer support assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return completion.choices[0].message.content


def faq_chain(query, chroma_client):
    result = get_relevant_qa(query, chroma_client)
    context = "".join([r.get('answer') for r in result['metadatas'][0]])
    print("Context:", context)
    answer = generate_answer(query, context)
    return answer


if __name__ == '__main__':
    chroma_client = get_chroma_client()
    ingest_faq_data(FAQS_PATH, chroma_client)
    query = "what's your policy on defective products?"
    # query = "Do you take cash as a payment option?"
    # result = get_relevant_qa(query)
    answer = faq_chain(query, chroma_client)
    print("Answer:",answer)