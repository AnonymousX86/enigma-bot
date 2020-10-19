# -*- coding: utf-8 -*-
from discord import Embed, User
from discord.ext.commands import Cog, command, UserNotFound

from enigma.utils.colors import random_color
from enigma.utils.database import get_single_user, update_profile
from enigma.utils.strings import chars


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
                            'XP:         {1.user_xp}\n'
                            'Cash:       {1.user_cash} {2}\n'
                            'Last daily: {1.last_daily}\n'
                            '```'.format(ctx.guild.get_member(result_user.user_id), result_user, chars['bitcoin']),
                color=random_color()
            ).set_footer(
                text=f'Accessed by {ctx.author.display_name}'
            ))

    @command(
        name='manage',
        brief='Manages users\' data',
        description='Only true Anonymous can use this command',
        help='Available options:\n'
             '- xp\n'
             '- cash',
        usage='<user> <option> <value>'
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
                text = '```py\n{0.display_name}#{0.discriminator}\n'
                text += 'XP:         {1}\n' if option == 'xp' else \
                        'Cash:       {1} {2}\n' if option == 'cash' else ''
                text += '```'
                await msg.edit(embed=Embed(
                    title=':incoming_envelope: Profile has been updated',
                    description=text.format(ctx.guild.get_member(updated_user.user_id), value, chars['bitcoin']),
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
        avatar = user.avatar_url
        status = f'As you wish, {ctx.message.author.display_name}\n\n' \
                 f':arrow_right: [See in full resolution]({avatar})'
        await ctx.send(embed=Embed(
            title=':bust_in_silhouette: User avatar',
            description=status,
            color=random_color()
        ).set_image(
            url=avatar
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
