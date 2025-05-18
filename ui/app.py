import os
import dotenv
import pandas as pd
from omegaconf import OmegaConf
import json

import gradio as gr

from src.exercises.exercises_filter import ExercisesFilter
from src.exercises.exercises_formatter import ExercisesFormatter
from src.exercises.exercises_processor import ExercisesProcessor
from src.training_plan.train_assistant import TrainAssistant
from src.training_plan.train_week import TrainWeek
from src.user_data.user_data_formatter import UserDataFormatter
from src.user_data.age_based_adjustments import AgeBasedAdjustmentsProcessor, AgeBasedAdjustmentsFormatter
from src.scanner_data_formatter import ScannerDataFormatter
from src.user_data.user_data_processor import UserDataProcessor


def get_training_plan(raw_user_data: str, raw_scanner_data: str):
    raw_user_data = json.loads(raw_user_data)
    raw_scanner_data = json.loads(raw_scanner_data)

    API_KEY = os.getenv("API_KEY")
    TRAIN_ASSISTANT_CONFIG_PATH = os.getenv("TRAIN_ASSISTANT_CONFIG_PATH")
    train_assistant_config = OmegaConf.load(TRAIN_ASSISTANT_CONFIG_PATH)

    DATA_PROCESSING_CONFIG_PATH = os.getenv("DATA_PROCESSING_CONFIG_PATH")
    data_processing_config = OmegaConf.load(DATA_PROCESSING_CONFIG_PATH)
    user_data_processing_config = data_processing_config["user_data_processing"]
    user_data_formatter_config = data_processing_config["user_data_formatter"]

    AGE_BASED_ADJUSTMENTS_CONFIG_PATH = os.getenv("AGE_BASED_ADJUSTMENTS_CONFIG_PATH")
    age_based_adjustments_config = OmegaConf.load(AGE_BASED_ADJUSTMENTS_CONFIG_PATH)

    DATA_PROCESSING_CONFIG_PATH = os.getenv("DATA_PROCESSING_CONFIG_PATH")
    data_processing_config = OmegaConf.load(DATA_PROCESSING_CONFIG_PATH)
    scanner_data_formatter_config = data_processing_config["scanner_data_formatter"]

    TRAIN_WEEKS_TEMPLATES_PATH = os.getenv("TRAIN_WEEKS_TEMPLATES_PATH")

    EXERCISES_CONFIG_PATH = os.getenv("EXERCISES_CONFIG_PATH")
    exercises_config = OmegaConf.load(EXERCISES_CONFIG_PATH)
    exercises_processor_config = exercises_config["exercises_processor"]
    exercises_planner_config = exercises_config["exercises_planner"]

    EXERCISES_RAW_DF_PATH = os.getenv("EXERCISES_RAW_DF_PATH")

    user_data_processor = UserDataProcessor(
        user_data=raw_user_data,
        user_data_processing_config=user_data_processing_config
    )
    user_data_formatter = UserDataFormatter(
        user_data_processor=user_data_processor, user_data_formatter_config=user_data_formatter_config
    )
    train_days_number = user_data_processor.get_training_days()

    age = user_data_processor.get_age()
    age_based_adjustments = AgeBasedAdjustmentsProcessor(
        age_based_adjustments_config=age_based_adjustments_config
    )
    age_period = age_based_adjustments.select_age_periods_adjustments(age)
    age_formatter = AgeBasedAdjustmentsFormatter(
        age_group_data=age_period,
        age_based_adjustments_config=age_based_adjustments_config
    )

    scanner_formatter = ScannerDataFormatter(
        scanner_data=raw_scanner_data, scanner_data_formatter_config=scanner_data_formatter_config
    )

    with open(TRAIN_WEEKS_TEMPLATES_PATH, "r", encoding="utf-8") as file:
        train_weeks_templates = json.load(file)

    train_week = TrainWeek(week_templates=train_weeks_templates, train_days_num=train_days_number)

    raw_df = pd.read_csv(EXERCISES_RAW_DF_PATH)
    exercises_processor = ExercisesProcessor(
        raw_exercises_df=raw_df, exercises_processor_config=exercises_processor_config
    )
    exercises_filter = ExercisesFilter(
        exercises_processor=exercises_processor, exercises_planner_config=exercises_planner_config
    )

    skill_level = user_data_processor.get_fitness_level()
    available_equipment = user_data_processor.get_equipment_list()

    processed_df = exercises_processor.processed_df
    available_exercises = exercises_filter.get_available_exercises_by_skill_level(
        df=processed_df, skill_level=skill_level
    )
    available_exercises = exercises_filter.get_available_exercises_by_equipment(
        df=available_exercises, available_equipment=available_equipment
    )
    exercises_formatter = ExercisesFormatter(exercises_config)

    train_assistant = TrainAssistant(
        API_KEY=API_KEY,
        train_week=train_week,
        available_exercises=available_exercises,
        exercises_formatter=exercises_formatter,
        user_data_formatter=user_data_formatter,
        age_formatter=age_formatter,
        scanner_formatter=scanner_formatter,
        train_assistant_config=train_assistant_config
    )

    train_program = train_assistant.generate_train_program()
    return train_program


if __name__ == "__main__":
    dotenv.load_dotenv()
    user_info_placeholder = '{\n"email": "newuser@example.com", \n"image": "http://example.com/image.jpg", \n"name": "New User", \n"gender": "male", \n"birthday": "1995-05-15T00:00:00Z", \n"height": 180.5, \n"height_type": "cm", \n"weight": 75.2, \n"weight_type": "kg", \n"fitness_level": "advanced", \n"improve_body_parts": ["none"], \n"exercise_limitations": ["no_overhead_pressing", "no_squatting", "no_hip_hinge_movements"], \n"nutrition_goal": "maintain_weight", "equipment_list": ["barbell", "dumbbells", "machines", "cables"], \n"training_days": 6, "workout_time": 90 }'

    interface = gr.Interface(
        fn=get_training_plan,
        inputs=[
            gr.TextArea(label='User Information', placeholder=user_info_placeholder),
            gr.TextArea(label='Scanner Info')
        ],
        outputs=gr.Textbox(label="Training Plan"),
        title="SCULPD Train Assistant",
        description="Write your user information and scanner information to receive personalized training plan."
    )

    interface.launch(share=True)