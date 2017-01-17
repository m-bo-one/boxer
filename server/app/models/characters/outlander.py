import constants as const

from . import CharacterModel


class Outlander(CharacterModel):

    setup_params = {
        'health': 250,
        'race': const.Race.Ghoul,
        'weapon': const.Weapon.Rifle,
        'armor': const.Armor.GhoulArmour
    }

    @classmethod
    def create(cls, user_id, name):
        return super(Outlander, cls).create(
            user_id=user_id, name=name, **cls.setup_params
        )
