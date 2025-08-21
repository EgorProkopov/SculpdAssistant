import pandas as pd
from pathlib import Path
from omegaconf import OmegaConf

from src.user_data.user_data_processor import UserDataProcessor
from src.user_data.user_data_formatter import UserDataFormatter
from src.exercises.exercises_formatter import ExercisesFormatter
from src.feedback_formatter import FeedbackFormatter
from src.previous_week_formatter import TrainingWeekFormatter
from src.scanner_data_formatter import ScannerDataFormatter


ROOT = Path(__file__).resolve().parents[2]


def user_data_formatter():
    cfg = OmegaConf.load(ROOT / "configs" / "data_processing_config.yaml")
    user_proc = UserDataProcessor(
        {
            "gender": "female",
            "age": 30,
            "height": 1.8,
            "height_type": "m",
            "weight": 70,
            "weight_type": "kg",
            "fitness_level": "beginner",
            "improve_body_parts": ["arms"],
            "exercise_limitations": [],
            "nutrition_goal": "lose_weight",
            "equipment_list": [],
            "training_days": 2,
            "workout_time": 30,
        },
        cfg["user_data_processing"],
    )
    return UserDataFormatter(user_proc, cfg["user_data_formatter"])


def exercises_formatter():
    cfg = OmegaConf.load(ROOT / "configs" / "exercises_config.yaml")
    df = pd.DataFrame({
        "Exercise Name": ["Squat"],
        "Equipment Used": ["barbell"],
        "Skill Level": ["beginner"],
        "Muscle Groups Targeted (%)": ["legs 100%"],
        "Exercise Group": ["LEGS"],
        "Body Part": ["legs"],
    })
    ex_proc = ExercisesFormatter(cfg)
    exercises_by_day = {"LEGS": df}
    return ex_proc, exercises_by_day


def test_user_data_formatter_output():
    formatter = user_data_formatter()
    text = formatter.data_format()
    assert "Gender: female" in text
    assert "Height" in text
    assert "Workout Time" in text


def test_exercises_formatter_output():
    formatter, exercises_by_day = exercises_formatter()
    text = formatter.data_format(exercises_by_day)
    assert "Exercises for DAY_TYPE='LEGS'" in text
    assert "Squat" in text


def test_feedback_formatter():
    cfg = OmegaConf.load(ROOT / "configs" / "feedback_config.yaml")
    formatter = FeedbackFormatter(cfg)
    text = formatter.data_format("easy")
    assert "workout was 'easy'" in text


def test_training_week_formatter():
    week = {
        "day 1": {
            "day_type": "UPPER_BODY",
            "exercises": {
                "Bench": {"sets": 3, "counts": 10, "set_rest_time": 90}
            },
            "rest_time": 180,
        },
        "day 2": {"day_type": "REST_DAY"},
    }
    formatter = TrainingWeekFormatter()
    text = formatter.data_format(week)
    assert "Total days: 2" in text
    assert "Rest days (1): day 2" in text


def test_scanner_data_formatter():
    cfg = OmegaConf.load(ROOT / "configs" / "data_processing_config.yaml")
    scanner_cfg = cfg["scanner_data_formatter"]
    data = {
        "disclaimer": "Should not appear",
        "physical_attributes": {"body_shape": "mesomorphic"},
        "estimated_body_fat": {"percentage_range": "10-15", "indicators": ["lean"]},
        "training_readiness": {"score": 7, "indicators": ["ok"]},
        "training_recommendations": {"body_development": {"upper_body": ["push-ups"]}},
    }
    formatter = ScannerDataFormatter(data, scanner_cfg)
    text = formatter.data_format()
    assert "Should not appear" not in text
    assert "Physical Attributes:" in text
    assert "Training Recommendations:" in text