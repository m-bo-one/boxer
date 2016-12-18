import enum


class ActionType(enum.IntEnum):
    IDLE = 0
    WALK = 1


class DirectionType(enum.IntEnum):
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3


class WeaponType(enum.IntEnum):
    NO_WEAPON = 0
    FLAMETHROWER = 1


class ArmorType(enum.IntEnum):
    NO_ARMOR = 0
    ENCLAVE_POWER_ARMOR = 1
