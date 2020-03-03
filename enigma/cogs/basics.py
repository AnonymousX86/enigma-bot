# -*- coding: utf-8 -*-
from discord import Embed
from discord.ext.commands import command, Cog

from datetime import datetime as d

from ..utils.colors import random_color


class Basics(Cog):

    def __init__(self, bot):
        self.bot = bot

    # @command(
    #     name='help',
    #     description='Shows this message.\n'
    #                 '`<...>` - Needed argument.\n'
    #                 '`[...]` - Optional argument.\n'
    #                 '`<..|..>` - Choose 1 needed argument from many.\n'
    #                 '`[..|..]` - Choose 1 optional argument from many.\n',
    #     brief='Help command',
    #     usage='[command]',
    #     aliases=['h', ]
    # )
    # async def help(self, ctx, arg: str = ''):
    #     if arg == '':
    #         pass

    @command(
        name='ping',
        description='Checks bot latency'
    )
    async def ping(self, ctx):
        start_time = d.timestamp(ctx.message.created_at)
        await ctx.send(embed=Embed(
            title=':ping_pong: Pong!',
            description=f'It took me: {round((d.timestamp(d.now()) - start_time) / 1000, 2)}ms',
            color=random_color()
        ))
        return


def setup(bot):
    bot.add_cog(Basics(bot))
