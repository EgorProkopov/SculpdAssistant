import os
import dotenv
import json
from omegaconf import OmegaConf, DictConfig


class FeedbackFormatter:
    def __init__(self, feedback_config: DictConfig):
        self.feedback_config = feedback_config

    def data_format(self, feedback_key) -> str:
        feedback_description = self.feedback_config["feedback_descriptions"][feedback_key]
        return feedback_description


if __name__ == "__main__":
    dotenv.load_dotenv()
    FEEDBACK_CONFIG_PATH = os.getenv("FEEDBACK_CONFIG_PATH")
    feedback_config = OmegaConf.load(FEEDBACK_CONFIG_PATH)

    feedback_formatter = FeedbackFormatter(feedback_config=feedback_config)

    feedback_key = 'hard'
    print(feedback_formatter.data_format(feedback_key))