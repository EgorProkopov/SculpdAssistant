import os
import json
from typing import Optional

import pandas as pd
from omegaconf import OmegaConf

from src.exercises.exercises_processor import ExercisesProcessor
from src.training_plan.train_assistant import TrainAssistant


def create_train_assistant(raw_user_data: dict, raw_scanner_data: Optional[dict] = None) -> TrainAssistant:
    API_KEY = os.getenv("API_KEY")

    train_assistant_config = OmegaConf.load(os.getenv("TRAIN_ASSISTANT_CONFIG_PATH"))
    data_processing_config = OmegaConf.load(os.getenv("DATA_PROCESSING_CONFIG_PATH"))
    age_based_adjustments_config = OmegaConf.load(os.getenv("AGE_BASED_ADJUSTMENTS_CONFIG_PATH"))

    exercises_config = OmegaConf.load(os.getenv("EXERCISES_CONFIG_PATH"))
    exercises_processor_config = exercises_config["exercises_processor"]

    feedback_config = OmegaConf.load(os.getenv("FEEDBACK_CONFIG_PATH"))

    train_weeks_templates = json.load(open(os.getenv("TRAIN_WEEKS_TEMPLATES_PATH"), "r", encoding="utf-8"))

    raw_df = pd.read_csv(os.getenv("EXERCISES_RAW_DF_PATH"), keep_default_na=False)
    exercises_processor = ExercisesProcessor(raw_df, exercises_processor_config)

    return TrainAssistant(
        API_KEY=API_KEY,
        train_assistant_config=train_assistant_config,
        data_processing_config=data_processing_config,
        age_based_adjustments_config=age_based_adjustments_config,
        exercises_config=exercises_config,
        feedback_config=feedback_config,
        raw_user_data=raw_user_data,
        raw_scanner_data=raw_scanner_data,
        train_weeks_templates=train_weeks_templates,
        exercises_processor=exercises_processor,
        training_program_examples_dir=os.getenv("TRAINING_PROGRAM_EXAMPLES_DIR"),
    )
