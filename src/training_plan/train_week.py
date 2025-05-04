import os
import json
import dotenv


class TrainWeek:
    def __init__(self, week_templates: dict, train_days_num: int):
        self.train_days_num = train_days_num
        self.week_templates = week_templates

        self.week = self.get_week_form(week_templates, train_days_num)
        self.day_types = self.get_day_types(train_days_num)

    def get_day_types(self, train_days_num: int) -> list:
        if train_days_num == 2 or train_days_num == 3:
            return ["FULL_BODY"]
        elif train_days_num == 4:
            return ["UPPER_BODY", "LOWER_BODY"]
        elif train_days_num == 5 or train_days_num == 5:
            return ["PUSH", "PULL", "LEGS"]
        else:
            raise

    def get_week_form(self, week_templates: dict, train_days_num: int) -> dict:
        key = f"day_{train_days_num}_template"
        week_template = week_templates[key]
        return week_template

    def get_week_formatted(self) -> str:
        week_text = str(self.week)
        week_text = week_text.replace("{", "{{")
        week_text = week_text.replace("}", "}}")
        return week_text


if __name__ == "__main__":
    dotenv.load_dotenv()

    TRAIN_WEEKS_TEMPLATES_PATH = os.getenv("TRAIN_WEEKS_TEMPLATES_PATH")
    with open(TRAIN_WEEKS_TEMPLATES_PATH, "r", encoding="utf-8") as file:
        train_weeks_templates = json.load(file)

    train_week = TrainWeek(week_templates=train_weeks_templates, train_days_num=4)
    print(train_week.week)
