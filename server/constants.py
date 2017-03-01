from enum import IntEnum

HEAL_TIME = 1
RESURECTION_TIME = 5
HUMAN_HEALTH = 100
MAX_AP = 10

HEAL_AP = 4
FIRE_AP = 5
STEALTH_AP = 3

HUMAN_SIZE = (40, 75)


class Display(IntEnum):

    Hidden = 1
    Exposed = 2


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

    NW = 5
    NE = 6
    SW = 7
    SE = 8


class Race(IntEnum):

    Human = 1
    Ghoul = 2
    Mutant = 3
    Pipboy = 4


class Armor(IntEnum):

    Unarmored = 1
    GhoulArmour = 2
    MutantArmour = 3


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

    TurretGun = 11


class Action(IntEnum):

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
    Magichigh = 12
    Pickup = 13
    Recoil = 14
    Heal = 15
    Walk = 16

    Bighole = 17
    Cutinhalf = 18
    Electrify = 19
    ElectrifyOverlay = 20
    Explode = 21
    Fire = 22
    FireOverlay = 23
    Melt = 24
    Riddled = 25

    @staticmethod
    def get_death_keys():
        return [
            Action.Bighole,
            Action.Cutinhalf,
            Action.Electrify,
            Action.ElectrifyOverlay,
            Action.Explode,
            Action.Fire,
            Action.FireOverlay,
            Action.Melt,
            Action.Riddled
        ]
