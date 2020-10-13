# -*- coding: utf-8 -*-
from datetime import datetime as d

from discord import Embed
from discord.ext.commands import Cog, command
from discord.utils import get

from enigma.utils.colors import random_color
from enigma.utils.datetime import execute_time, utc_to_local
from enigma.utils.searching import find_user


class Profiles(Cog):
    """
    Users' profiles related commands

    Commands:
        avatar: returns specified member avatar or, by default, member who invoked command avatar
    """

    def __init__(self, bot):
        self.bot = bot

    @command(
        name='avatar',
        brief='Shows user avatar',
        description='No arg  will return you\'s avatar and adding user ID or mention will show other user\'s avatar',
        usage='[user]',
        aliases=['avk']
    )
    async def avatar(self, ctx, user=None):
        start_time = d.timestamp(utc_to_local(ctx.message.created_at))

        # Get self avatar
        if user is None:
            user_id = ctx.message.author.id
            user_found = True

        # Provided argument
        else:
            user_id = find_user(user)

            # Bad argument or user is not found
            if user_id is None:
                user_found = False

            # User is found
            else:
                user_found = True

        if user_found is True:
            avatar = get(ctx.guild.members, id=user_id).avatar_url
            status = f'As you wish, {ctx.message.author.display_name}\n\n' \
                     f':arrow_right: [See in full resolution]({avatar})'

        else:
            avatar = None
            status = 'User avatar not found!'

        await ctx.send(embed=Embed(
            title=':bust_in_silhouette: User avatar',
            description=status,
            color=random_color()
        ).set_image(
            url=avatar
        ).set_footer(
            text=f'It took me {execute_time(start_time)}'
        ))


def setup(bot):
    bot.add_cog(Profiles(bot))
