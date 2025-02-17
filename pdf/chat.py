import os
from openai import OpenAI

openai = OpenAI()

if not openai.api_key:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

questions = [
    # {
    #     "id": 1,
    #     "question": "Extract no more than 5 ideas from this paper to be used as descriptive keywords. List them just comma-separated regular text"
    # },
    # {
    #     "id": 2,
    #     "question": "what are the objectives of the paper in one sentence?"
    # },
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

FOLDER_PATH = "./docs/papers"

def ask_question_about_text(file_content: str, question: str) -> str:
    """
    Send a prompt to OpenAI's model, telling it to answer ONLY based on the provided text.
    Return the answer string.
    """
    system_message = (
        "You are a helpful assistant strictly limited to the context provided. "
        "Use only the text below to answer the question. "
        "If the text does not provide enough information, say you don't know.\n\n"
        "Important: provide direct quotations from the paper's text, like what exact sentences did you use to make this conclusion."
        "Provide sections titles, where you got this info from. Privide answer as a plain text, no markdown"
        f"=== TEXT START ===\n{file_content}\n=== TEXT END ==="
    )

    user_message = question

    response = openai.chat.completions.create(
        # model="o1-2024-12-17",
        model="o1-mini-2024-09-12",
        messages=[
            {"role": "user", "content": system_message},
            {"role": "user", "content": user_message},
        ]
    )

    answer = response.choices[0].message.content
    return answer.strip()

def main():
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(".txt"):
            txt_path = os.path.join(FOLDER_PATH, filename)
            
            # Read the .txt file content
            with open(txt_path, "r", encoding="utf-8") as f:
                file_content = f.read()
            
            # Prepare the output filename (replace .txt with .md)
            base_name = os.path.splitext(filename)[0]  # e.g. "10.1016_j.eswa.2023.123128"
            md_filename = base_name + ".md"
            md_path = os.path.join(FOLDER_PATH, md_filename)

            md_output_lines = []
            for q in questions:
                answer = ask_question_about_text(file_content, q["question"])
                
                # Markdown formatting
                md_output_lines.append(f"## Question {q['id']}\n")
                md_output_lines.append(f"**{q['question']}**\n")
                md_output_lines.append(f"{answer}\n\n")

            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write("\n".join(md_output_lines))
            
            print(f"Processed '{filename}' -> '{md_filename}'")


if __name__ == "__main__":
    main()
