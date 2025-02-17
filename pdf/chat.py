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
    {
        "id": 2,
        "question": "what are the objectives of the paper in one sentence? important: provide direct quotations from the paper's text. Provide sections titles, where you got this info from. Privide answer as a plain text, no markdown"
    },
    
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
