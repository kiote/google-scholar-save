import os
from typing import List
from langchain.schema import Document

# 1) LangChain modules for loading text, splitting, embeddings, and vector store
from langchain.docstore.document import Document as LC_Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 2) LangChain modules for the LLM and QA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# 3) For optional named tracing sessions (see below)
from langchain.callbacks import tracing_enabled

# --------------------------------------------------
# Configuration
# --------------------------------------------------

FOLDER_PATH = "./docs/papers"

# The same questions you used before
QUESTIONS = [
    {
        "id": 1,
        "question": "Extract no more than 5 ideas from this paper to be used as descriptive keywords. List them just comma-separated regular text"
    },
    {
        "id": 2,
        "question": "what are the objectives of the paper in one sentence?"
    },
    {
        "id": 3,
        "question": "what are Ethical concerns (anything in the paper discussing the use of ethic frameworks to prepare their data and model)"
    },
    {
        "id": 4,
        "question": "what educational or behavioural theories used in this paper?"
    },
    {
        "id": 5,
        "question": "in one sentence list what are methods (algorithms) used in paper. Make sure they used in \"Methods\" or \"Methodology\" section, not just discussed in general."
    },
    {
        "id": 6,
        "question": "How many participants (sample)? and what datasets were used in the paper."
    },
    {
        "id": 7,
        "question": "What is the field of study particiapnts were tested?"
    },
    {
        "id": 8,
        "question": "what was used as an input features for the model(s)?"
    },
    {
        "id": 9,
        "question": "Describe validation method and metrics for evaluation."
    },
    {
        "id": 10,
        "question": "Does paper mention any data bias? Or data inconsistency, sparsity or imbalance? It should be mentioned not in context of general problem, but what this particular paper did about it."
    },
    {
        "id": 11,
        "question": "How does paper address and evaluate sequential stability?"
    },
    {
        "id": 12,
        "question": "How does paper addresses and evaluate interpretability? does paper discuss interpretability in this meaning: Interpretability and Explainability Interpretability in machine learning involves elucidating model decisions in a manner comprehensible to humans, revealing the underlying reasoning process. We use the terms interpretable and explainable interchangeably, collectively referred to as interpretability. Key difference in interpretability Probabilities of skill mastery: These are often treated as an output-level interpretability metric, summarizing the learner’s overall skill state. Focus is on the end result (skill level) rather than the journey (how the level was reached). Process-level interpretability: This method delves into process-level interpretability, emphasizing the journey by uncovering how individual or grouped interactions shape the model's predictions. It provides insights into the reasoning process of the DKT model, making the predictionsmore transparent Important: provide direct quotations from the paper's text, like what exact sentences did you use to make this conclusion. Provide sections titles, where you got this info from"
    },
    {
        "id": 13,
        "question": "Does paper discuss limitations, challanges and future directions for the work?"
    }
]

# A generic prompt template; you can customize as needed.
PROMPT_TEMPLATE = """You are a helpful assistant strictly limited to the context provided. 
Use only the text below to answer the question. 
If the text does not provide enough information, say you don't know.
Important: provide direct quotations from the paper's text, like what exact sentences did you use to make this conclusion.
Provide sections titles, where you got this info from. Provide answer as plain text, no markdown

Context:
{context}

Question: {question}

Answer (plain text only):"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE, 
    input_variables=["context", "question"]
)

# --------------------------------------------------
# Helper Function
# --------------------------------------------------

def build_vectorstore_from_text(text: str) -> FAISS:
    """
    Given a file's text, split it into smaller chunks,
    embed them, and store them in a local FAISS vector store.
    Returns the vectorstore object.
    """
    raw_doc = LC_Document(page_content=text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents([raw_doc])

    embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY from environment
    vectorstore = FAISS.from_documents(docs, embedding=embeddings)
    return vectorstore


def answer_question(vectorstore: FAISS, question: str) -> str:
    """
    Given a vector store and a question, retrieve relevant chunks
    and run the LLM chain to get an answer. 
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(model_name="o1-preview", temperature=1.0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # simplest approach
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )

    response = qa_chain.run(question)
    return response.strip()

# --------------------------------------------------
# Main Script
# --------------------------------------------------

def main():
    # Optionally, name your session with a context manager:
    # with tracing_enabled("my_rag_session"):

    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(".txt"):
            txt_path = os.path.join(FOLDER_PATH, filename)
            
            with open(txt_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            vectorstore = build_vectorstore_from_text(file_content)

            base_name = os.path.splitext(filename)[0]
            md_filename = base_name + ".md"
            md_path = os.path.join(FOLDER_PATH, md_filename)

            for q in QUESTIONS:
                answer = answer_question(vectorstore, q["question"])
                md_content = (
                    f"## Question {q['id']}\n"
                    f"**{q['question']}**\n"
                    f"{answer}\n\n"
                )
                with open(md_path, "a", encoding="utf-8") as md_file:
                    md_file.write(md_content)

            print(f"Processed '{filename}' -> '{md_filename}'")


if __name__ == "__main__":
    # Make sure OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

    # Run
    main()
