import requests

user_info_json = {
  "email": "newuser@example.com",
  "image": "http://example.com/image3.jpg",
  "name": "New User",
  "gender": "male",
  "age": 40,
  "height": 180.5,
  "height_type": "cm",
  "weight": 82.0,
  "weight_type": "kg",
  "fitness_level": "intermediate",
  "improve_body_parts": ["abs", "shoulders", "chest"],
  "exercise_limitations": ["no_overhead_pressing"],
  "nutrition_goal": "lose_weight",
  "equipment_list": ["cable_machine", "barbell", "platform", "barbell", "ez_bar"],
  "training_days": 4,
  "workout_time": 60
}

scanner_info_json = {
    "disclaimer": "This analysis is based solely on the provided summary and is for simulation purposes only. It is not a substitute for professional medical or fitness advice. For personalized guidance, consulting with a fitness professional is recommended.",
    "physical_attributes": {
      "body_shape": "mesomorphic",
      "muscle_tone": "balanced with potential for improved definition",
      "muscle_symmetry": "balanced",
      "major_muscle_groups": ["chest", "shoulders"],
      "major_muscle_groups_indicators": ["well-developed"],
      "weak_muscle_groups": ["arms", "legs"],
      "weak_muscle_groups_indicators": ["potential focus needed on enhancing muscle hypertrophy"]
    },
    "estimated_body_fat": {
      "percentage_range": "15-20",
      "indicators": ["muscle definition cues"]
    },
    "training_readiness": {
      "score": 8,
      "indicators": ["upright posture", "high energy levels"]
    },
    "training_recommendations": {
      "body_development": {
        "upper_body": {
          "chest": ["bench presses", "push-ups"],
          "back": ["pull-ups", "rows"],
          "shoulders": ["shoulder presses", "lateral raises"],
          "arms": ["bicep curls", "triceps dips"]
        },
        "lower_body": {
          "legs": ["squats", "lunges"],
          "calves": ["calf raises"]
        },
        "core": ["planks", "back extensions"],
        "postural_balance": ["face pulls", "seated rows"]
      },
      "body_maintenance": {
        "upper_body": {
          "chest": ["bench presses", "push-ups"],
          "back": ["pull-ups", "rows"],
          "shoulders": ["shoulder presses", "lateral raises"],
          "arms": ["bicep curls", "triceps dips"]
        },
        "lower_body": {
          "legs": ["squats", "lunges"],
          "calves": ["calf raises"]
        },
        "core": {
          "exercises": ["planks", "back extensions"]
        },
        "postural_balance": {
          "exercises": ["face pulls", "seated rows"]
        }
      },
      "fat_loosing": {
        "cardiovascular": []
      }
    }
  }

prev_week = {
  "day 1": {
    "day_type": "UPPER_BODY",
    "exercises": {
      "1": {
        "sets": 4,
        "counts": 15,
        "set_rest_time": 90
      },
      "2": {
        "sets": 4,
        "counts": 15,
        "set_rest_time": 90
      },
      "3": {
        "sets": 3,
        "counts": 12,
        "set_rest_time": 60
      },
      "4": {
        "sets": 3,
        "counts": 12,
        "set_rest_time": 60
      },
      "5": {
        "sets": 3,
        "counts": 15,
        "set_rest_time": 60
      }
    },
    "notes": "Maintain a controlled tempo: 4-1-1-0 for each rep.",
    "explanations": "1. Lat Pulldown: Targets lats and biceps, increasing back strength. 2. Mid Chest Staggered Stance Cable Fly: Focuses on chest development without overhead pressing. 3. Unilateral Cable Lateral Raises: Targets shoulders while avoiding overhead pressing. 4. Supinated Pulldown: Works the biceps and lats further. 5. Single Arm Cross Body Extension: Isolates triceps, complementing chest work.",
    "rest_time": 180
  },
  "day 2": {
    "day_type": "LOWER_BODY",
    "exercises": {
      "1": {
        "sets": 4,
        "counts": 20,
        "set_rest_time": 90
      },
      "2": {
        "sets": 4,
        "counts": 20,
        "set_rest_time": 90
      },
      "3": {
        "sets": 3,
        "counts": 15,
        "set_rest_time": 60
      },
      "4": {
        "sets": 3,
        "counts": 15,
        "set_rest_time": 60
      }
    },
    "notes": "Focus on core stability and engagement during all exercises.",
    "explanations": "1. Glute Kickback: Targets glutes, important for lower body strength. 2. Plank: Enhances core stability, crucial for overall performance. 3. Bicycle Crunch: Works core, especially obliques, supporting fat loss goal. 4. Cable Woodchopper: Engages core and obliques, enhancing rotational strength.",
    "rest_time": 180
  },
  "day 3": {
    "day_type": "REST_DAY"
  },
  "day 4": {
    "day_type": "UPPER_BODY",
    "exercises": {
      "1": {
        "sets": 4,
        "counts": 15,
        "set_rest_time": 90
      },
      "2": {
        "sets": 4,
        "counts": 15,
        "set_rest_time": 90
      },
      "3": {
        "sets": 3,
        "counts": 12,
        "set_rest_time": 60
      },
      "4": {
        "sets": 3,
        "counts": 12,
        "set_rest_time": 60
      },
      "5": {
        "sets": 3,
        "counts": 15,
        "set_rest_time": 60
      }
    },
    "notes": "Maintain a controlled tempo: 4-1-1-0 for each rep.",
    "explanations": "1. V-Grip Pulldown: Provides a varied grip to target lats and biceps. 2. Downward Cable Fly: Focuses on lower chest, complementing previous chest work. 3. Kneeling Single Arm Cable Row: Targets lower lats, improving back detail. 4. Spider Curl: Isolates biceps for increased arm size. 5. Cable Kickback: Targets triceps, completing the arm workout.",
    "rest_time": 180
  },
  "day 5": {
    "day_type": "LOWER_BODY",
    "exercises": {
      "1": {
        "sets": 4,
        "counts": 20,
        "set_rest_time": 90
      },
      "2": {
        "sets": 4,
        "counts": 20,
        "set_rest_time": 90
      },
      "3": {
        "sets": 3,
        "counts": 15,
        "set_rest_time": 60
      },
      "4": {
        "sets": 3,
        "counts": 15,
        "set_rest_time": 60
      }
    },
    "notes": "Focus on core engagement during all exercises.",
    "explanations": "1. Glute Kickback: Reinforces glute strength for lower body power. 2. Plank: Ensures a strong core, essential for injury prevention. 3. Bicycle Crunch: Supports the calorie deficit goal by engaging the core. 4. Cable Woodchopper: Enhances core rotation, important for overall stability.",
    "rest_time": 180
  },
  "day 6": {
    "day_type": "REST_DAY"
  },
  "day 7": {
    "day_type": "REST_DAY"
  }
}

