SHOOT_DELAY = 1
RESURECTION_TIME = 5


class StatusType(dict):
    ALIVE = 'alive'
    DEAD = 'dead'


class ActionType(dict):
    IDLE = 'idle'
    WALK = 'walk'
    FIRE = 'fire'
    DEATH_FROM_ABOVE = 'death_from_above'


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
