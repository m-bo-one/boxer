import constants as const

from .base import CharacterModel, autosave


class Outlander(CharacterModel):
    """Outlander - from ashes and pray he become a powerfull ambusher,
    could kill fast and without fear.

    Advantages:
        - Ambush from stealth (+300% damage)
        - High critical chance (45%)
        - Middle range
        - Can fast run
    Disadvantages:
        - Poor armor
        - Small damage when not in stealth
    """
    allowed_actions = set(['stealth', 'shoot', 'move', 'heal', 'equip'])

    setup_params = {
        'health': 250,
        'race': const.Race.Ghoul,
        'weapon': const.Weapon.Rifle,
        'armor': const.Armor.GhoulArmour,
        'display': const.Display.Exposed
    }

    @classmethod
    def create(cls, user_id, name):
        return super(Outlander, cls).create(
            user_id=user_id, name=name, **cls.setup_params
        )

    @autosave
    def stealth(self):
        if (self.is_dead or
           self.operations_blocked or
           self.AP - const.STEALTH_AP < 0 or
           not self.is_allowed('equip')):
            return
        self.use_AP(const.STEALTH_AP)
        self.display_toggle()
