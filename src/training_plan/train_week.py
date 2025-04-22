import os
import json
import dotenv

from omegaconf import OmegaConf, DictConfig


class TrainWeek:
    def __init__(self, train_days: list):
        self.train_days = train_days
        self.week = self.get_week_form()

    def get_week_form(self) -> dict:
        week = {}
        for day_num in range(1, 8):
            day_name = f"day {day_num}"
            if day_num in self.train_days:
                week[day_name] = {"restday": False, "exercises": {}, "notes": {}, "explanations": {}}
            else:
                week[day_name] = {"restday": True}
        return week


if __name__ == "__main__":
    train_week = TrainWeek(train_days=[1, 3, 5, 7])
    print(train_week.week)
