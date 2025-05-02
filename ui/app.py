import os
import json
import dotenv
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from omegaconf import OmegaConf
import pandas as pd
from typing import Any, AsyncGenerator
from contextlib import asynccontextmanager

# Import your modules
from src.exercises.exercises_processor import ExercisesProcessor
from src.training_plan.train_assistant import TrainAssistant

USER_PROFILE_URL = "http://89.104.65.131/user/get-profile"

# Lifespan handler to replace deprecated startup event
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Load environment
    dotenv.load_dotenv()

    # API key
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY is not set in environment variables")
    app.state.api_key = api_key  # type: ignore

    # Load configs
    app.state.train_assistant_config = OmegaConf.load(os.getenv("TRAIN_ASSISTANT_CONFIG_PATH"))  # type: ignore
    app.state.data_processing_config = OmegaConf.load(os.getenv("DATA_PROCESSING_CONFIG_PATH"))  # type: ignore
    app.state.age_based_adjustments_config = OmegaConf.load(os.getenv("AGE_BASED_ADJUSTMENTS_CONFIG_PATH"))  # type: ignore
    app.state.exercises_config = OmegaConf.load(os.getenv("EXERCISES_CONFIG_PATH"))  # type: ignore
    app.state.feedback_config = OmegaConf.load(os.getenv("FEEDBACK_CONFIG_PATH"))  # type: ignore
    app.state.train_weeks_templates = json.load(
        open(os.getenv("TRAIN_WEEKS_TEMPLATES_PATH"), encoding="utf-8")  # type: ignore
    )

    # Prepare exercises processor
    raw_df = pd.read_csv(os.getenv("EXERCISES_RAW_DF_PATH"), keep_default_na=False)
    ex_cfg = app.state.exercises_config["exercises_processor"]  # type: ignore
    app.state.exercises_processor = ExercisesProcessor(raw_df, ex_cfg)  # type: ignore

    yield
    # (Optional) teardown logic here

# Initialize FastAPI with lifespan handler
app = FastAPI(title="SCULPD Train Assistant API", lifespan=lifespan)

# Pydantic model for request containing only scanner_info
class TrainingPlanRequest(BaseModel):
    scanner_info: dict = Field(default_factory=dict, description="Optional scanner data JSON")

class TrainingPlanResponse(BaseModel):
    plan: dict = Field(..., description="Generated training plan structure")

@app.post("/generate_training_plan", response_model=TrainingPlanResponse)
def generate_training_plan(request_data: TrainingPlanRequest, request: Request):
    """
    Generate a personalized training plan for the user.
    Fetches user profile automatically, uses provided scanner_info.
    """
    # Fetch user info from external service
    resp = requests.get(USER_PROFILE_URL)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch user profile: {resp.status_code}")
    user_info = resp.json()

    try:
        state: Any = request.app.state  # type: ignore
        assistant = TrainAssistant(
            API_KEY=state.api_key,
            train_assistant_config=state.train_assistant_config,
            data_processing_config=state.data_processing_config,
            age_based_adjustments_config=state.age_based_adjustments_config,
            exercises_config=state.exercises_config,
            feedback_config=state.feedback_config,
            raw_user_data=user_info,
            raw_scanner_data=request_data.scanner_info,
            train_weeks_templates=state.train_weeks_templates,
            exercises_processor=state.exercises_processor
        )
        plan = assistant.generate_first_week()
        return TrainingPlanResponse(plan=plan)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))