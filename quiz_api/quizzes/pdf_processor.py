import anthropic
import json
from PyPDF2 import PdfReader
from django.conf import settings
from .models import TempQuestion, TempAnswer
import re

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def extract_slides_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    slides = []
    slide_number = 1

    for page in reader.pages:
        text = page.extract_text()

        # Split the page content if it contains multiple slides
        potential_slides = re.split(r'\n(?=(?:Slide|^\d+\.)\s*\n)', text, flags=re.MULTILINE)

        for potential_slide in potential_slides:
            if potential_slide.strip():  # Ignore empty slides
                slides.append(f"Slide {slide_number}\n\n{potential_slide.strip()}\n")
                slide_number += 1

    return slides


def generate_questions(slides):
    all_slides = []

    for i, slide in enumerate(slides, 1):
        print(f"Processing Slide {i} of {len(slides)}...")

        if len(slide.split()) < 20:  # Skip slides with very little content
            print(f"Skipping Slide {i} due to insufficient content.")
            continue

        prompt = f"""
        You are an expert in creating educational content about databases. Based on the following slide content (Slide {i} of {len(slides)}), generate multiple-choice questions that directly test the understanding of the information presented. Each question should have 4 options (A, B, C, D). Provide the correct answer for each question.

        Guidelines:
        1. Use ONLY the information explicitly stated in the slide content. Do not introduce any external knowledge or inferences.
        2. Create questions that directly relate to the key points, definitions, and concepts presented in the slide.
        3. Use the exact wording and terminology from the slide whenever possible.
        4. Avoid creating questions about trivial details, slide titles, or formatting.
        5. Generate 1-3 questions per slide, depending on the content density.
        6. Ensure that the correct answer and at least one incorrect option are taken directly from the slide content.
        7. If the slide doesn't contain enough substantial information to create meaningful questions, don't generate any questions for that slide.

        Format the output as a JSON object with the following structure:
        {{
            "questions": [
                {{
                    "question_text": "Question text here",
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

        If no meaningful questions can be generated using only the slide content, return an empty questions array.

        Slide content:
        {slide}
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

        try:
            slide_questions = json.loads(message.content[0].text)
            if slide_questions['questions']:
                all_slides.append({
                    "slide_number": i,
                    "questions": slide_questions['questions']
                })
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for Slide {i}: {e}")
            continue

    return {"slides": all_slides}


def process_pdf_and_generate_questions(pdf_file, quiz):
    slides = extract_slides_from_pdf(pdf_file)
    questions_data = generate_questions(slides)

    total_questions = 0
    for slide_data in questions_data['slides']:
        for q_data in slide_data['questions']:
            temp_question = TempQuestion.objects.create(
                quiz=quiz,
                text=q_data['question_text'],
                question_type='mcq',
                slide_number=slide_data['slide_number']
            )

            for key, value in q_data['options'].items():
                TempAnswer.objects.create(
                    temp_question=temp_question,
                    text=value,
                    is_correct=(key == q_data['correct_answer']),
                )
            total_questions += 1

    return total_questions