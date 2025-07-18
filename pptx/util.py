class Inches(float):
    def __new__(cls, value):
        return float.__new__(cls, value)
