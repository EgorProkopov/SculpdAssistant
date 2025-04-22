import os
import dotenv
import json
from omegaconf import OmegaConf, DictConfig


class ScannerDataFormatter:
    def __init__(self, scanner_data: dict, scanner_data_formatter_config: DictConfig):
        self.scanner_data = scanner_data
        self.scanner_data_formatter_config = scanner_data_formatter_config
        self.lines = []

    def data_format(self) -> str:
        self.lines = []
        if self.scanner_data_formatter_config["print_disclaimer"]:
            self._process_disclaimer()
        self._process_physical_attributes()
        self._process_estimated_body_fat()
        self._process_training_readiness()
        self._process_training_recommendations()
        return "\n".join(self.lines)

    def _process_disclaimer(self) -> None:
        disclaimer = self.scanner_data.get("disclaimer")
        if disclaimer:
            self.lines.append(disclaimer)
            self.lines.append("")

    def _process_physical_attributes(self) -> None:
        pa = self.scanner_data.get("physical_attributes", {})
        if not pa:
            return

        self.lines.append("Physical Attributes:")
        self._append_simple_field(pa, "body_shape", "Body shape")
        self._append_simple_field(pa, "muscle_tone", "Muscle tone")
        self._append_simple_field(pa, "muscle_symmetry", "Muscle symmetry")
        self._append_list_field(pa, "major_muscle_groups", "major_muscle_groups_indicators", "Major muscle groups")
        self._append_list_field(pa, "weak_muscle_groups", "weak_muscle_groups_indicators", "Weak muscle groups")
        self.lines.append("")

    def _process_estimated_body_fat(self) -> None:
        ebf = self.scanner_data.get("estimated_body_fat", {})
        if not ebf:
            return

        self.lines.append("Estimated Body Fat:")
        perc = ebf.get("percentage_range")
        if perc:
            self.lines.append(f"  • Percentage range: {perc}%")
        inds = ebf.get("indicators", [])
        if inds:
            self.lines.append(f"  • Indicators: {', '.join(inds)}")
        self.lines.append("")

    def _process_training_readiness(self) -> None:
        tr = self.scanner_data.get("training_readiness", {})
        if not tr:
            return

        self.lines.append("Training Readiness:")
        score = tr.get("score")
        if score is not None:
            self.lines.append(f"  • Score: {score}/10")
        inds = tr.get("indicators", [])
        if inds:
            self.lines.append(f"  • Indicators: {', '.join(inds)}")
        self.lines.append("")

    def _process_training_recommendations(self) -> None:
        rec = self.scanner_data.get("training_recommendations", {})
        if not rec:
            return

        self.lines.append("Training Recommendations:")
        for category, content in rec.items():
            section_title = category.replace("_", " ").capitalize()
            self.lines.append(f"  {section_title}:")
            if isinstance(content, dict):
                for subgroup, exercises in content.items():
                    subgroup_title = subgroup.replace("_", " ").capitalize()
                    if isinstance(exercises, dict) and "exercises" in exercises:
                        items = exercises["exercises"]
                    elif isinstance(exercises, list):
                        items = exercises
                    else:
                        self.lines.append(f"    {subgroup_title}:")
                        for part, part_exs in exercises.items():
                            part_title = part.replace("_", " ").capitalize()
                            self.lines.append(f"      {part_title}: {', '.join(part_exs) or 'no need'}")
                        continue
                    self.lines.append(f"    {subgroup_title}: {', '.join(items) or 'no need'}")
            self.lines.append("")

    def _append_simple_field(self, data: dict, key: str, label: str) -> None:
        value = data.get(key)
        if value:
            self.lines.append(f"  • {label}: {value}")

    def _append_list_field(self, data: dict, items_key: str, inds_key: str, label: str) -> None:
        items = data.get(items_key, [])
        inds  = data.get(inds_key, [])
        if items:
            text = ", ".join(items)
            if inds:
                text += f" ({'; '.join(inds)})"
            self.lines.append(f"  • {label}: {text}")


if __name__ == "__main__":
    dotenv.load_dotenv()

    DATA_PROCESSING_CONFIG_PATH = os.getenv("DATA_PROCESSING_CONFIG_PATH")
    data_processing_config = OmegaConf.load(DATA_PROCESSING_CONFIG_PATH)
    scanner_data_formatter_config = data_processing_config["scanner_data_formatter"]

    scanner_data_json_path = r"F:\SCULPD\SculpdAssistant\data\scanner_info\scanner_output_15-19.json"
    with open(scanner_data_json_path, "r", encoding="utf-8") as file:
        raw_scanner_data = json.load(file)


    scanner_data_processor = ScannerDataFormatter(
        scanner_data=raw_scanner_data, scanner_data_formatter_config=scanner_data_formatter_config
    )

    print(scanner_data_processor.data_format())

