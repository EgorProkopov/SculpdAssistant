import os
import dotenv
import json
import logging
import pandas as pd
from omegaconf import OmegaConf, DictConfig

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate

from src.exercises.exercises_filter import ExercisesFilter
from src.exercises.exercises_formatter import ExercisesFormatter
from src.exercises.exercises_processor import ExercisesProcessor
from src.feedback_formatter import FeedbackFormatter
from src.previous_week_formatter import TrainingWeekFormatter
from src.training_plan.train_week import TrainWeek
from src.user_data.user_data_formatter import UserDataFormatter
from src.user_data.age_based_adjustments import AgeBasedAdjustmentsProcessor, AgeBasedAdjustmentsFormatter
from src.scanner_data_formatter import ScannerDataFormatter
from src.user_data.user_data_processor import UserDataProcessor

from src.logger import get_logger


class TrainAssistant:
    def __init__(
            self,
            API_KEY: str,
            train_assistant_config: DictConfig,
            data_processing_config: DictConfig,
            age_based_adjustments_config: DictConfig,
            exercises_config: DictConfig,
            feedback_config: DictConfig,
            raw_user_data: dict,
            raw_scanner_data: dict | None,
            train_weeks_templates: dict,
            exercises_processor: ExercisesProcessor,
            training_program_examples_dir: str | None = None
    ):
        self.llm = ChatOpenAI(api_key=API_KEY)

        self.train_assistant_config = train_assistant_config

        self.exercises_processor = exercises_processor

        self.__init_assistant(
            data_processing_config=data_processing_config,
            age_based_adjustments_config=age_based_adjustments_config,
            exercises_config=exercises_config,
            feedback_config=feedback_config,
            raw_user_data=raw_user_data,
            raw_scanner_data=raw_scanner_data,
            train_weeks_templates=train_weeks_templates,
        )

        self.avatar_examples = ""
        if training_program_examples_dir and os.path.isdir(training_program_examples_dir):
            self.avatar_examples = self.__load_avatar_examples(training_program_examples_dir)

        self.logger = get_logger(name=self.__class__.__name__, level=logging.DEBUG)

    @staticmethod
    def __load_avatar_examples(examples_dir: str) -> str:
        examples = []
        for file_name in sorted(os.listdir(examples_dir)):
            if file_name.endswith(".txt"):
                file_path = os.path.join(examples_dir, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    examples.append(file.read().strip())
        return "\n\n".join(examples)

    def __init_chain(self, prompt, model_name, temperature):
        self.llm.model_name = model_name
        if model_name == "gpt4o":
            self.llm.temperature = temperature

        prompt_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(prompt)
        ])
        chain = prompt_template | self.llm
        return chain

    def __init_assistant(
            self,
            data_processing_config: DictConfig,
            age_based_adjustments_config: DictConfig,
            exercises_config: DictConfig,
            feedback_config: DictConfig,
            raw_user_data: dict,
            raw_scanner_data: dict,
            train_weeks_templates: dict
    ):
        # user data formatter
        user_data_processing_config = data_processing_config["user_data_processing"]
        user_data_formatter_config = data_processing_config["user_data_formatter"]
        user_data_processor = UserDataProcessor(raw_user_data, user_data_processing_config)
        self.user_data_formatter = UserDataFormatter(user_data_processor, user_data_formatter_config)

        # age based adjustments formatter
        age = user_data_processor.get_age()
        age_based_adjustments_processor = AgeBasedAdjustmentsProcessor(age_based_adjustments_config)
        age_period = age_based_adjustments_processor.select_age_periods_adjustments(age)
        self.age_formatter = AgeBasedAdjustmentsFormatter(age_period, age_based_adjustments_config)

        # scanner data formatter
        if raw_scanner_data:
            scanner_data_formatter_config = data_processing_config["scanner_data_formatter"]
            self.scanner_formatter = ScannerDataFormatter(raw_scanner_data, scanner_data_formatter_config)

        # train week
        train_days_number = user_data_processor.get_training_days()
        self.train_week = TrainWeek(week_templates=train_weeks_templates, train_days_num=train_days_number)

        # exercises formatter and available_exercises
        exercises_planner_config = exercises_config["exercises_planner"]
        exercises_filter = ExercisesFilter(self.exercises_processor, exercises_planner_config)

        skill_level = user_data_processor.get_fitness_level()
        available_equipment = user_data_processor.get_equipment_list()
        day_types = self.train_week.day_types

        available_exercises = exercises_filter.get_available_exercises_by_equipment(
            df=self.exercises_processor.processed_df, available_equipment=available_equipment
        )
        available_exercises = exercises_filter.get_available_exercises_by_skill_level(
            df=available_exercises, skill_level=skill_level
        )
        available_exercises_by_day_type = exercises_filter.get_available_exercises_by_day_type(
            df=available_exercises, day_types=day_types
        )
        self.available_exercises_by_day_type = available_exercises_by_day_type
        self.exercises_formatter = ExercisesFormatter(exercises_config)

        self.train_week_formatter = TrainingWeekFormatter()
        self.feedbaack_formatter = FeedbackFormatter(feedback_config)

    def generate_first_week(self) -> str:
        prompt = self.train_assistant_config["train_assistant"]["first_week"]["prompt_template"]
        model_name = self.train_assistant_config["train_assistant"]["first_week"]["model"]
        temperature = self.train_assistant_config["train_assistant"]["first_week"]["temperature"]

        chain = self.__init_chain(prompt, model_name, temperature)

        week_template = str(self.train_week.week)
        user_data = self.user_data_formatter.data_format()
        scanner_recommendations = self.scanner_formatter.data_format()
        age_recommendations = self.age_formatter.data_format()
        exercises_formatted = self.exercises_formatter.data_format(self.available_exercises_by_day_type)
        avatar_examples = self.avatar_examples

        self.logger.debug(f"Week Template: \n{week_template}")
        self.logger.debug(f"User Data Formatted: \n{user_data}")
        self.logger.debug(f"Scanner Recommendations Formatted: \n{scanner_recommendations}")
        self.logger.debug(f"Age Recommendations Formatted: \n{age_recommendations}")
        self.logger.debug(f"Exercises List Formatted: \n{exercises_formatted}")

        result = chain.invoke(
            {
                "week_template": week_template,
                "user_data": user_data,
                "scanner_recommendations": scanner_recommendations,
                "age_recommendations": age_recommendations,
                "available_exercises": exercises_formatted,
                "avatars_examples": avatar_examples
            }
        )
        processed_result = result.content.strip()
        self.logger.info(f"Training Plan Result: \n{processed_result}")
        return processed_result

    def generate_next_week(self, feedback_key: str, previous_week: dict) -> str:
        prompt = self.train_assistant_config["train_assistant"]["next_week"]["prompt_template"]
        model_name = self.train_assistant_config["train_assistant"]["next_week"]["model"]
        temperature = self.train_assistant_config["train_assistant"]["next_week"]["temperature"]

        chain = self.__init_chain(prompt, model_name, temperature)

        week_template = str(self.train_week.week)
        user_data = self.user_data_formatter.data_format()
        age_recommendations = self.age_formatter.data_format()
        exercises_formatted = self.exercises_formatter.data_format(self.available_exercises_by_day_type)
        feedback = self.feedbaack_formatter.data_format(feedback_key)
        prev_week_formatted = self.train_week_formatter.data_format(previous_week)

        self.logger.debug(f"Week Template: \n{week_template}")
        self.logger.debug(f"User Data Formatted: \n{user_data}")
        self.logger.debug(f"Previous Week Formatted: \n{prev_week_formatted}")
        self.logger.debug(f"Feedback formatted: \n{feedback}")
        self.logger.debug(f"Age Recommendations Formatted: \n{age_recommendations}")
        self.logger.debug(f"Exercises List Formatted: \n{exercises_formatted}")

        result = chain.invoke(
            {
                "week_template": week_template,
                "user_data": user_data,
                "previous_week": prev_week_formatted,
                "feedback": feedback,
                "age_recommendations": age_recommendations,
                "available_exercises": exercises_formatted
            }
        )
        processed_result = result.content.strip()
        self.logger.info(f"Training Plan Result: \n{processed_result}")
        return processed_result

    def convert_result_to_json(self, processed_result: str) -> dict:
        if processed_result.startswith("```") and processed_result.endswith("```"):
            processed_result = "\n".join(processed_result.splitlines()[1:-1]).strip()

        try:
            return json.loads(processed_result)
        except json.JSONDecodeError as e:
            raise ValueError("Failed to decode JSON. Output received:\n" + processed_result) from e


