HEAL_TIME = 1
RESURECTION_TIME = 5
HUMAN_HEALTH = 100
MAX_AP = 10

HEAL_AP = 3
FIRE_AP = 4


class StatusType(dict):

    ALIVE = 'alive'
    DEAD = 'dead'

    __slots__ = [ALIVE, DEAD]


class ActionType(dict):

    IDLE = 'idle'
    WALK = 'walk'
    FIRE = 'fire'
    HEAL = 'heal'
    DEATH_FROM_ABOVE = 'death_from_above'

    __slots__ = [IDLE, WALK, FIRE, HEAL, DEATH_FROM_ABOVE]


class DirectionType(dict):

    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'

    __slots__ = [LEFT, RIGHT, TOP, BOTTOM]


class WeaponType(dict):

    NO_WEAPON = 'no_weapon'
    M60 = 'm60'

    __slots__ = [NO_WEAPON, M60]


class ArmorType(dict):

    NO_ARMOR = 'no_armor'
    ENCLAVE_POWER_ARMOR = 'enclave_power_armor'

    __slots__ = [NO_ARMOR, ENCLAVE_POWER_ARMOR]
