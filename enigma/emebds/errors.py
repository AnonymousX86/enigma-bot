# -*- coding: utf-8 -*-
from discord import User, Member
from discord.ext.commands import Context

from enigma.emebds.core import ErrorEmbed


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
        if ctx:
            self.title = ':octagonal_sign: Error'
            self.description = f'***[Message link]({ctx.message.jump_url} "Click me!")***\n\n'
            self.add_field(
                name='Context',
                value=f'Channel \u2015 {ctx.channel.mention}\n'
                      f'User \u2015 {ctx.author.mention}\n'
                      f'Datetime \u2015 {str(ctx.message.created_at)[:19]}',
                inline=False
            ).add_field(
                name='Message',
                value=f'```\n'
                      f'{ctx.message.content}\n'
                      f'```\n',
                inline=False
            )
        if e:
            self.add_field(
                name='Error traceback',
                value='```diff\n'
                      '- {0}: {1}\n'
                      '```'.format(e.__class__.__name__, str(e).replace('\n', '\n- ')),
                inline=False
            )
        if member:
            self.add_field(
                name='Member',
                value=f'{str(member)} - {member.mention}'
            ).add_field(
                name='Guild',
                value=str(member.guild)
            )
