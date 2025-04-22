import os
import dotenv
import json
from omegaconf import OmegaConf, DictConfig

from src.training_plan.train_week import TrainWeek
from src.exercises.exercises_filter import ExercisesFilter
from src.user_data.user_data_formatter import UserDataFormatter
from src.user_data.age_based_adjustments import AgeBasedAdjustmentsProcessor, AgeBasedAdjustmentsFormatter
from src.scanner_data_formatter import ScannerDataFormatter

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


