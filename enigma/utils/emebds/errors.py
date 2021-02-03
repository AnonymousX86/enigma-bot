# -*- coding: utf-8 -*-
from datetime import datetime as d

from discord import User, Member
from discord.ext.commands import Context

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


class DebugEmbed(ErrorEmbed):
    def __init__(self, author: User, ctx: Context = None, e: Exception = None, member: Member = None, **kwargs):
        super().__init__(author, **kwargs)
        data = ''
        if ctx:
            data += f'{ctx.author.mention} raised an error in {ctx.channel.mention}.\n\n' \
                    f'**[Message Link]({ctx.message.jump_url})**\n\n' \
                    f'**MESSAGE INFO:**' \
                    f'```xl\n' \
                    f'Channel ID  - {ctx.channel.id}\n' \
                    f'User ID     - {ctx.author.id}\n' \
                    f'Datetime    - {str(d.utcnow())[:19]}\n' \
                    f'```\n' \
                    f'**MESSAGE CONTENT:**\n' \
                    f'```\n' \
                    f'{ctx.message.content}\n' \
                    f'```\n'

        if e is not None:
            data += f'**ERROR:**\n' \
                    f'```diff\n' \
                    f'- {e.__class__.__name__}: {e}\n' \
                    f'```'

        if member:
            data += f'Member {member.mention} raised an error.'

        self.description = data
