SHOOT_DELAY = 2


class ActionType(dict):
    IDLE = 'idle'
    WALK = 'walk'
    FIRE = 'fire'


class DirectionType(dict):
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'


class WeaponType(dict):
    NO_WEAPON = 'no_weapon'
    M60 = 'm60'


class ArmorType(dict):
    NO_ARMOR = 'no_armor'
    ENCLAVE_POWER_ARMOR = 'enclave_power_armor'
