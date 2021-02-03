# -*- coding: utf-8 -*-
from datetime import datetime as d

from discord import Embed, User
from discord.ext.commands import Cog, command, UserNotFound, Context

from enigma.settings import in_production
from enigma.utils.colors import random_color
from enigma.utils.database import get_single_user, update_profile, user_get_cash
from enigma.utils.emebds.core import ErrorEmbed, SuccessEmbed
from enigma.utils.emebds.misc import PleaseWaitEmbed, DevelopmentEmbed
from enigma.utils.strings import f_btc


class Profiles(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='profile',
        brief='Shows user\'s profile',
        description='Show user\'s profile from database (XP, cash, etc.)',
        usage='[user]',
        aliases=['prof'],
        enabled=in_production()
    )
    async def profile(self, ctx: Context, user: User = None):
        if not user:
            user = ctx.author
        if user.bot is True:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Bots do not have profiles'
            ))
        else:
            msg = await ctx.send(embed=PleaseWaitEmbed(author=ctx.author))
            result_user = get_single_user(user.id if user else ctx.author.id)
            await msg.edit(embed=SuccessEmbed(
                author=ctx.author,
                title=':card_box: User\'s data',
                description='```py\n'
                            '{0.display_name}#{0.discriminator}\n'
                            '```'.format(ctx.guild.get_member(result_user.user_id))
            ).add_field(
                name='XP',
                value=str(result_user.user_xp)
            ).add_field(
                name='Cash',
                value=f_btc(result_user.user_cash)
            ))

    @command(
        name='daily',
        brief='Collect daily cash bonus',
        help='Cooldown resets on 00:00.',
        enabled=in_production()
    )
    async def daily(self, ctx: Context):
        base_cash = 200
        user = get_single_user(ctx.author.id)
        now = d.now()
        able = False
        time_travel = False
        if user.last_daily.year == now.year:
            if user.last_daily.month == now.month:
                if user.last_daily.day == now.day:
                    pass
                elif user.last_daily.day < now.day:
                    able = True
                else:
                    time_travel = True
            elif user.last_daily.month < now.month:
                able = True
            else:
                time_travel = True
        elif user.last_daily.year < now.year:
            able = True
        else:
            time_travel = True
        if time_travel:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Hello time traveler',
                description='Anyway, there\'s no cash for you.'
            ))
        elif able:
            new_user = user_get_cash(ctx.author.id, base_cash)
            await ctx.send(embed=SuccessEmbed(
                author=ctx.author,
                title=':moneybag: Daily bonus gained!',
                description=f'You\'ve earned **{f_btc(base_cash)}**,'
                            f' so now you have **{f_btc(new_user.user_cash)}**.'
            ))
        else:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: You\'ve already collected your daily cash',
                description='Please come back tomorrow.'
            ))

    @command(
        name='reputation',
        brief='Gives someone reputation',
        help='Available once a day, resets on 00:00.',
        usage='<user>',
        aliases=['rep'],
        enabled=not in_production()
    )
    async def reputation(self, ctx: Context):
        await ctx.send(embed=DevelopmentEmbed(author=ctx.author))

    @command(
        name='manage',
        brief='Manages users\' data',
        description='Only true Anonymous can use this command',
        help='Available options:\n'
             '- xp\n'
             '- cash',
        usage='<user> <option> <value>',
        enabled=in_production(),
        hidden=True
    )
    async def manage(self, ctx: Context, user: User = None, option: str = None, value: int = None):
        em = ErrorEmbed
        if ctx.author.id != self.bot.owner_id:
            st = ':x: You\'re not authorized'
        elif not user:
            st = ':x: No user provided'
        elif user.bot is True:
            st = ':x: Bots do not have profiles'
        elif not option:
            st = ':x: No option specified'
        elif option not in ['xp', 'cash']:
            st = ':x: Invalid option'
        elif value is None:
            st = ':x: No amount provided'
        else:
            st = None
            msg = await ctx.send(embed=PleaseWaitEmbed(author=ctx.author))
            managed_user = get_single_user(user.id)
            if not managed_user:
                await msg.edit(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':x: User do not exists in database'
                ))
            else:
                if option == 'xp':
                    updated_user = update_profile(user.id, xp=value)
                elif option == 'cash':
                    updated_user = update_profile(user.id, cash=value)
                else:
                    raise
                text = '```py\n{0.display_name}#{0.discriminator}\n'.format(ctx.guild.get_member(updated_user.user_id))
                if option == 'xp':
                    text += f'XP:         {value}\n'
                elif option == 'cash':
                    text += f'Cash:       {f_btc(value)}\n'
                text += '```'
                await msg.edit(embed=SuccessEmbed(
                    author=ctx.author,
                    title=':incoming_envelope: Profile has been updated',
                    description=text
                ))
        if st:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=st
            ))

    @command(
        name='avatar',
        brief='Shows user\'s avatar',
        description='No arg will return your\'s avatar and adding user ID or mention will show other user\'s avatar',
        usage='[user]',
        aliases=['avk'],
        enabled=in_production()
    )
    async def avatar(self, ctx: Context, user: User = None):
        if not user:
            user = ctx.author
        await ctx.send(embed=SuccessEmbed(
            author=ctx.author,
            title=f':bust_in_silhouette: {user} avatar',
            description=f'As you wish, {ctx.author.mention}.'
        ).set_image(
            url=user.avatar_url
        ))

    @avatar.error
    async def avatar_error(self, ctx: Context, error: Exception):
        if isinstance(error, UserNotFound):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':mag: User not found!'
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)


def setup(bot):
    bot.add_cog(Profiles(bot))
