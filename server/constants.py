from enum import IntEnum

HEAL_TIME = 1
RESURECTION_TIME = 5
HUMAN_HEALTH = 100
MAX_AP = 10

HEAL_AP = 3
FIRE_AP = 4

HUMAN_SIZE = (40, 75)


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


class Position(IntEnum):

    Crouch = 1
    Prone = 2
    Stand = 3
    Death = 4


class Direction(IntEnum):

    N = 1
    E = 2
    S = 3
    W = 4


class Armor(IntEnum):

    Ghoul = 1
    GhoulArmour = 2
    Mutant = 3
    MutantArmour = 4


class Weapon(IntEnum):

    Unarmed = 1
    Club = 2
    Heavy = 3
    Knife = 4
    Minigun = 5
    Pistol = 6
    Rifle = 7
    Rocket = 8
    SMG = 9
    Spear = 10


class BaseAction(IntEnum):

    Breathe = 1
    Attack = 2
    DodgeOne = 3
    DodgeTwo = 4
    Fallback = 5
    Fallenback = 6
    Fallforward = 7
    Fallenforward = 8
    Getupback = 9
    Getupforward = 10
    Magiclow = 11
    Magichigh = 11
    Pickup = 12
    Recoil = 13
    Heal = 14


class DeathAction(IntEnum):

    Bighole = 1
    Cutinhalf = 2
    Electrify = 3
    ElectrifyOverlay = 4
    Explode = 5
    Fire = 6
    FireOverlay = 7
    Melt = 8
    Riddled = 9
