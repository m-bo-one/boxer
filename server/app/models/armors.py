import constants as const


class Armor(object):

    def __init__(self, name, user):
        _armors = {
            const.Armor.GhoulArmour: GhoulArmour,
            const.Armor.MutantArmour: MutantArmour,
            const.Armor.Mutant: NoArmour,
        }
        self.name = name
        self.a = _armors[const.Armor(name)]()
        self.a.user = user
        self.user = user

    def reduce_damage(self, weapon, dmg):
        try:
            return int(dmg * (1 - self.a.RESISTANCE[weapon.w.CHARGE_TYPE]))
        except KeyError:
            return dmg


class MutantArmour(object):

    RESISTANCE = {
        'bullet': 0.7,
        'flame': 0.4
    }


class GhoulArmour(object):

    RESISTANCE = {
        'bullet': 0.3,
        'flame': 0.0
    }


class NoArmour(object):

    RESISTANCE = {
        'bullet': 0.0,
        'flame': 0.0
    }
