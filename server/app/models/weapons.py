import logging
import math
import random


import constants as const


class WeaponVision(object):

    def __init__(self, weapon):
        self.user = weapon.user
        self.weapon = weapon

    def in_vision(self, other):
        return other

    @property
    def vision_direction(self):
        pass

    def _in_circle(self, other):
        pass

    # def in_sector(self, user, other):
    #     def are_clockwise(center, radius, angle, point2):
    #         point1 = (
    #             (center[0] + radius) * math.cos(math.radians(angle)),
    #             (center[1] + radius) * math.sin(math.radians(angle))
    #         )
    #         return bool(-point1[0] * point2[1] + point1[1] * point2[0] > 0)

    #     points = [
    #         (other.x + (other.width / 2), other.y + (other.height / 2)),
    #         (other.x + (other.width / 2), other.y),
    #         (other.x + (other.width / 2), other.y + other.height),
    #     ]
    #     center = (user.x + (user.width / 2), user.y + (user.height / 2))
    #     radius = self.R
    #     angle1 = self._get_alphas(user.cmd.direction)
    #     angle2 = self._get_alphae(user.cmd.direction)

    #     logging.debug('Points: %s', points)
    #     logging.debug('Direction: %s', user.cmd.direction)
    #     logging.debug('Width: %s', other.width)
    #     logging.debug('Height: %s', other.height)

    #     for point in points:
    #         rel_point = (point[0] - center[0], point[1] - center[1])
    #         is_detected = bool(
    #             not are_clockwise(center, radius, angle1, rel_point) and
    #             are_clockwise(center, radius, angle2, rel_point) and
    #             (rel_point[0] ** 2 + rel_point[1] ** 2 <= radius ** 2))
    #         if is_detected:
    #             return True
    #     else:
    #         return False

    # def _get_alphas(self, direction):
    #     alpha = self.alpha / 2
    #     if direction == 'left':
    #         return 180 - alpha
    #     elif direction == 'right':
    #         return -alpha
    #     elif direction == 'top':
    #         return -90 - alpha
    #     elif direction == 'bottom':
    #         return 90 - alpha

    # def _get_alphae(self, direction):
    #     return self._get_alphas(direction) + self.alpha


class Weapon(object):

    def __init__(self, name, user):
        _weapons = {
            const.Weapon.Unarmed: Unarmed,
            const.Weapon.Heavy: Heavy,
            const.Weapon.Rifle: Rifle,
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
        return int(random.choice(xrange(self.DMG[0],
                                        self.DMG[1],
                                        1)))

    def shoot(self, detected):
        calc_damage = self.damage
        if random.randrange(100) < self.CRIT_CHANCE:
            calc_damage *= self.CRIT_MULTIPLIER

        is_killed = detected._delayed_command(0.5, 'got_hit', self.user.weapon,
                                              calc_damage).get()
        if is_killed:  # killed
            self.user._delayed_command(0, 'update_scores')


class Unarmed(BaseWeapon):

    DMG = 1
    RANGE = 1
    CRIT_CHANCE = 1
    CRIT_MULTIPLIER = 1
    SHOOT_TIME = 1
    CHARGE_TYPE = ''


class Rifle(BaseWeapon):

    DMG = (45, 60)
    RANGE = 180  # px
    CRIT_CHANCE = 30  # persent
    CRIT_MULTIPLIER = 2
    SHOOT_TIME = 0.8
    CHARGE_TYPE = 'bullet'

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

    @property
    def SOUND(self):
        return random.choice(['fire'])
