import os
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from .vector_db import get_vector_store

LLM_MODEL = os.getenv("LLM_MODEL", "phi4")


# Function to get the prompt templates for generating alternative questions and answering based on context
def get_prompt():
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""Sei un assistente per la validazione di piani di test e di collaudo, puoi suggerire test alternativi, puoi evidenziare mancanze nei piani di test o di collaudo. Devi usare solo i documenti forniti per rispondere. Domanda originale: {question}""",
    )

    template = """Rispondi solo usando i documenti forniti.:
    {context}
    Domanda: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    return QUERY_PROMPT, prompt


# Main function to handle the query process
def query(input, model, collection_name):
    if input:
        # Initialize the language model with the specified model name
        llm = OllamaLLM(model=model, num_ctx=32128)
        # Get the vector database instance

        # Get the prompt templates
        QUERY_PROMPT, prompt = get_prompt()

        # Set up the retriever to generate multiple queries using the language model and the query prompt
        vector_store = get_vector_store(collection_name)
        retriever = MultiQueryRetriever.from_llm(
            vector_store.as_retriever(), llm, prompt=QUERY_PROMPT
        )

        # Define the processing chain to retrieve context, generate the answer, and parse the output
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(input)

        return response

    return None
