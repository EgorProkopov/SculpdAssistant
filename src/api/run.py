import os
import json
import dotenv
import pandas as pd
from omegaconf import OmegaConf

import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.endpoints import router
from src.exercises.exercises_processor import ExercisesProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    dotenv.load_dotenv()

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY is not set in environment variables")
    app.state.api_key = api_key

    app.state.train_assistant_config = OmegaConf.load(os.getenv("TRAIN_ASSISTANT_CONFIG_PATH"))
    app.state.data_processing_config = OmegaConf.load(os.getenv("DATA_PROCESSING_CONFIG_PATH"))
    app.state.age_based_adjustments_config = OmegaConf.load(os.getenv("AGE_BASED_ADJUSTMENTS_CONFIG_PATH"))
    app.state.exercises_config = OmegaConf.load(os.getenv("EXERCISES_CONFIG_PATH"))
    app.state.feedback_config = OmegaConf.load(os.getenv("FEEDBACK_CONFIG_PATH"))
    app.state.train_weeks_templates = json.load(
        open(os.getenv("TRAIN_WEEKS_TEMPLATES_PATH"), encoding="utf-8")
    )
    app.state.training_program_examples_dir = os.getenv("TRAINING_PROGRAM_EXAMPLES_DIR")

    raw_df = pd.read_csv(os.getenv("EXERCISES_RAW_DF_PATH"), keep_default_na=False)
    ex_cfg = app.state.exercises_config["exercises_processor"]
    app.state.exercises_processor = ExercisesProcessor(raw_df, ex_cfg)

    yield

app = FastAPI(title="SCULPD Train Assistant API", lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    api_config = OmegaConf.load(os.getenv("API_CONFIG_PATH"))
    uvicorn.run("src.api.run:app", host="0.0.0.0", port=int(os.getenv("PORT", api_config["port"])), reload=True)
