import os
import dotenv
import pandas as pd
from omegaconf import OmegaConf, DictConfig

from src.exercises.exercises_processor import ExercisesProcessor


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

        matching_skills_columns = [skill.lower() for skill in skills_columns and matching_cols]
        filtered_df = df[df[matching_skills_columns].any(axis=1)]
        return filtered_df

    def get_available_exercises_by_equipment(self, df: pd.DataFrame, available_equipment: list) -> pd.DataFrame:
        equipment_columns = self.exercises_processor.get_equipment_columns()
        missing = set(available_equipment) - set(equipment_columns)
        if missing:
            raise KeyError(f"Не найдено оборудования: {missing}")

        total_required = df[equipment_columns].sum(axis=1)
        total_covered = df[available_equipment].sum(axis=1)

        mask = total_required.eq(total_covered)
        return df[mask]

    def get_available_exercises_by_day_type(self, df: pd.DataFrame, day_types: list) -> dict:
        exercises_by_day_type = {}

        day_type_to_body_parts = {
            "FULL_BODY": ["Back", "Chest", "Triceps", "Biceps", "Shoulders", "Legs", "Forearms", "Core"],
            "LOWER_BODY": ["Legs", "Core"],
            "UPPER_BODY": ["Back", "Chest", "Triceps", "Biceps", "Shoulders", "Legs", "Forearms", "Core"],
            "PUSH": ["Chest", "Triceps", "Shoulders", "Forearms", "Core"],
            "PULL": ["Back", "Biceps", "Shoulders", "Forearms", "Core"],
            "LEGS": ["Legs", "Core"]
        }

        for day_type in day_types:
            parts = day_type_to_body_parts[day_type]

            mask = df['Body Part'].isin(parts)
            filtered = df.loc[mask].reset_index(drop=True)

            exercises_by_day_type[day_type] = filtered

        return exercises_by_day_type


if __name__ == "__main__":
    dotenv.load_dotenv()

    EXERCISES_CONFIG_PATH = os.getenv("EXERCISES_CONFIG_PATH")
    exercises_config = OmegaConf.load(EXERCISES_CONFIG_PATH)
    exercises_processor_config = exercises_config["exercises_processor"]
    exercises_planner_config = exercises_config["exercises_planner"]

    raw_df = pd.read_csv(r"/data/exercises/sculpd_exercise_processed.csv")

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

