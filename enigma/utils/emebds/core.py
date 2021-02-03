# -*- coding: utf-8 -*-
from datetime import datetime

from discord import Embed, User, Color


class CustomEmbed(Embed):
    def __init__(self, author: User, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.utcnow()
        self.set_footer(
            text=str(author),
            icon_url=author.avatar_url
        )


class ErrorEmbed(CustomEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.colour = Color.red()


class SuccessEmbed(CustomEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.colour = Color.red()


class InfoEmbed(CustomEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.colour = Color.blue()


class MiscEmbed(CustomEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.colour = Color.gold()
