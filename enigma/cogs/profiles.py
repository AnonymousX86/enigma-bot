# -*- coding: utf-8 -*-
from discord import Embed, User
from discord.ext.commands import Cog, command, UserNotFound

from enigma.utils.colors import random_color
from enigma.utils.database import get_single_user, update_profile, user_get_cash
from enigma.utils.strings import f_btc


class Profiles(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='profile',
        brief='Shows user\'s profile from bot\'s database',
        usage='[user]',
        aliases=['prof']
    )
    async def profile(self, ctx: Context, user: User = None):
        """Sends user's profile. (XP, cash, etc.)

        :param ctx: Context object.
        :param user: User which profile should be showed. (optional)
        """
        if not user:
            user = ctx.author
        if user.bot is True:
            await ctx.send(embed=Embed(
                title=':x: Bots do not have profiles',
                color=random_color()
            ))
        else:
            msg = await ctx.send(embed=Embed(
                title=':hourglass_flowing_sand: Please wait...',
                color=random_color()
            ))
            result_user = get_single_user(user.id if user else ctx.author.id)
            await msg.edit(embed=Embed(
                title=':card_box: User\'s data',
                description='```py\n'
                            '{0.display_name}#{0.discriminator}\n'
                            '```'.format(ctx.guild.get_member(result_user.user_id)),
                color=random_color()
            ).add_field(
                name='XP',
                value=str(result_user.user_xp)
            ).add_field(
                name='Cash',
                value=f_btc(result_user.user_cash)
            ).set_footer(
                text=f'Accessed by {ctx.author.display_name}'
            ))

    @command(
        name='daily',
        brief='Collect daily cash bonus',
        description='Cooldown resets on 00:00.'
    )
    async def daily(self, ctx: Context):
        base_cash = 200
        user = get_single_user(ctx.author.id)
        now = d.now()
        able = False
        time_travel = False
        if user.last_daily.year == now.year:
            if user.last_daily.month == now.month:
                if user.last_daily.day < now.day:
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
            await ctx.send(embed=Embed(
                title=':x: Hello time traveler',
                description='Anyway, there\'s no cash for you.',
                color=random_color()
            ))
        elif able:
            new_user = user_get_cash(ctx.author.id, base_cash)
            await ctx.send(embed=Embed(
                title=':moneybag: Daily bonus gained!',
                description=f'You\'ve earned **{f_btc(base_cash)}**,'
                            f' so now you have **{f_btc(new_user.user_cash)}**.',
                color=random_color()
            ))

    @command(
        name='manage',
        brief='Manages users\' data',
        description='Only true Anonymous can use this command',
        help='Available options:\n'
             '- xp\n'
             '- cash',
        usage='<user> <option> <value>',
        hidden=True
    )
    async def manage(self, ctx: Context, user: User = None, option: str = None, value: int = None):
        if ctx.author.id != self.bot.owner_id:
            await ctx.send(embed=Embed(
                title=':x: You\'re not authorized',
                color=random_color()
            ))
        elif not user:
            await ctx.send(embed=Embed(
                title=':x: No user provided',
                color=random_color()
            ))
        elif user.bot is True:
            await ctx.send(embed=Embed(
                title=':x: Bots do not have profiles',
                color=random_color()
            ))
        elif not option:
            await ctx.send(embed=Embed(
                title=':x: No option specified',
                color=random_color()
            ))
        elif option not in ['xp', 'cash']:
            await ctx.send(embed=Embed(
                title=':x: Invalid option',
                color=random_color()
            ))
        elif not value:
            await ctx.send(embed=Embed(
                title=':x: No amount provided',
                color=random_color()
            ))
        else:
            msg = await ctx.send(embed=Embed(
                title=':hourglass_flowing_sand: Please wait',
                color=random_color()
            ))
            managed_user = get_single_user(user.id)
            if not managed_user:
                await msg.edit(embed=Embed(
                    title='User do not exists in database',
                    color=random_color()
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
                await msg.edit(embed=Embed(
                    title=':incoming_envelope: Profile has been updated',
                    description=text,
                    color=random_color()
                ))

    @command(
        name='avatar',
        brief='Shows user\'s avatar',
        description='No arg will return your\'s avatar and adding user ID or mention will show other user\'s avatar',
        usage='[user]',
        aliases=['avk']
    )
    async def avatar(self, ctx: Context, user: User = None):
        """Sends user's avatar.

        :param ctx: Context object.
        :param user: User mention or ID.
        """
        if not user:
            user = ctx.author
        await ctx.send(embed=Embed(
            title=':bust_in_silhouette: User avatar',
            description=f'As you wish, {ctx.author.mention}.',
            color=random_color()
        ).set_image(
            url=user.avatar_url
        ))

    @avatar.error
    async def avatar_error(self, ctx: Context, error):
        if isinstance(error, UserNotFound):
            await ctx.send(embed=Embed(
                title=':mag: User not found!',
                color=random_color()
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)


def setup(bot):
    bot.add_cog(Profiles(bot))
