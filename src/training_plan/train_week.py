import os
import json
import pandas as pd
import dotenv
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI

from omegaconf import OmegaConf, DictConfig

from src.user_data.user_data_processor import UserDataProcessor
from src.user_data.user_data_formatter import UserDataFormatter
from src.user_data.age_based_adjustments import AgeBasedAdjustmentsProcessor, AgeBasedAdjustmentsFormatter
from src.scanner_data_formatter import ScannerDataFormatter


class TrainWeek:
    def __init__(self, week_templates: dict, train_days_num: int):
        self.train_days_num = train_days_num
        self.week_templates = week_templates

        self.week = self.get_week_form()

    def get_week_form(self) -> dict:
        key = f"day_{self.train_days_num}_template"
        week_template = self.week_templates[key]
        return week_template


if __name__ == "__main__":
    dotenv.load_dotenv()

    TRAIN_WEEKS_TEMPLATES_PATH = os.getenv("TRAIN_WEEKS_TEMPLATES_PATH")
    with open(TRAIN_WEEKS_TEMPLATES_PATH, "r", encoding="utf-8") as file:
        train_weeks_templates = json.load(file)

    train_week = TrainWeek(week_templates=train_weeks_templates, train_days_num=4)
    print(train_week.week)
