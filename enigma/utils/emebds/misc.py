# -*- coding: utf-8 -*-
from discord import User, Guild

from enigma.utils.emebds.core import MiscEmbed


class PleaseWaitEmbed(MiscEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':hourglass_flowing_sand: Please wait...'


class DevelopmentEmbed(MiscEmbed):
    def __init__(self, author: User, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':tools: Function under development'


class JoinGuildEmbed(MiscEmbed):
    def __init__(self, author: User, guild: Guild, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':small_blue_diamond: Joined new guild'
        self.add_field(
            name='NAME',
            value=guild.name
        ).add_field(
            name='MEMBERS',
            value=guild.member_count
        ).add_field(
            name='OWNER',
            value=str(guild.owner)
        ).add_field(
            name='CREATED AT',
            value=guild.created_at
        ).set_thumbnail(
            url=guild.icon_url
        )


class RemoveGuildEmbed(MiscEmbed):
    def __init__(self, author: User, guild: Guild, **kwargs):
        super().__init__(author, **kwargs)
        self.title = ':small_orange_diamond: Removed from guild'
        self.add_field(
            name='NAME',
            value=guild.name
        )
