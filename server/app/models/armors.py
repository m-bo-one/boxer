import constants as const


class Armor(object):

    def __init__(self, name, user):
        _armors = {
            const.Armor.GhoulArmour: GhoulArmour,
            const.Armor.MutantArmour: MutantArmour
        }
        self.name = name
        self.a = _armors.get(const.Armor(name), Unarmored)()
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


class Unarmored(object):

    RESISTANCE = {
        'bullet': 0.0,
        'flame': 0.0
    }
