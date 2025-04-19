import pandas as pd


class ExercisesProcessor:
    def __init__(self, raw_exercises_df):
        self.exercises_df = self.__one_hot_encode_equipment(raw_exercises_df)

    def __one_hot_encode_equipment(self, raw_exercises_df):
        pass
