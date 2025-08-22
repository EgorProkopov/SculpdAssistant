import json
import os

import dotenv
import gradio as gr

from src.training_plan.utils import create_train_assistant


def generate_first_week(raw_user_data: str, raw_scanner_data: str) -> str:
    dotenv.load_dotenv()
    raw_user_data = json.loads(raw_user_data)
    raw_scanner_data = json.loads(raw_scanner_data)

    train_assistant = create_train_assistant(
        raw_user_data=raw_user_data,
        raw_scanner_data=raw_scanner_data,
    )
    return train_assistant.generate_first_week()


def generate_next_week(
    raw_user_data: str, raw_feedback: str, raw_previous_week: str
) -> str:
    dotenv.load_dotenv()
    raw_user_data = json.loads(raw_user_data)
    previous_week = json.loads(raw_previous_week)

    train_assistant = create_train_assistant(
        raw_user_data=raw_user_data,
        raw_scanner_data=None,
    )
    return train_assistant.generate_next_week(
        feedback_key=raw_feedback,
        previous_week=previous_week,
    )


if __name__ == "__main__":
    dotenv.load_dotenv()
    user_info_placeholder = '{\n"email": "newuser@example.com", \n"image": "http://example.com/image.jpg", \n"name": "New User", \n"gender": "male", \n"birthday": "1995-05-15T00:00:00Z", \n"height": 180.5, \n"height_type": "cm", \n"weight": 75.2, \n"weight_type": "kg", \n"fitness_level": "advanced", \n"improve_body_parts": ["none"], \n"exercise_limitations": ["no_overhead_pressing", "no_squatting", "no_hip_hinge_movements"], \n"nutrition_goal": "maintain_weight", \n"equipment_list": ["barbell", "dumbbells", "machines", "cables"], \n"training_days": 6, \n"workout_time": 80 }'
    previous_week_placeholder = '{}'

    first_week_interface = gr.Interface(
        fn=generate_first_week,
        inputs=[
            gr.TextArea(label="User Information", placeholder=user_info_placeholder),
            gr.TextArea(label="Scanner Info"),
            gr.TextArea(label="Program Generation Rules")
        ],
        outputs=gr.Textbox(label="Training Plan"),
        title="First Week Generation",
        description="Upload user information and scanner output to receive first week training plan",
    )

    next_week_prompt_text_area = gr.TextArea(label="Program Generation Rules")
    next_week_prompt_placeholder = os.getenv("")
    next_week_prompt_text_area.value = "need a text placeholder"

    next_week_interface = gr.Interface(
        fn=generate_next_week,
        inputs=[
            gr.TextArea(label="User Information", placeholder=user_info_placeholder),
            gr.Textbox(label="Feedback Key", placeholder="hard"),
            gr.TextArea(label="Previous Week JSON", placeholder=previous_week_placeholder),
            next_week_prompt_text_area
        ],
        outputs=gr.Textbox(label="Training Plan"),
        title="Next Week Generation",
        description="Upload user information, feedback, and previous week plan to receive next week training plan",
    )

    interface = gr.TabbedInterface(
        [first_week_interface, next_week_interface], ["First Week", "Next Week"]
    )

    interface.launch(share=True)
