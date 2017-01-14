import constants as const


class Armor(object):

    def __init__(self, name, user):
        _armors = {
            const.Armor.GhoulArmour: GhoulArmour
        }
        self.name = name
        self.a = _armors[const.Armor(name)]()
        self.a.user = user
        self.user = user

    def reduce_damage(self, weapon, dmg):
        return self.a.reduce_damage(weapon, dmg)


class GhoulArmour(object):

    RESISTANCE = {
        'bullet': 0.8,
        'flame': 0.6
    }

    def reduce_damage(self, weapon, dmg):
        try:
            return int(dmg * (1 - self.RESISTANCE[weapon.w.CHARGE_TYPE]))
        except KeyError:
            return dmg
