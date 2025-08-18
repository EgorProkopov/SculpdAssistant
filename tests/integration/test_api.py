import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import endpoints


class DummyTrainAssistant:
    def __init__(self, *args, **kwargs):
        pass

    def generate_first_week(self):
        return json.dumps({"plan": "ok"})

    def generate_next_week(self, feedback_key, previous_week):
        return json.dumps({"plan": f"next-{feedback_key}"})

    def convert_result_to_json(self, plan_str):
        return json.loads(plan_str)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(endpoints, "TrainAssistant", DummyTrainAssistant)

    app = FastAPI()
    app.include_router(endpoints.router)

    app.state.api_key = "test"
    app.state.train_assistant_config = {}
    app.state.data_processing_config = {}
    app.state.age_based_adjustments_config = {}
    app.state.exercises_config = {}
    app.state.feedback_config = {}
    app.state.train_weeks_templates = {}
    app.state.exercises_processor = object()
    app.state.training_program_examples_dir = None
    app.state.eric_recommendations_path = None

    return TestClient(app)


@pytest.mark.integration
def test_ping_endpoint(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Successful ping"}


@pytest.mark.integration
def test_generate_first_week_endpoint(client):
    payload = {"user_info": {}, "scanner_info": {}}
    resp = client.post("/generate_first_week", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"plan": {"plan": "ok"}}


@pytest.mark.integration
def test_generate_next_week_endpoint(client):
    payload = {"user_info": {}, "prev_week": {}, "feedback_key": "easy"}
    resp = client.post("/generate_next_week", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"plan": {"plan": "next-easy"}}