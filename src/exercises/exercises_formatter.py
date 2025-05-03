import os
import dotenv
import pandas as pd
from omegaconf import OmegaConf, DictConfig

from src.exercises.exercises_filter import ExercisesFilter
from src.exercises.exercises_processor import ExercisesProcessor


class ExercisesFormatter:
    def __init__(self, exercises_config: DictConfig):
        self.exercises_config = exercises_config

    def data_format(self, exercises_by_day_type: dict) -> str:
        lines = []
        for day_type, exercises_df in exercises_by_day_type.items():
            columns = []

            if self.exercises_config["exercises_formatter"]["print_exercises_names"]:
                columns.append(self.exercises_config["exercises_processor"]["keys"]["exercise_names_key"])
            if self.exercises_config["exercises_formatter"]["print_exercises_group"]:
                columns.append(self.exercises_config["exercises_processor"]["keys"]["exercise_groups_key"])
            if self.exercises_config["exercises_formatter"]["print_body_part"]:
                columns.append(self.exercises_config["exercises_processor"]["keys"]["body_parts_key"])
            if self.exercises_config["exercises_formatter"]["print_muscle_groups_targeted"]:
                columns.append(self.exercises_config["exercises_processor"]["keys"]["muscles_key"])

            preprint_exercises_df = exercises_df[columns]

            header = f"Exercises for DAY_TYPE='{day_type}':\n" + " | ".join(columns)

            lines.append(header)
            for _, row in preprint_exercises_df.iterrows():
                line = " | ".join(str(row[col]) for col in columns)
                lines.append(line)

            lines.append("\n")

        text = "\n".join(lines)
        return text


if __name__ == "__main__":
    dotenv.load_dotenv()

    EXERCISES_CONFIG_PATH = os.getenv("EXERCISES_CONFIG_PATH")
    exercises_config = OmegaConf.load(EXERCISES_CONFIG_PATH)
    exercises_processor_config = exercises_config["exercises_processor"]
    exercises_planner_config = exercises_config["exercises_planner"]

    raw_df = pd.read_csv(r"")

    exercises_processor = ExercisesProcessor(
        raw_exercises_df=raw_df, exercises_processor_config=exercises_processor_config
    )

    exercises_filter = ExercisesFilter(
        exercises_processor=exercises_processor, exercises_planner_config=exercises_planner_config
    )

    skill_level="intermediate"
    available_equipment = ["cable_machine", "platform", "barbell", "ez_bar"]
    day_types = ["PUSH", "PULL", "LEGS"]

    processed_df = exercises_processor.processed_df
    available_exercises = exercises_filter.get_available_exercises_by_skill_level(
        df=processed_df, skill_level=skill_level
    )
    available_exercises = exercises_filter.get_available_exercises_by_equipment(
        df=available_exercises, available_equipment=available_equipment
    )
    available_exercises_by_day_type = exercises_filter.get_available_exercises_by_day_type(
        df=available_exercises, day_types=day_types
    )

    exercises_formatter = ExercisesFormatter(exercises_config)

    formatted_exercises = exercises_formatter.data_format(available_exercises_by_day_type)
    print(formatted_exercises)


