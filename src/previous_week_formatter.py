class TrainingWeekFormatter:
    def data_format(self, week_json: dict) -> str:
        total_days = len(week_json)
        rest_days = []
        workout_days = []
        per_day_lines = []

        for day_name, info in week_json.items():
            day_type = info.get('day_type', '')
            if day_type == 'REST_DAY':
                rest_days.append(day_name)
            else:
                workout_days.append(day_name)
                exercises = info.get('exercises', {})
                total_sets = sum(ex['sets'] for ex in exercises.values())
                total_reps = sum(ex['sets'] * ex['counts'] for ex in exercises.values())
                avg_set_rest = (
                    sum(ex['set_rest_time'] for ex in exercises.values()) / len(exercises)
                ) if exercises else 0
                rest_between = info.get('rest_time')
                notes = info.get('notes', '')

                per_day_lines.append(f"{day_name} ({day_type}):")
                per_day_lines.append(f"  Exercises: {len(exercises)}")
                per_day_lines.append(f"  Total sets: {total_sets}")
                per_day_lines.append(f"  Total reps: {total_reps}")
                per_day_lines.append(f"  Avg rest between sets: {avg_set_rest:.1f}s")
                per_day_lines.append(f"  Rest between exercises: {rest_between}s")
                if notes:
                    per_day_lines.append(f"  Notes: {notes}")
                per_day_lines.append("")

        lines = [
            f"Total days: {total_days}",
            f"Rest days ({len(rest_days)}): {', '.join(rest_days)}",
            f"Workout days ({len(workout_days)}): {', '.join(workout_days)}",
            ""
        ]
        lines.extend(per_day_lines)
        return "\n".join(lines)


if __name__ == '__main__':
    week_data =  {
            "day 1": {
                "day_type": "UPPER_BODY",
                "exercises": {
                    "Bench Press": {"sets": 4, "counts": 10, "set_rest_time": 90},
                    "Lat Pulldown": {"sets": 4, "counts": 12, "set_rest_time": 90},
                    "Unilateral Cable Lateral Raises": {"sets": 3, "counts": 15, "set_rest_time": 60},
                    "Preacher Curls": {"sets": 3, "counts": 15, "set_rest_time": 60},
                    "Single Arm Cross Body Extension": {"sets": 3, "counts": 15, "set_rest_time": 60}
                },
                "notes": "Focus on controlled tempo: use a 3-1-1-0 pace for each rep.",
                "explanations": "Bench Press targets the chest effectively and aligns with user's chest focus. Lat Pulldown strengthens back and biceps, supporting balanced upper body development. Unilateral Cable Lateral Raises engage shoulders without overhead pressing, respecting user's limitations. Preacher Curls enhance bicep definition. Single Arm Cross Body Extension focuses on triceps. Exercises are chosen for muscle balance and hypertrophy.",
                "rest_time": 240
            },
            "day 2": {
                "day_type": "LOWER_BODY",
                "exercises": {
                    "Glute Kickback": {"sets": 4, "counts": 12, "set_rest_time": 75},
                    "Plank": {"sets": 3, "counts": 60, "set_rest_time": 60},
                    "Bicycle Crunch": {"sets": 3, "counts": 20, "set_rest_time": 60},
                    "Cable Woodchopper": {"sets": 3, "counts": 15, "set_rest_time": 60}
                },
                "notes": "Focus on core stability during Plank and Cable Woodchopper.",
                "explanations": "Glute Kickback emphasizes lower body strength and hypertrophy, especially in glutes. Plank and Bicycle Crunches focus on core, aligning with user's target of abs. Cable Woodchopper adds rotational core work, enhancing functional strength.",
                "rest_time": 240
            },
            "day 3": {
                "day_type": "REST_DAY"
            },
            "day 4": {
                "day_type": "UPPER_BODY",
                "exercises": {
                    "Incline Bench Press": {"sets": 4, "counts": 10, "set_rest_time": 90},
                    "V-Grip Pulldown": {"sets": 4, "counts": 12, "set_rest_time": 90},
                    "Kneeling Single Arm Cable Row (Low Position)": {"sets": 3, "counts": 12, "set_rest_time": 60},
                    "Spider Curl": {"sets": 3, "counts": 15, "set_rest_time": 60},
                    "Cable Kickback": {"sets": 3, "counts": 15, "set_rest_time": 60}
                },
                "notes": "Maintain a controlled tempo with a 3-1-1-0 pace.",
                "explanations": "Incline Bench Press targets upper chest, contributing to muscle symmetry. V-Grip Pulldown and Kneeling Single Arm Cable Row focus on back, ensuring balanced development. Spider Curl and Cable Kickback enhance arm definition. Exercises are selected for upper body muscle hypertrophy while respecting limitations.",
                "rest_time": 240
            },
            "day 5": {
                "day_type": "LOWER_BODY",
                "exercises": {
                    "Glute Kickback": {"sets": 4, "counts": 12, "set_rest_time": 75},
                    "Plank": {"sets": 3, "counts": 60, "set_rest_time": 60},
                    "Bicycle Crunch": {"sets": 3, "counts": 20, "set_rest_time": 60},
                    "Cable Woodchopper": {"sets": 3, "counts": 15, "set_rest_time": 60}
                },
                "notes": "Focus on core engagement during all exercises.",
                "explanations": "Repeat of Day 2 to maintain lower body and core development, focusing on glute strength and core stability, which is key for supporting the overall body structure and enhancing muscle tone.",
                "rest_time": 240
            },
            "day 6": {
                "day_type": "REST_DAY"
            },
            "day 7": {
                "day_type": "REST_DAY"
            }
        }

    formatter = TrainingWeekFormatter()
    summary_text = formatter.data_format(week_data)
    print(summary_text)
