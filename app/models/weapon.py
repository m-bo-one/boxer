import logging
import math

from constants import WeaponType


class WeaponVision(object):

    def __init__(self, user, R=400, alpha=15):
        self.user = user
        self.R = R
        self.alpha = alpha

    def to_dict(self):
        return {
            'alphas': self.alphas,
            'alphae': self.alphae,
            'R': self.R
        }

    def is_inside_sector(self, other):
        def are_clockwise(center, radius, angle, point2):
            point1 = (
                (center[0] + radius) * math.cos(math.radians(angle)),
                (center[1] + radius) * math.sin(math.radians(angle))
            )
            return bool(-point1[0] * point2[1] + point1[1] * point2[0] > 0)

        points = [
            other._vision._sector_center,
            # other.coords,
            (other.x + (other.width / 2), other.y),
            # (other.x + other.width, other.y),
            # (other.x, other.y + (other.height / 2)),
            # (other.x, other.y + other.height),
            (other.x + (other.width / 2), other.y + other.height),
            # (other.x + other.width, other.y + other.height),
            # (other.x + other.width, other.y + (other.height / 2)),
        ]
        center = self.user._vision._sector_center
        radius = self.R
        angle1 = self.alphas
        angle2 = self.alphae

        logging.debug('Points: %s', points)
        logging.debug('Width: %s', other.width)
        logging.debug('Height: %s', other.height)

        for point in points:
            rel_point = (point[0] - center[0], point[1] - center[1])

            logging.debug('--------------')
            logging.debug('Search point - x:%s, y:%s' % point)
            logging.debug('Radius center - x:%s, y:%s' % center)
            logging.debug('Radius length - %s' % radius)
            logging.debug('Angle start - %s' % self.alphas)
            logging.debug('Angle end - %s' % self.alphae)
            logging.debug('Point diff - x:%s, y:%s' % rel_point)
            logging.debug('--------------')

            is_detected = bool(
                not are_clockwise(center, radius, angle1, rel_point) and
                are_clockwise(center, radius, angle2, rel_point) and
                (rel_point[0] ** 2 + rel_point[1] ** 2 <= radius ** 2))
            if is_detected:
                return True
        else:
            return False

    @property
    def alphas(self):
        alpha = self.alpha / 2
        if self.user.direction == 'left':
            return 180 - alpha
        elif self.user.direction == 'right':
            return -alpha
        elif self.user.direction == 'top':
            return -90 - alpha
        elif self.user.direction == 'bottom':
            return 90 - alpha

    @property
    def alphae(self):
        alpha = self.alpha / 2
        if self.user.direction == 'left':
            return 180 + alpha
        elif self.user.direction == 'right':
            return alpha
        elif self.user.direction == 'top':
            return -90 + alpha
        elif self.user.direction == 'bottom':
            return 90 + alpha

    @property
    def _sector_center(self):
        result = (self.user.x + (self.user.width / 2),
                  self.user.y + (self.user.height / 2))
        logging.info('Sector start coords: (%s, %s)' % result)
        return result

    @classmethod
    def patch_user(cls, user):
        user._vision = cls(user)


class Weapon(object):

    def __init__(self, name):
        _weapons = {
            WeaponType.M60: M60Weapon
        }
        self.name = name
        self._w = _weapons[name]
        self.vision = WeaponVision(
            R=self._w.RANGE,
            alpha=self._w.SPECTRE
        )

    def in_vision(self, user, other):
        return self._w.in_vision(user, other)

    def shoot(self, detected):
        return self._w.shoot(detected)


class M60Weapon(object):

    DMG = 60
    RANGE = 200
    SPECTRE = 30

    def in_vision(self, user, other):
        pass

    def shoot(self, detected):
        pass
