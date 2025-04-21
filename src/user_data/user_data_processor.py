import os
import json
import dotenv
from datetime import datetime, date
from omegaconf import OmegaConf, DictConfig

class UserDataProcessor:
    def __init__(self, user_data, user_data_processing_config: DictConfig):
        self.user_data = user_data
        self.user_data_processing_config = user_data_processing_config

    def get_gender(self) -> str:
        gender_key = self.user_data_processing_config["keys"]["gender_key"]
        return self.user_data[gender_key]

    def get_age(self) -> int:
        birthday_key = self.user_data_processing_config["keys"]["birthday_key"]
        birthday_str = self.user_data[birthday_key]
        birthday_date =  datetime.strptime(birthday_str, "%Y-%m-%dT%H:%M:%SZ").date()
        today = date.today()

        age = int(today.year - birthday_date.year - (
            (today.month, today.day) < (birthday_date.month, birthday_date.day)
        ))
        return age

    def get_height_cm(self) -> float:
        height_key = self.user_data_processing_config["keys"]["height_key"]
        height_type_key = self.user_data_processing_config["keys"]["height_type_key"]

        height = self.user_data[height_key]
        unit = self.user_data[height_type_key].lower()

        if unit == "cm":
            return height
        elif unit == "in":
            return height * 2.54
        elif unit == "ft":
            return height * 30.48
        elif unit == "m":
            return height * 100
        else:
            raise ValueError(f"Unrecognized height_type unit: {unit!r}")

    def get_weight_kg(self) -> float:
        weight_key = self.user_data_processing_config["keys"]["weight_key"]
        weight_type_key = self.user_data_processing_config["keys"]["weight_type_key"]

        weight = self.user_data[weight_key]
        unit = self.user_data[weight_type_key].lower()

        if unit == "kg":
            return weight
        elif unit == "lb":
            return weight * 0.45359237
        elif unit == "stone":
            return weight * 6.35029
        else:
            raise ValueError(f"Unrecognized weight_type unit: {unit!r}")

    def get_fitness_level(self) -> str:
        fitness_level_key = self.user_data_processing_config["keys"]["fitness_level_key"]
        return self.user_data[fitness_level_key]

    def get_improve_body_parts(self) -> list:
        improve_body_parts_key = self.user_data_processing_config["keys"]["improve_body_parts_key"]
        improve_body_parts = self.user_data[improve_body_parts_key]

        if len(improve_body_parts) == 0:
            improve_body_parts.append("no preferences")

        return improve_body_parts

    def get_exercise_limitations_descriptions(self) -> dict:
        exercise_limitations_key = self.user_data_processing_config["keys"]["exercise_limitations_key"]

        exercise_limitations = self.user_data[exercise_limitations_key]
        possible_exercise_limitations = self.user_data_processing_config["keys"]["possible_exercise_limitations"]
        exercise_limitations = [exercise_limitation for exercise_limitation in possible_exercise_limitations and exercise_limitations]
        exercise_limitations_descriptions = {}
        data_descriptions = self.user_data_processing_config["data_descriptions"]["exercise_limitations"]
        for exercise_limitation in exercise_limitations:
            description = data_descriptions[exercise_limitation]
            exercise_limitations_descriptions[exercise_limitation] = description

        return data_descriptions

    def get_nutrition_goal_description(self) -> dict:
        nutrition_goal_key = self.user_data_processing_config["keys"]["nutrition_goal_key"]
        nutrition_goal = self.user_data[nutrition_goal_key]
        possible_nutrition_goals = self.user_data_processing_config["keys"]["possible_nutrition_goals"]
        # TODO: add possible_nutrition_goals check

        data_descriptions = self.user_data_processing_config["data_descriptions"]["nutrition_goals"]
        description = {}
        description[nutrition_goal] = data_descriptions[nutrition_goal]
        return description

    def get_equipment_list(self) -> list:
        equipment_list_key = self.user_data_processing_config["keys"]["equipment_list_key"]
        equipment_list = self.user_data[equipment_list_key]

        equipment_list.append("none")
        return equipment_list

    def get_training_days(self) -> list:
        training_days_key = self.user_data_processing_config["keys"]["training_days_keys"]
        training_days = self.user_data
        return training_days

    def get_workout_time(self) -> int:
        workout_time_key = self.user_data_processing_config["keys"]["workout_time_key"]
        workout_time = self.user_data[workout_time_key]

        return workout_time


if __name__ == "__main__":
    dotenv.load_dotenv()

    DATA_PROCESSING_CONFIG_PATH = os.getenv("DATA_PROCESSING_CONFIG_PATH")
    data_processing_config = OmegaConf.load(DATA_PROCESSING_CONFIG_PATH)
    user_data_processing_config = data_processing_config["user_data_processing"]

    user_data_json_path = r"F:\SCULPD\SculpdAssistant\data\user_data\user_data_15-19.json"
    with open(user_data_json_path, "r", encoding="utf-8") as file:
        raw_user_data = json.load(file)

    user_data_processor = UserDataProcessor(
        user_data=raw_user_data,
        user_data_processing_config=user_data_processing_config
    )

    print(user_data_processor.get_age())
    print(user_data_processor.get_height_cm())
    print(user_data_processor.get_weight_kg())
    print(user_data_processor.get_exercise_limitations_descriptions())
    print(user_data_processor.get_nutrition_goal_description())
