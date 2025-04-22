import os
import dotenv
from omegaconf import OmegaConf, DictConfig


class AgeBasedAdjustmentsProcessor:
    def __init__(self, age_based_adjustments_config: DictConfig):
        self.age_based_adjustments_config = age_based_adjustments_config

    def select_age_periods_adjustments(self, age) -> dict:
        age_periods_adjustments = self.age_based_adjustments_config["age_periods"]

        for age_period_key, adjustments in age_periods_adjustments.items():
            lower_age_bound = age_periods_adjustments[age_period_key]["lower_bound"]
            upper_age_bound = age_periods_adjustments[age_period_key]["upper_bound"]

            if age >= lower_age_bound and age <= upper_age_bound:
                return adjustments

        return {"wrong_age": "null"}


class AgeBasedAdjustmentsFormatter:
    def __init__(
            self,
            age_group_data: dict,
            age_based_adjustments_config: DictConfig
    ):
        self.data = age_group_data
        self.config = age_based_adjustments_config["formatter"]
        self.line = []

    def data_format(self) -> str:
        self.lines = []
        if self.config["print_age_range"]: self._process_age_range()
        if self.config["print_summary"]: self._process_summary()
        if self.config["print_training_recommendations"]: self._process_training_recommendations()
        if self.config["print_adjustments"]: self._process_adjustments()
        return "\n".join(self.lines)

    def _process_age_range(self) -> None:
        lb = self.data.get("lower_bound")
        ub = self.data.get("upper_bound")
        label = self.data.get("label", f"{lb}-{ub}")
        self.lines.append(f"Age Range: {label}")
        self.lines.append("")

    def _process_summary(self) -> None:
        summary = self.data.get("summary")
        if not summary:
            return
        self.lines.append("Summary:")
        for line in summary.strip().split("\n"):
            if line:
                self.lines.append(f"  • {line.strip()}")
        self.lines.append("")

    def _process_training_recommendations(self) -> None:
        recs = self.data.get("training_recommendations")
        if not recs:
            return
        self.lines.append("Training Recommendations:")
        for part in recs.strip().split(" - "):
            part = part.strip()
            if part:
                prefix = "•" if not part.startswith("•") else ""
                self.lines.append(f"  {prefix} {part}".strip())
        self.lines.append("")

    def _process_adjustments(self) -> None:
        adjustments = self.data.get("adjustments")
        if not adjustments:
            return
        self.lines.append("Adjustments:")
        for part in adjustments.strip().split(" - "):
            part = part.strip()
            if part:
                prefix = "•" if not part.startswith("•") else ""
                self.lines.append(f"  {prefix} {part}".strip())
        self.lines.append("")


if __name__ == "__main__":
    dotenv.load_dotenv()

    AGE_BASED_ADJUSTMENTS_CONFIG_PATH = os.getenv("AGE_BASED_ADJUSTMENTS_CONFIG_PATH")
    age_based_adjustments_config = OmegaConf.load(AGE_BASED_ADJUSTMENTS_CONFIG_PATH)

    age_based_adjustments = AgeBasedAdjustmentsProcessor(
        age_based_adjustments_config=age_based_adjustments_config
    )
    age_period = age_based_adjustments.select_age_periods_adjustments(31)

    age_based_adjustments_formatter = AgeBasedAdjustmentsFormatter(
        age_group_data=age_period,
        age_based_adjustments_config=age_based_adjustments_config
    )

    print(age_based_adjustments_formatter.data_format())

