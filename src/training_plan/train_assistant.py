import os
from pathlib import Path

import json
import logging
from omegaconf import DictConfig

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
            training_program_examples_dir: str | None = None,
            eric_recommendations_path: str | None = None
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

        self.merged_recs = ""
        if eric_recommendations_path and os.path.isfile(eric_recommendations_path):
            with open(eric_recommendations_path, "r", encoding="utf-8") as file:
                self.merged_recs = file.read().strip()

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
        root_dir = Path(__file__).resolve().parent.parent
        custom_prompt_path = root_dir / r"data/prompt_rules/first_week/prompt_placeholder.txt"
        custom_prompt = custom_prompt_path.read_text()
        return self.generate_first_week_with_custom_prompt(custom_prompt)

    def generate_first_week_with_custom_prompt(self, custom_prompt: str) -> str:
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
        merged_recs = self.merged_recs

        self.logger.debug(f"Week Template: \n{week_template}")
        self.logger.debug(f"User Data Formatted: \n{user_data}")
        self.logger.debug(f"Scanner Recommendations Formatted: \n{scanner_recommendations}")
        # self.logger.debug(f"Age Recommendations Formatted: \n{age_recommendations}")
        self.logger.debug(f"Exercises List Formatted: \n{exercises_formatted}")
        self.logger.debug(f"Custom Prompt: \n {custom_prompt}")

        result = chain.invoke(
            {
                "week_template": week_template,
                "user_data": user_data,
                "scanner_recommendations": scanner_recommendations,
                "age_recommendations": age_recommendations,
                "available_exercises": exercises_formatted,
                "avatars_examples": avatar_examples,
                "merged_recs": merged_recs,
                "custom_rules": custom_prompt
            }
        )
        processed_result = result.content.strip()
        self.logger.info(f"Training Plan Result: \n{processed_result}")
        return processed_result

    def generate_next_week(self, feedback_key: str, previous_week: dict) -> str:
        root_dir = Path(__file__).resolve().parent.parent
        custom_prompt_path = root_dir / r"data/prompt_rules/nextt_week/prompt_placeholder.txt"
        custom_prompt = custom_prompt_path.read_text()
        return self.generate_next_week_with_prompt(custom_prompt, feedback_key, previous_week)

    def generate_next_week_with_prompt(self, custom_prompt: str, feedback_key: str, previous_week: dict) -> str:
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
        avatar_examples = self.avatar_examples
        merged_recs = self.merged_recs

        self.logger.debug(f"Week Template: \n{week_template}")
        self.logger.debug(f"User Data Formatted: \n{user_data}")
        self.logger.debug(f"Previous Week Formatted: \n{prev_week_formatted}")
        self.logger.debug(f"Feedback formatted: \n{feedback}")
        self.logger.debug(f"Age Recommendations Formatted: \n{age_recommendations}")
        self.logger.debug(f"Exercises List Formatted: \n{exercises_formatted}")
        self.logger.debug(f"Custom Prompt: \n {custom_prompt}")

        result = chain.invoke(
            {
                "week_template": week_template,
                "user_data": user_data,
                "previous_week": prev_week_formatted,
                "feedback": feedback,
                "age_recommendations": age_recommendations,
                "available_exercises": exercises_formatted,
                "avatars_examples": avatar_examples,
                "merged_recs": merged_recs,
                "custom_rules": custom_prompt
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

