import os
import dotenv
import json

import pandas as pd
from omegaconf import OmegaConf, DictConfig

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate

from src.exercises.exercises_filter import ExercisesFilter
from src.exercises.exercises_formatter import ExercisesFormatter
from src.exercises.exercises_processor import ExercisesProcessor
from src.training_plan.train_week import TrainWeek
from src.user_data.user_data_formatter import UserDataFormatter
from src.user_data.age_based_adjustments import AgeBasedAdjustmentsProcessor, AgeBasedAdjustmentsFormatter
from src.scanner_data_formatter import ScannerDataFormatter
from src.user_data.user_data_processor import UserDataProcessor


class TrainAssistant:
    def __init__(
            self,
            API_KEY: str,
            train_week: TrainWeek,
            available_exercises: pd.DataFrame,
            exercises_formatter: ExercisesFormatter,
            user_data_formatter: UserDataFormatter,
            age_formatter: AgeBasedAdjustmentsFormatter,
            scanner_formatter: ScannerDataFormatter,
            train_assistant_config: DictConfig
    ):

        self.train_week = train_week
        self.available_exercises = available_exercises
        self.exercises_formatter = exercises_formatter
        self.user_data_formatter = user_data_formatter
        self.age_formatter = age_formatter
        self.scanner_formatter = scanner_formatter

        self.train_assistant_config = train_assistant_config
        prompt = self.train_assistant_config["train_assistant"]["prompt_template"]

        model_name = self.train_assistant_config["train_assistant"]["model"]
        temperature = self.train_assistant_config["train_assistant"]["temperature"]

        self.llm = ChatOpenAI(api_key=API_KEY, model=model_name, temperature=temperature)
        self.prompt_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(prompt)
        ])
        self.chain = self.prompt_template | self.llm

    def generate_train_program(self) -> str:
        week_template = str(self.train_week.week)
        user_data = self.user_data_formatter.data_format()
        scanner_recommendations = self.scanner_formatter.data_format()
        age_recommendations = self.age_formatter.data_format()

        exercises_formatted = self.exercises_formatter.data_format(self.available_exercises)

        result = self.chain.invoke(
            {
                "week_template": week_template,
                "user_data": user_data,
                "scanner_recommendations": scanner_recommendations,
                "age_recommendations": age_recommendations,
                "available_exercises": exercises_formatted
            }
        )
        processed_result = result.content.strip()
        return processed_result

    def convert_result_to_json(self, processed_result: str) -> dict:
        if processed_result.startswith("```") and processed_result.endswith("```"):
            processed_result = "\n".join(processed_result.splitlines()[1:-1]).strip()

        try:
            structured_data = json.loads(processed_result)
        except json.JSONDecodeError as e:
            raise ValueError("Failed to decode JSON. Output received:\n" + processed_result) from e

        return structured_data


if __name__ == "__main__":
    dotenv.load_dotenv()

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

    user_data_json_path = r"F:\SCULPD\SculpdAssistant\data\user_data\user_data_15-19.json"
    scanner_data_json_path = r"F:\SCULPD\SculpdAssistant\data\scanner_info\scanner_output_15-19.json"

    with open(user_data_json_path, "r", encoding="utf-8") as file:
        raw_user_data = json.load(file)
    with open(scanner_data_json_path, "r", encoding="utf-8") as file:
        raw_scanner_data = json.load(file)

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

    train_week = TrainWeek(week_templates=train_weeks_templates, train_days_num=4)

    raw_df = pd.read_csv(r"F:\SCULPD\SculpdAssistant\data\exercises\sculpd_exercise_processed.csv")
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
    print(train_program)