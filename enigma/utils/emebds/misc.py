# -*- coding: utf-8 -*-
from discord import User

from enigma.utils.emebds.core import MiscEmbed


class PleaseWaitEmbed(MiscEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':hourglass_flowing_sand: Please wait...'


class DevelopmentEmbed(MiscEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':tools: Function under development'
