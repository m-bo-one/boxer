from constants import WeaponType


class Weapon(object):

    def __init__(self, name):
        _weapons = {
            WeaponType.M60: M60Weapon
        }
        self.name = name


class M60Weapon(object):

    DMG = 60
