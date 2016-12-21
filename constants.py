import enum


class ActionType(dict):
    IDLE = 'idle'
    WALK = 'walk'


class DirectionType(dict):
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'


class WeaponType(dict):
    NO_WEAPON = 'no_weapon'
    FLAMETHROWER = 'flamethrower'


class ArmorType(dict):
    NO_ARMOR = 'no_armor'
    ENCLAVE_POWER_ARMOR = 'enclave_power_armor'
