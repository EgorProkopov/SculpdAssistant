import os
import dotenv
import json
from omegaconf import OmegaConf, DictConfig

from src.user_data.user_data_processor import UserDataProcessor


class UserDataFormatter:
    def __init__(self, user_data_processor: UserDataProcessor, user_data_formatter_config: DictConfig):
        self.user_data_processor = user_data_processor
        self.user_data_formatter_config = user_data_formatter_config

        self.lines = []

    def data_format(self) -> str:
        self.lines = []
        if self.user_data_formatter_config["print_gender"]: self._process_gender()
        if self.user_data_formatter_config["print_age"]: self._process_age()
        if self.user_data_formatter_config["print_height"]: self._process_height()
        if self.user_data_formatter_config["print_weight"]: self._process_weight()
        if self.user_data_formatter_config["print_fitness_level"]: self._process_fitness_level()
        if self.user_data_formatter_config["print_improve_body_parts"]: self._process_improve_body_parts()
        if self.user_data_formatter_config["print_exercise_limitations"]: self._process_exercise_limitations()
        if self.user_data_formatter_config["print_nutrition_goal"]: self._process_nutrition_goal()
        if self.user_data_formatter_config["print_equipment_list"]: self._process_equipment_list()
        if self.user_data_formatter_config["print_training_days"]: self._process_training_days()
        if self.user_data_formatter_config["print_workout_time"]: self._process_workout_time()
        return "\n".join(self.lines)

    def _process_gender(self) -> None:
        label = "Gender"
        value = self.user_data_processor.get_gender()
        self.lines.append(f"{label}: {value}")

    def _process_age(self) -> None:
        label = "Age"
        value = self.user_data_processor.get_age()
        self.lines.append(f"{label}: {value} years")

    def _process_height(self) -> None:
        label = "Height (cm)"
        value = self.user_data_processor.get_height_cm()
        self.lines.append(f"{label}: {value:.1f}")

    def _process_weight(self) -> None:
        label = "Weight (kg)"
        value = self.user_data_processor.get_weight_kg()
        self.lines.append(f"{label}: {value:.1f}")

    def _process_fitness_level(self) -> None:
        label = "Fitness Level"
        value = self.user_data_processor.get_fitness_level()
        self.lines.append(f"{label}: {value}")

    def _process_improve_body_parts(self) -> None:
        label = "Target Body Parts"
        parts = self.user_data_processor.get_improve_body_parts()
        self.lines.append(f"{label}: {', '.join(parts)}")

    def _process_exercise_limitations(self) -> None:
        label = "Exercise Limitations"
        limitations = self.user_data_processor.get_exercise_limitations_descriptions()
        if limitations:
            self.lines.append(f"{label}:")
            for key, desc in limitations.items():
                self.lines.append(f"  • {key}: {desc}")
        else:
            self.lines.append(f"{label}: none")

    def _process_nutrition_goal(self) -> None:
        label = "Nutrition Goal"
        descriptions = self.user_data_processor.get_nutrition_goal_description()
        for goal, desc in descriptions.items():
            self.lines.append(f"{label}: {goal} – {desc}")

    def _process_equipment_list(self) -> None:
        label = "Available Equipment"
        equipment = self.user_data_processor.get_equipment_list()
        self.lines.append(f"{label}: {', '.join(equipment)}")

    def _process_training_days(self) -> None:
        label = f"Training Days"
        days_num = self.user_data_processor.get_training_days()
        # days= self.user_data_processor.get_training_days()
        # days_str = ", ".join(str(d) for d in days)
        self.lines.append(f"{label}: {days_num}")

    def _process_workout_time(self) -> None:
        label = "Workout Time (min)"
        minutes = self.user_data_processor.get_workout_time()
        self.lines.append(f"{label}: {minutes} minutes")


if __name__ == "__main__":
    dotenv.load_dotenv()

    DATA_PROCESSING_CONFIG_PATH = os.getenv("DATA_PROCESSING_CONFIG_PATH")
    data_processing_config = OmegaConf.load(DATA_PROCESSING_CONFIG_PATH)
    user_data_processing_config = data_processing_config["user_data_processing"]
    user_data_formatter_config = data_processing_config["user_data_formatter"]

    user_data_json_path = r""
    with open(user_data_json_path, "r", encoding="utf-8") as file:
        raw_user_data = json.load(file)

    user_data_processor = UserDataProcessor(
        user_data=raw_user_data,
        user_data_processing_config=user_data_processing_config
    )

    user_data_formatter = UserDataFormatter(
        user_data_processor=user_data_processor, user_data_formatter_config=user_data_formatter_config
    )
    print(user_data_formatter.data_format())