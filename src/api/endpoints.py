from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from src.logger import get_logger
from src.training_plan.train_assistant import TrainAssistant


router = APIRouter()
logger = get_logger(__name__)


class FirstWeekRequest(BaseModel):
    user_info: dict = Field(default_factory=dict, description="User data JSON")
    scanner_info: dict = Field(default_factory=dict, description="Scanner data JSON")


class NextWeekRequest(BaseModel):
    user_info: dict = Field(default_factory=dict, description="User data JSON.")
    prev_week: dict = Field(default_factory=dict, description="Previous week training plan JSON.")
    feedback_key: str = Field(description="Feedback key ('easy', 'normal', 'hard').")


class TrainWeekResponse(BaseModel):
    plan: dict = Field(..., description="Generated week training plan")


@router.post("/generate_first_week", response_model=TrainWeekResponse)
def generate_first_week(request_data: FirstWeekRequest, request: Request):
    user_info = request_data.user_info
    scanner_info = request_data.scanner_info

    try:
        state = request.app.state
        assistant = TrainAssistant(
            API_KEY=state.api_key,
            train_assistant_config=state.train_assistant_config,
            data_processing_config=state.data_processing_config,
            age_based_adjustments_config=state.age_based_adjustments_config,
            exercises_config=state.exercises_config,
            feedback_config=state.feedback_config,
            raw_user_data=user_info,
            raw_scanner_data=scanner_info,
            train_weeks_templates=state.train_weeks_templates,
            exercises_processor=state.exercises_processor,
            training_program_examples_dir=state.training_program_examples_dir
        )
        plan = assistant.generate_first_week()
        json_plan = assistant.convert_result_to_json(plan)
        return TrainWeekResponse(plan=json_plan)
    except Exception as e:
        logger.exception("Error generating first week")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_next_week", response_model=TrainWeekResponse)
def generate_next_week(request_data: NextWeekRequest, request: Request):
    user_info = request_data.user_info
    prev_week = request_data.prev_week
    feedback_key = request_data.feedback_key

    try:
        state = request.app.state
        assistant = TrainAssistant(
            API_KEY=state.api_key,
            train_assistant_config=state.train_assistant_config,
            data_processing_config=state.data_processing_config,
            age_based_adjustments_config=state.age_based_adjustments_config,
            exercises_config=state.exercises_config,
            feedback_config=state.feedback_config,
            raw_user_data=user_info,
            raw_scanner_data=None,
            train_weeks_templates=state.train_weeks_templates,
            exercises_processor=state.exercises_processor,
            training_program_examples_dir=state.training_program_examples_dir
        )
        plan = assistant.generate_next_week(feedback_key=feedback_key, previous_week=prev_week)
        json_plan = assistant.convert_result_to_json(plan)
        return TrainWeekResponse(plan=json_plan)
    except Exception as e:
        logger.exception("Error generating next week")
        raise HTTPException(status_code=500, detail=str(e))
