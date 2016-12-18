# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from constants import WeaponType, ArmorType
from utils import enum_convert


class Gear(object):

    def __init__(self, sprite, armor=None, weapon=None):
        self.armor = enum_convert(ArmorType, armor) or ArmorType.NO_ARMOR
        self.weapon = enum_convert(WeaponType, weapon) or WeaponType.NO_WEAPON
        self.load_sprite()

    def load_sprite(self):
        pass

    def equip(self,):
        pass

    def unequip(self):
        pass

    @property
    def has_armor(self):
        return bool(self.armor != ArmorType.NO_ARMOR)

    @property
    def has_weapon(self):
        return bool(self.weapon != WeaponType.NO_WEAPON)
