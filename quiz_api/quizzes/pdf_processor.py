import anthropic
import json
from PyPDF2 import PdfReader
from django.conf import settings
from .models import TempQuestion, TempAnswer

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n\n"  # Add extra newlines between pages
    return text


def split_text(text, max_chunk_size=8000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    for word in words:
        if current_size + len(word) > max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks


def generate_questions(lecture_content):
    chunks = split_text(lecture_content)
    all_questions = []

    for i, chunk in enumerate(chunks):
        prompt = f"""
            You are an expert in creating comprehensive educational content. Based on the following lecture content (part {i + 1} of {len(chunks)}), generate multiple-choice questions that test general understanding of database concepts. Each question should have 4 options (A, B, C, D). Provide the correct answer for each question.

            Important guidelines:
            1. Focus ONLY on general concepts and principles, NOT on specific examples or sections from the lecture.
            2. Do not reference any diagrams, images, or specific lecture sections (e.g., "STUDENT 29").
            3. Create questions that can stand alone without needing to refer back to the lecture notes.
            4. Avoid questions about specific database instances or examples used in the lecture.
            5. Instead, formulate questions about general database principles, terminology, and concepts.

            Ensure that the questions:
            1. Cover important database concepts mentioned in the content
            2. Range from basic recall of definitions to complex application of database principles
            3. Provide a thorough assessment of general database knowledge
            4. Include questions about database design, normalization, keys, relationships, and other relevant topics
            5. Can be answered by someone with a good understanding of database concepts, even if they haven't seen this specific lecture
            6. Generate at least 30 questions, or more if the content warrants it

            Format the output as a JSON object with the following structure:
            {{
                "questions": [
                    {{
                        "question": "Question text here",
                        "options": {{
                            "A": "Option A text",
                            "B": "Option B text",
                            "C": "Option C text",
                            "D": "Option D text"
                        }},
                        "correct_answer": "Correct option letter"
                    }},
                    ...
                ]
            }}

            Lecture content (part {i + 1} of {len(chunks)}):
            {chunk}
            """

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Print the raw response
        print(f"Raw response for chunk {i + 1}:")
        print(message.content[0].text)
        print("=" * 50)  # Separator for readability

        try:
            chunk_questions = json.loads(message.content[0].text)
            all_questions.extend(chunk_questions['questions'])
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for chunk {i + 1}: {e}")
            # Optionally, you can continue to the next chunk instead of breaking
            continue

    return {"questions": all_questions}


def process_pdf_and_generate_questions(pdf_file, quiz):
    lecture_content = extract_text_from_pdf(pdf_file)
    questions_data = generate_questions(lecture_content)

    for q_data in questions_data['questions']:
        temp_question = TempQuestion.objects.create(
            quiz=quiz,
            text=q_data['question'],
            question_type='mcq',
        )

        for key, value in q_data['options'].items():
            TempAnswer.objects.create(
                temp_question=temp_question,
                text=value,
                is_correct=(key == q_data['correct_answer']),
            )

    return len(questions_data['questions'])