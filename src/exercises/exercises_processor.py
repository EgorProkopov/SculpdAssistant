import os
import re
import dotenv
import pandas as pd
from omegaconf import OmegaConf, DictConfig

class ExercisesProcessor:
    def __init__(self, raw_exercises_df: pd.DataFrame, exercises_processor_config: DictConfig):
        self.raw_exercises_df = raw_exercises_df
        self.exercises_processor_config = exercises_processor_config

        keys = exercises_processor_config['keys']

        self.muscles_df = self.process_muscle_groups(keys['muscles_key'])
        self.equipment_df = self.process_equipment(keys['equipments_key'])
        self.skills_df = self.process_skill_level(keys['skill_levels_key'])

        self.processed_df = self.merge_df(
            keys['exercise_names_key'], keys['exercise_groups_key'], keys['body_parts_key'], keys['muscles_key']
        )

    @staticmethod
    def __parse_muscle(s):
        d = {}
        for item in s.split(', '):
            m = re.match(r'(.+?)\s+(\d+)%', item, flags=re.IGNORECASE)
            if m:
                muscle, pct = m.groups()
                d[muscle] = int(pct)
        return d

    def get_muscules_columns(self) -> list:
        return self.muscles_df.columns.tolist()

    def get_equipment_columns(self) -> list:
        return self.equipment_df.columns.tolist()

    def get_skills_columns(self) -> list:
        return self.skills_df.columns.tolist()

    def process_muscle_groups(self, muscles_key: str) -> pd.DataFrame:
        """
        Args:
            muscles_key: Expected 'Muscle Groups Targeted (%)'

        Returns:
            Encoded muscles DataFrame
        """
        muscle_parsed = self.raw_exercises_df[muscles_key].apply(self.__parse_muscle)
        muscles_df = pd.json_normalize(muscle_parsed).fillna(0).astype(int)

        muscles_df.columns = (
            muscles_df.columns
                .str.strip()
                .str.lower()
        )

        return muscles_df

    def process_equipment(self, equipments_key: str) -> pd.DataFrame:
        """
        Args:
            equipments_key: Expected 'Equipment Used'

        Returns:
            Encoded equipment DataFrame
        """
        equipment_df = self.raw_exercises_df[equipments_key]
        equipment_df = equipment_df.str.get_dummies(sep=', ')

        equipment_df.columns = (
            equipment_df.columns
                .str.strip()
                .str.lower()
        )

        return equipment_df

    def process_skill_level(self, skill_levels_key) -> pd.DataFrame:
        """
        Args:
            levels_key: Expected 'Skill Level'

        Returns:
            Encoded levels DataFrame
        """
        skill_df = self.raw_exercises_df[skill_levels_key]
        skill_df = skill_df.str.get_dummies()

        skill_df.columns = (
            skill_df.columns
            .str.strip()
            .str.lower()
        )

        return skill_df

    def merge_df(self, exercise_names_key: str, exercise_groups_key: str, body_parts_key: str, muscle_key: str) -> pd.DataFrame:
        exercises_name_df = self.raw_exercises_df[exercise_names_key]
        exercises_group_df = self.raw_exercises_df[exercise_groups_key]
        exercises_body_pard_df = self.raw_exercises_df[body_parts_key]
        muscle_goups_text_df = self.raw_exercises_df[muscle_key]

        merged_df = pd.concat([exercises_name_df, exercises_group_df, exercises_body_pard_df, self.skills_df, self.equipment_df, self.muscles_df, muscle_goups_text_df], axis=1)

        return merged_df


if __name__ == "__main__":
    dotenv.load_dotenv()

    EXERCISES_CONFIG_PATH = os.getenv("EXERCISES_CONFIG_PATH")
    exercises_config = OmegaConf.load(EXERCISES_CONFIG_PATH)
    exercises_processor_config = exercises_config["exercises_processor"]

    raw_df = pd.read_csv(r"/data/exercises/sculpd_exercise_processed.csv")

    exercises_processor = ExercisesProcessor(
        raw_exercises_df=raw_df, exercises_processor_config=exercises_processor_config
    )
    print(exercises_processor.processed_df.columns.tolist())
