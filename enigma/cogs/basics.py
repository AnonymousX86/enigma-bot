# -*- coding: utf-8 -*-
from discord import Embed
from discord.ext.commands import command, Cog, has_permissions, MissingPermissions, Context, cooldown, BucketType, \
    CommandOnCooldown

from enigma.settings import in_production
from enigma.utils.colors import random_color
from enigma.utils.exceptions import NoError


class Basics(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='error',
        brief='Raises an example error',
        description='Only specific users have access to this command',
        aliases=['err'],
        enabled=in_production(),
        hidden=True
    )
    @cooldown(1, 30, BucketType.user)
    @has_permissions(administrator=True)
    async def error_cmd(self, ctx: Context):
        """Raises a bot's internal error.

        :param ctx: Context object.
        """
        await self.bot.debug_log(ctx=ctx, e=NoError())
        await ctx.send(embed=Embed(
            title=':exclamation: Raised `NoError`',
            description='Bot\'s owner should be notified',
            color=random_color()
        ))

    @error_cmd.error
    async def error_error(self, ctx: Context, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(embed=Embed(
                title=':man_technologist: You\'re not an IT specialist',
                description='Only those can use this command',
                color=random_color()
            ))
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(embed=Embed(
                title=':x: Command\'s on cooldown',
                color=random_color()
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)

    @command(
        name='ping',
        brief='Checks bot latency',
        description='Counts time difference between command execution time and bot\'s response',
        enabled=in_production()
    )
    async def ping(self, ctx):
        """Checks bot's latency.

        :param ctx: Context object.
        """
        await ctx.send(embed=Embed(
            title=':ping_pong: Pong!',
            description=f'Current latency is: {round(self.bot.latency * 1000)}ms',
            color=random_color()
        ))

    @command(
        name='invite',
        brief='Sends bot\'s invite link',
        enabled=in_production()
    )
    async def invite(self, ctx: Context):
        link = 'https://discord.com/api/oauth2/authorize?client_id=678357487560425555&permissions=27718&scope=bot'
        await ctx.send(embed=Embed(
            title=':mailbox_with_mail: Here\'s an invite link',
            description='**\u00bb [Click me!]({0} "{0}") \u00ab**'.format(link),
            color=random_color()
        ).add_field(
            name='Important info',
            value='Remember, that you need **manage users** permission to add me to the server.'
        ))

    @command(
        name='info',
        brief='Sends short bot\'s info',
        description='Sends info about bot itself and its author. This is NOT help command.',
        aliases=['about', 'github', 'code'],
        enabled=in_production()
    )
    async def info(self, ctx: Context):
        await ctx.send(embed=Embed(
            title=':desktop: Source code',
            description='This bot is made on open source, GNU GPL v3.0 license.',
            color=random_color()
        ).add_field(
            name='Links',
            value='\u00b7 [GitHub homepage](https://github.com/AnonymousX86/Enigma-Bot)\n'
                  '\u00b7 [Changelog](https://github.com/AnonymousX86/Enigma-Bot/'
                  'blob/master/docs/CHANGELOG.md#enigma-bot-changelog)\n'
        ).add_field(
            name='Additional info',
            value='If you\'d like to help to develop this bot just make a pull request on GitHub or'
                  ' write to bot main dev.'
        ).add_field(
            name='More about bot',
            value='Version: *v{0}*.\n'
                  'Author: *{1.display_name}#{1.discriminator}*.'.format(
                      self.bot.version,
                      self.bot.get_user(self.bot.owner_id)
                  )
        ))


def setup(bot):
    bot.add_cog(Basics(bot))
