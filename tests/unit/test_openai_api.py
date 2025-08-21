import os
import dotenv
from pathlib import Path

import pytest
from omegaconf import OmegaConf
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate


CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "train_assistant_config.yaml"


def _model_query(model: str, prompt: str) -> str:
    llm = ChatOpenAI(api_key=os.getenv("API_KEY"))
    llm.model_name = model
    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template(prompt)
    ])
    chain = prompt_template | llm
    result = chain.invoke({})
    processed_result = result.content.strip()
    return processed_result

@pytest.mark.special
def test_openai_api_respond():
    dotenv.load_dotenv()
    cfg = OmegaConf.load(CONFIG_PATH)
    model = cfg.train_assistant.first_week.model
    output = _model_query(model, "Respond with the word 'pinged'.")
    assert "pinged" in output.lower()