feedback_key = "normal"

payload = {
    "user_info": user_info_json,
    "scanner_info": scanner_info_json,
    # "prev_week": prev_week,
    # "feedback_key": feedback_key
}


payload = {
  "scanner_info": {
    "disclaimer": "This analysis is based solely on provided data and is for simulation purposes only. It should not replace professional medical or fitness advice.",
    "physical_attributes": {
      "body_shape": "mesomorph",
      "muscle_tone": "muscular and well-defined",
      "muscle_symmetry": "balanced",
      "major_muscle_groups": [
        "chest",
        "arms"
      ],
      "major_muscle_groups_indicators": [
        "good definition"
      ],
      "weak_muscle_groups": [
        "legs"
      ],
      "weak_muscle_groups_indicators": [
        "lack of definition"
      ]
    },
    "estimated_body_fat": {
      "percentage_range": "15-20",
      "indicators": [
        "visible muscle lines",
        "some abdominal definition"
      ]
    },
    "training_readiness": {
      "score": 8,
      "indicators": [
        "high energy levels",
        "strong physical condition"
      ]
    },
    "training_recommendations": {
      "body_development": {
        "upper_body": {
          "chest": [
            "bench press",
            "incline dumbbell press"
          ],
          "back": [
            "pull-ups",
            "bent-over rows"
          ],
          "shoulders": [
            "overhead press",
            "lateral raises"
          ],
          "arms": [
            "bicep curls",
            "tricep dips"
          ]
        },
        "lower_body": {
          "legs": [
            "squats",
            "deadlifts"
          ],
          "calves": [
            "calf raises"
          ]
        },
        "core": [
          "planks",
          "Russian twists"
        ],
        "postural_balance": [
          "yoga",
          "Pilates"
        ]
      },
      "body_maintenance": {
        "upper_body": {
          "chest": [
            "push-ups",
            "chest fly"
          ],
          "back": [
            "lat pull-downs",
            "seated rows"
          ],
          "shoulders": [
            "front raises",
            "shrugs"
          ],
          "arms": [
            "hammer curls",
            "tricep extensions"
          ]
        },
        "lower_body": {
          "legs": [
            "lunges",
            "leg press"
          ],
          "calves": [
            "seated calf raises"
          ]
        },
        "core": {
          "exercises": [
            "sit-ups",
            "leg raises"
          ]
        },
        "postural_balance": {
          "exercises": [
            "balance exercises",
            "core stability exercises"
          ]
        }
      },
      "fat_loosing": {
        "cardiovascular": [
          "running",
          "cycling",
          "HIIT",
          "brisk walking"
        ]
      }
    }
  },
  "user_info": {
    "email": "kireev@gmail.com",
    "image": "https://test-fitness.s3.regru.cloud/6186d19e-e875-47f1-a8b5-cf2fb29580d7-1751370544655732742_2025-07-01 01.24.32.jpg",
    "name": "Khanil",
    "gender": "male",
    "age": 22,
    "height": 197,
    "height_type": "cm",
    "weight": 100,
    "weight_type": "kg",
    "fitness_level": "intermediate",
    "improve_body_parts": [
      "abs",
      "shoulders",
      "chest"
    ],
    "exercise_limitations": [
      "no_overhead_pressing"
    ],
    "nutrition_goal": "lose_weight",
    "equipment_list": [
      "barbell"
    ],
    "training_days": 6,
    "workout_time": 60
  }
}

resp = requests.post("https://a9008069abc1.ngrok-free.app//generate_first_week", json=payload)
print(resp.json())
