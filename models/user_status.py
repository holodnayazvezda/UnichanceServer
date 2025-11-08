from enum import Enum


class UserStatus(str, Enum):
    GUEST = "guest"
    TEACHER = "teacher"
    SUPERADMIN = "superadmin"