if __name__ == "__main__":
    dotenv.load_dotenv()

    user_data_json_path = r""
    scanner_data_json_path = r""

    with open(user_data_json_path, "r", encoding="utf-8") as file:
        raw_user_data = json.load(file)
    with open(scanner_data_json_path, "r", encoding="utf-8") as file:
        raw_scanner_data = json.load(file)

    API_KEY = os.getenv("API_KEY")
    TRAIN_ASSISTANT_CONFIG_PATH = os.getenv("TRAIN_ASSISTANT_CONFIG_PATH")
    train_assistant_config = OmegaConf.load(TRAIN_ASSISTANT_CONFIG_PATH)

    DATA_PROCESSING_CONFIG_PATH = os.getenv("DATA_PROCESSING_CONFIG_PATH")
    data_processing_config = OmegaConf.load(DATA_PROCESSING_CONFIG_PATH)

    AGE_BASED_ADJUSTMENTS_CONFIG_PATH = os.getenv("AGE_BASED_ADJUSTMENTS_CONFIG_PATH")
    age_based_adjustments_config = OmegaConf.load(AGE_BASED_ADJUSTMENTS_CONFIG_PATH)

    EXERCISES_CONFIG_PATH = os.getenv("EXERCISES_CONFIG_PATH")
    exercises_config = OmegaConf.load(EXERCISES_CONFIG_PATH)

    TRAIN_WEEKS_TEMPLATES_PATH = os.getenv("TRAIN_WEEKS_TEMPLATES_PATH")
    with open(TRAIN_WEEKS_TEMPLATES_PATH, "r", encoding="utf-8") as file:
        train_weeks_templates = json.load(file)

    EXERCISES_RAW_DF_PATH = os.getenv("EXERCISES_RAW_DF_PATH")
    raw_df = pd.read_csv(EXERCISES_RAW_DF_PATH, keep_default_na=False)

    TRAINING_PROGRAM_EXAMPLES_DIR = os.getenv("TRAINING_PROGRAM_EXAMPLES_DIR")

    train_assistant = TrainAssistant(
        API_KEY=API_KEY,
        train_assistant_config=train_assistant_config,
        data_processing_config=data_processing_config,
        age_based_adjustments_config=age_based_adjustments_config,
        exercises_config=exercises_config,
        raw_user_data=raw_user_data,
        raw_scanner_data=raw_scanner_data,
        train_weeks_templates=train_weeks_templates,
        training_program_examples_dir=TRAINING_PROGRAM_EXAMPLES_DIR
    )

    print(train_assistant.generate_first_week())

