import json
from pathlib import Path

import pandas as pd
from omegaconf import OmegaConf
import pytest

from src.training_plan.train_assistant import TrainAssistant
from src.exercises.exercises_processor import ExercisesProcessor


class DummyResult:
    def __init__(self, content: str):
        self.content = content


class DummyChain:
    def __init__(self, content: str):
        self._content = content

    def invoke(self, _):
        return DummyResult(self._content)


@pytest.fixture
def assistant(monkeypatch):
    response_json = json.dumps({"day 1": {"day_type": "REST_DAY"}})

    def fake_init_chain(self, prompt, model_name, temperature):
        return DummyChain(response_json)

    monkeypatch.setattr(TrainAssistant, "_TrainAssistant__init_chain", fake_init_chain)

    base = Path(__file__).resolve().parents[2]

    train_assistant_cfg = OmegaConf.load(base / "configs" / "train_assistant_config.yaml")
    data_processing_cfg = OmegaConf.load(base / "configs" / "data_processing_config.yaml")
    age_cfg = OmegaConf.load(base / "configs" / "age_based_adjustments_config.yaml")
    exercises_cfg = OmegaConf.load(base / "configs" / "exercises_config.yaml")
    feedback_cfg = OmegaConf.load(base / "configs" / "feedback_config.yaml")
    train_weeks_templates = json.load(open(base / "configs" / "week_templates.json", encoding="utf-8"))

    user_data = json.load(open(base / "data" / "user_data" / "user_data_30-34.json", encoding="utf-8"))
    scanner_data = json.load(open(base / "data" / "scanner_info" / "scanner_output_30-34.json", encoding="utf-8"))
    raw_df = pd.read_csv(base / "data" / "exercises" / "sculpd_exercise_processed.csv", keep_default_na=False)
    ex_proc = ExercisesProcessor(raw_df, exercises_cfg["exercises_processor"])

    return TrainAssistant(
        API_KEY="test",
        train_assistant_config=train_assistant_cfg,
        data_processing_config=data_processing_cfg,
        age_based_adjustments_config=age_cfg,
        exercises_config=exercises_cfg,
        feedback_config=feedback_cfg,
        raw_user_data=user_data,
        raw_scanner_data=scanner_data,
        train_weeks_templates=train_weeks_templates,
        exercises_processor=ex_proc,
        eric_recommendations_path=str(base / "data" / "eric_recommendations" / "merged_recs.txt")
    )


@pytest.mark.integration
def test_generate_first_week_and_convert(assistant):
    result_str = assistant.generate_first_week()
    result = assistant.convert_result_to_json(result_str)
    assert result["day 1"]["day_type"] == "REST_DAY"


@pytest.mark.integration
def test_generate_next_week_and_convert(assistant):
    prev_week = {"day 1": {"day_type": "REST_DAY"}}
    result_str = assistant.generate_next_week("normal", prev_week)
    result = assistant.convert_result_to_json(result_str)
    assert result["day 1"]["day_type"] == "REST_DAY"