# -*- coding: utf-8 -*-
from discord.ext.commands import Cog, command, Context

from enigma.settings import in_production
from enigma.utils.emebds.misc import DevelopmentEmbed


class GameSeeker(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='host',
        brief='Hosts game',
        description='Creates your\'s event in provided game.',
        help='Bot sends info to all guilds with set game hosting, allowing other people too get in touch with you and'
             ' other gamers.',
        usage='<game name> [additional info]',
        enabled=not in_production()
    )
    async def host(self, ctx: Context, game: str = None, description: str = None):
        await ctx.send(embed=DevelopmentEmbed(
            author=ctx.author
        ).add_field(
            name='GAME',
            value=game
        ).add_field(
            name='DESCRIPTION',
            value=str(description)
        ))


def setup(bot):
    bot.add_cog(GameSeeker(bot))
