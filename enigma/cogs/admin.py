# -*- coding: utf-8 -*-
from discord import Embed, User
from discord.errors import Forbidden  # If bot has no permissions for deleting message
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, MissingPermissions, \
    BotMissingPermissions, UserNotFound
from discord.utils import get
from enigma.src.bad_words import bad_words

from enigma.utils.colors import random_color


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='ban',
        brief='Bans user',
        description='You can provide user ID or mention someone',
        usage='<user>'
    )
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: User = None):
        """Bans user from guild.

        :param ctx: Context object.
        :param user: User mention or ID.
        """
        # No user provided
        if not user:
            await ctx.send(embed=Embed(
                title=':face_with_raised_eyebrow: Who do I need to ban?',
                description='You\'ve not provided a victim',
                color=random_color()
            ))

        else:
            # User is trying to ban yourself
            if user.id == ctx.message.author.id:
                await ctx.send(embed=Embed(
                    title=':clown: You can\'t ban yourself',
                    description='Ask someone to help you commit sepuku or something...',
                    color=random_color()
                ))

            # User is trying to ban guild owner
            elif user.id == ctx.guild.owner.id:
                await ctx.send(embed=Embed(
                    title=':crown: You can\'t ban guild owner',
                    description='He\'s the almighty one, sorry',
                    color=random_color()
                ))

            # User is trying to ban the bot
            elif user.id == self.bot.user.id:
                await ctx.send(embed=Embed(
                    title=':zany_face: I can\'t ban myself',
                    description='Even if I would I can\'t, sorry',
                    color=random_color()
                ))

            # No errors
            else:
                await ctx.send(embed=Embed(
                    title=f':hammer: Banning {get(ctx.guild.members, id=user.id)}',
                    description='(Just kidding, I\'m still in development)',
                    color=random_color()
                ))
                # TODO - enable banning

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            status = 'You don\'t have **ban** permissions!'

        elif isinstance(error, BotMissingPermissions):
            status = 'I don\' have **ban** permissions!'

        elif isinstance(error, UserNotFound):
            status = 'User not found!'

        else:
            status = 'Unknown error has occurred!'
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)

        await ctx.send(embed=Embed(
            title=':rolling_eyes: Whoops!',
            description=status,
            color=random_color()
        ))

    # TODO - unban command

    @command(
        name='kick',
        brief='Kicks user',
        description='You can provide user ID or mention someone',
        usage='<user>'
    )
    @has_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: User = None):
        """Kicks user from guild.

        :param ctx: Context object.
        :param user: User mention or ID.
        """
        # No user provided
        if not user:
            await ctx.send(embed=Embed(
                title=':cowboy: Who do I need to kick round the clock?',
                description='You\'ve not provided a victim',
                color=random_color()
            ))

        else:
            # User is trying to ban yourself
            if user.id == ctx.message.author.id:
                await ctx.send(embed=Embed(
                    title=':man_facepalming: No... That\'s not how mafia works',
                    description='If you want to leave, do this, but don\'t try to kick yourself, that\'s stupid',
                    color=random_color()
                ))

            # User is trying to ban guild owner
            elif user.id == ctx.guild.owner.id:
                await ctx.send(embed=Embed(
                    title=':oncoming_police_car: Wait, that\'s illegal',
                    description='You can\'t kick the police officer',
                    color=random_color()
                ))

            # User is trying to ban the bot
            elif user.id == self.bot.user.id:
                await ctx.send(embed=Embed(
                    title=':face_with_symbols_over_mouth: NO',
                    description='I won\'t leave this guild even if you want to',
                    color=random_color()
                ))

            # No errors
            else:
                await ctx.send(embed=Embed(
                    title=f':boot: I\'m kicking {get(ctx.guild.members, id=user.id)} out',
                    description='(Just kidding, I\'m still in development)',
                    color=random_color()
                ))
                # TODO - enable kicking

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            status = 'You don\'t have **kick** permissions!'

        elif isinstance(error, BotMissingPermissions):
            status = 'I don\' have **kick** permissions!'

        elif isinstance(error, UserNotFound):
            status = 'User not found!'

        else:
            status = 'Unknown error has occurred!'
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)

        await ctx.send(embed=Embed(
            title=':rolling_eyes: Whoops!',
            description=status,
            color=random_color()
        ))

    @Cog.listener()
    async def on_message(self, message):
        if not message.channel.is_nsfw():
            words = message.content.split()
            for word in words:
                if word in bad_words:
                    try:
                        await message.delete()
                        await message.channel.send(embed=Embed(
                            title=f':zipper_mouth: {message.author.display_name}, watch your language!',
                            color=random_color()
                        ))
                    except Forbidden:
                        await message.channel.send(embed=Embed(
                            title=':rolling_eyes: Whoops!',
                            description='Someone has written *bad word* but I don\' have **manage messages** '
                                        'permissions!',
                            color=random_color()
                        ))


def setup(bot):
    bot.add_cog(Admin(bot))
