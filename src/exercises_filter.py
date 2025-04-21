import os
import re
import dotenv
import pandas as pd
from omegaconf import OmegaConf, DictConfig

from src.exercises_processor import ExercisesProcessor


class ExercisesFilter:
    def __init__(self, exercises_processor: ExercisesProcessor, exercises_planner_config: DictConfig):
        self.exercises_processor = exercises_processor
        self.exercises_planner_config = exercises_planner_config

    def get_available_exercises_by_skill_level(self, df: pd.DataFrame, skill_level: str) -> pd.DataFrame:
        skills_columns = self.exercises_processor.get_skills_columns()
        current_skill_grade = self.exercises_planner_config['skills'][skill_level]

        matching_cols = []
        for skill, skill_grade in self.exercises_planner_config['skills'].items():
            if skill_grade <= current_skill_grade:
                matching_cols.append(skill)

        matching_skills_columns = [skill for skill in skills_columns and matching_cols]
        print(matching_skills_columns)
        filtered_df = df[df[matching_skills_columns].any(axis=1)]
        return filtered_df

    def get_available_exercises_by_equipment(self, df: pd.DataFrame, available_equipment: list) -> pd.DataFrame:
        equipment_columns = self.exercises_processor.get_equipment_columns()

        matching_cols = [
            col for col in equipment_columns
            if any(available in col for available in available_equipment)
        ]

        filtered_df = df[df[matching_cols].any(axis=1)]
        return filtered_df


if __name__ == "__main__":
    dotenv.load_dotenv()

    EXERCISES_CONFIG_PATH = os.getenv("EXERCISES_CONFIG_PATH")
    exercises_config = OmegaConf.load(EXERCISES_CONFIG_PATH)
    exercises_processor_config = exercises_config["exercises_processor"]
    exercises_planner_config = exercises_config["exercises_planner"]

    raw_df = pd.read_csv(r"F:\SCULPD\SculpdAssistant\data\exercises\sculpd_exercise_processed.csv")

    exercises_processor = ExercisesProcessor(
        raw_exercises_df=raw_df, exercises_processor_config=exercises_processor_config
    )

    exercises_filter = ExercisesFilter(
        exercises_processor=exercises_processor, exercises_planner_config=exercises_planner_config
    )

    skill_level="Beginner"
    available_equipment = ['Barbell']

    processed_df = exercises_processor.processed_df
    available_exercises = exercises_filter.get_available_exercises_by_skill_level(
        df=processed_df, skill_level=skill_level
    )
    print(len(available_exercises))
    print(available_exercises.columns.tolist())

    available_exercises = exercises_filter.get_available_exercises_by_equipment(
        df=available_exercises, available_equipment=available_equipment
    )
    print(len(available_exercises))
    print(available_exercises.columns.tolist())

