from constants import ArmorType


class Armor(object):

    def __init__(self, name, user):
        _armors = {
            ArmorType.NO_ARMOR: NoArmor,
            ArmorType.ENCLAVE_POWER_ARMOR: EnclavePowerArmor
        }
        self.name = name
        self.a = _armors[name]()
        self.a.user = user
        self.user = user

    def reduce_damage(self, weapon, dmg):
        return self.a.reduce_damage(weapon, dmg)


class BaseArmor(object):

    RESISTANCE = {
        'bullet': 0.0,
        'flame': 0.0
    }

    def reduce_damage(self, weapon, dmg):
        try:
            return int(dmg * (1 - self.RESISTANCE[weapon.w.CHARGE_TYPE]))
        except KeyError:
            return dmg


class NoArmor(BaseArmor):
    pass


class EnclavePowerArmor(BaseArmor):

    RESISTANCE = {
        'bullet': 0.8,
        'flame': 0.6
    }
