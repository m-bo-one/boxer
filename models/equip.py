# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from constants import WeaponType, ArmorType
from utils import enum_convert

from db import DB


class NoWeapon(object):

    DISTANCE = 2
    DAMAGE = 1

    def __repr__(self):
        return "no_weapon"


class Flamer(object):

    DISTANCE = 10
    DAMAGE = 30

    def __repr__(self):
        return "flamer"

    def shoot(self):
        pass
