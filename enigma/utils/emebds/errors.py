# -*- coding: ut-8 -*-
from discord import User

from enigma.utils.emebds.core import ErrorEmbed


class TimeoutEmbed(ErrorEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':x: Timed out'
        self.description = 'Next time please type faster.'


class CooldownEmbed(ErrorEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':x: Command\'s on cooldown'
