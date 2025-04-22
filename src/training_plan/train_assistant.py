import os
import dotenv
import json
from omegaconf import OmegaConf, DictConfig

from src.training_plan.train_week import TrainWeek
from src.exercises.exercises_filter import ExercisesFilter
from src.user_data.user_data_formatter import UserDataFormatter
from src.user_data.age_based_adjustments import AgeBasedAdjustmentsProcessor, AgeBasedAdjustmentsFormatter
from src.scanner_data_formatter import ScannerDataFormatter
from src.user_data.user_data_processor import UserDataProcessor


class TrainAssistant:
    def __init__(
            self, train_week: TrainWeek,
            exercises_filter: ExercisesFilter,
            user_data_formatter: UserDataFormatter,
            age_processor: AgeBasedAdjustmentsProcessor,
            age_formatter: AgeBasedAdjustmentsFormatter,
            scanner_formatter: ScannerDataFormatter,
            train_assistant_config: DictConfig
    ):

        self.train_week = train_week
        self.exercises_filter = exercises_filter
        self.user_data_formatter = user_data_formatter
        self.age_processor = age_processor
        self.age_formatter = age_formatter
        self.scanner_formatter = scanner_formatter

        self.train_assistant_config = train_assistant_config
        self.prompt_template = self.train_assistant_config["prompt_template"]





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

    user_data_json_path = r"F:\SCULPD\SculpdAssistant\data\user_data\user_data_15-19.json"
    with open(user_data_json_path, "r", encoding="utf-8") as file:
        raw_user_data = json.load(file)

    user_data_processor = UserDataProcessor(
        user_data=raw_user_data,
        user_data_processing_config=user_data_processing_config
    )
    user_data_formatter = UserDataFormatter(
        user_data_processor=user_data_processor, user_data_formatter_config=user_data_formatter_config
    )
    train_days_number = user_data_processor.get_training_days()
    user_data = user_data_formatter.data_format()

    age_based_adjustments = AgeBasedAdjustmentsProcessor(
        age_based_adjustments_config=age_based_adjustments_config
    )
    age_period = age_based_adjustments.select_age_periods_adjustments(31)
    age_based_adjustments_formatter = AgeBasedAdjustmentsFormatter(
        age_group_data=age_period,
        age_based_adjustments_config=age_based_adjustments_config
    )
    age_recommendations = age_based_adjustments_formatter.data_format()

    scanner_data_json_path = r"F:\SCULPD\SculpdAssistant\data\scanner_info\scanner_output_15-19.json"
    with open(scanner_data_json_path, "r", encoding="utf-8") as file:
        raw_scanner_data = json.load(file)

    scanner_data_processor = ScannerDataFormatter(
        scanner_data=raw_scanner_data, scanner_data_formatter_config=scanner_data_formatter_config
    )

    scanner_recommendations = scanner_data_processor.data_format()

    with open(TRAIN_WEEKS_TEMPLATES_PATH, "r", encoding="utf-8") as file:
        train_weeks_templates = json.load(file)

    train_week = TrainWeek(week_templates=train_weeks_templates, train_days_num=4)
