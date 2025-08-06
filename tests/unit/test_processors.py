import pandas as pd
from pathlib import Path
from omegaconf import OmegaConf

from src.user_data.user_data_processor import UserDataProcessor
from src.exercises.exercises_processor import ExercisesProcessor


ROOT = Path(__file__).resolve().parents[2]


def build_user_processor():
    cfg = OmegaConf.load(ROOT / "configs" / "data_processing_config.yaml")
    user_cfg = cfg["user_data_processing"]
    user_data = {
        "gender": "male",
        "age": 25,
        "height": 72,
        "height_type": "in",
        "weight": 180,
        "weight_type": "lb",
        "fitness_level": "beginner",
        "improve_body_parts": [],
        "exercise_limitations": ["no_squatting", "unknown"],
        "nutrition_goal": "gain_weight",
        "equipment_list": ["barbell"],
        "training_days": 3,
        "workout_time": 45,
    }
    return UserDataProcessor(user_data, user_cfg)


def build_exercises_processor():
    cfg = OmegaConf.load(ROOT / "configs" / "exercises_config.yaml")
    ex_cfg = cfg["exercises_processor"]
    df = pd.DataFrame({
        "Exercise Name": ["Push Up"],
        "Equipment Used": ["bodyweight"],
        "Skill Level": ["beginner"],
        "Muscle Groups Targeted (%)": ["chest 100%"],
        "Exercise Group": ["PUSH"],
        "Body Part": ["chest"],
    })
    return ExercisesProcessor(df, ex_cfg)


def test_user_data_processor_conversions():
    proc = build_user_processor()
    assert proc.get_height_cm() == 72 * 2.54
    assert proc.get_weight_kg() == 180 * 0.45359237
    assert proc.get_improve_body_parts() == ["no preferences"]
    limitations = proc.get_exercise_limitations_descriptions()
    assert "no_squatting" in limitations and "unknown" not in limitations
    nutrition = proc.get_nutrition_goal_description()
    assert "gain_weight" in nutrition
    equipment = proc.get_equipment_list()
    assert equipment[-1] == "none"
    assert proc.get_training_days() == 3
    assert proc.get_workout_time() == 45


def test_exercises_processor_columns():
    proc = build_exercises_processor()
    assert proc.processed_df.shape[0] == 1
    assert "bodyweight" in proc.get_equipment_columns()
    assert "beginner" in proc.get_skills_columns()