import random

import constants as const


class WeaponVision(object):

    def __init__(self, weapon):
        self.user = weapon.user
        self.weapon = weapon

    def in_vision(self, other):
        return self.in_range(other)

    def in_range(self, other):
        return bool((other.x - self.user.x) ** 2 +
                    (other.y - self.user.y) ** 2 <=
                    self.weapon.w.RANGE ** 2)


class Weapon(object):

    def __init__(self, name, user):
        _weapons = {
            const.Weapon.Unarmed: Unarmed,
            const.Weapon.Heavy: Heavy,
            const.Weapon.Rifle: Rifle,
            const.Weapon.TurretGun: TurretGun
        }
        self.name = name
        self.w = _weapons[const.Weapon(name)]()
        self.w.user = user
        self.user = user
        self._vision = WeaponVision(self)

    def in_vision(self, other):
        return self._vision.in_vision(other)

    def shoot(self, detected):
        return self.w.shoot(detected)


class BaseWeapon(object):

    @property
    def damage(self):
        return int(random.choice(range(self.DMG[0], self.DMG[1], 1)))

    def shoot(self, detected):
        calc_damage = self.damage
        if random.randrange(100) < self.CRIT_CHANCE:
            calc_damage *= self.CRIT_MULTIPLIER

        if not self.DELAY:
            detected.got_hit(self.user, calc_damage)
        else:
            detected._delayed_command(self.DELAY,
                                      'got_hit', self.user,
                                      calc_damage).get()


class Unarmed(BaseWeapon):

    DMG = 1
    RANGE = 1
    CRIT_CHANCE = 1
    CRIT_MULTIPLIER = 1
    SHOOT_TIME = 1
    CHARGE_TYPE = ''
    DELAY = 1


class Rifle(BaseWeapon):

    DMG = (45, 60)
    RANGE = 360  # px
    CRIT_CHANCE = 30  # persent
    CRIT_MULTIPLIER = 2
    SHOOT_TIME = 0.8
    CHARGE_TYPE = 'bullet'
    DELAY = 0.5

    @property
    def SOUND(self):
        return random.choice(['fire3'])


class Heavy(BaseWeapon):

    DMG = (60, 95)
    RANGE = 150  # px
    CRIT_CHANCE = 15  # persent
    CRIT_MULTIPLIER = 3
    SHOOT_TIME = 1.1
    CHARGE_TYPE = 'bullet'
    DELAY = 0.5

    @property
    def SOUND(self):
        return random.choice(['fire'])


class TurretGun(BaseWeapon):

    DMG = (5, 8)
    RANGE = 200  # px
    CRIT_CHANCE = 15  # persent
    CRIT_MULTIPLIER = 2
    SHOOT_TIME = 1.5
    CHARGE_TYPE = 'bullet'
    DELAY = 0.15

    @property
    def SOUND(self):
        return random.choice(['fire'])
