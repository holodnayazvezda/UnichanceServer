from enum import Enum


class LessonSubject(str, Enum):
    UNICHANCE = "unichance"
    MATH = "math"
    INF = "informatics"
    CHEM = "chemistry"
    PHYS = "physics"
