# -*- coding: utf-8 -*-
from discord import Embed, Member
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, MissingPermissions, \
    BotMissingPermissions, UserNotFound, Context
from discord.utils import get

from enigma.settings import in_production
from enigma.utils.colors import random_color
from enigma.utils.emebds.core import ErrorEmbed, SuccessEmbed


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='ban',
        brief='Bans user',
        description='You can provide user ID or mention someone',
        usage='<user>',
        enabled=in_production()
    )
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def ban(self, ctx: Context, member: Member = None, reason: str = None):
        # No user provided
        if not member:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':face_with_raised_eyebrow: Who do I need to ban?',
                description='You\'ve not provided a victim',
            ))

        else:
            # User is trying to ban yourself
            if member.id == ctx.message.author.id:
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':clown: You can\'t ban yourself',
                    description='Ask someone to help you commit sepuku or something...',
                ))

            # User is trying to ban guild owner
            elif member.id == ctx.guild.owner.id:
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':crown: You can\'t ban guild owner',
                    description='He\'s the almighty one, sorry'
                ))

            # User is trying to ban the bot
            elif member.id == self.bot.user.id:
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':zany_face: I can\'t ban myself',
                    description='Even if I would I can\'t, sorry'
                ))

            # No errors
            else:
                await ctx.send(embed=SuccessEmbed(
                    author=ctx.author,
                    title=f':hammer: Banning {get(ctx.guild.members, id=member.id)}',
                    description=f'Reason:```\n{str(reason)}\n```'
                ))
                await member.ban(reason=reason)

    @ban.error
    async def ban_error(self, ctx: Context, error: Exception):
        if isinstance(error, MissingPermissions):
            status = 'You don\'t have **ban** permissions!'

        elif isinstance(error, BotMissingPermissions):
            status = 'I don\' have **ban** permissions!'

        elif isinstance(error, UserNotFound):
            status = 'User not found!'

        else:
            status = 'Unknown error has occurred!'
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.author)

        await ctx.send(embed=ErrorEmbed(
            author=ctx.author,
            title=':rolling_eyes: Whoops!',
            description=status
        ))

    # TODO - unban command

    @command(
        name='kick',
        brief='Kicks user',
        description='You can provide user ID or mention someone',
        usage='<user>',
        enabled=in_production()
    )
    @has_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: Member = None, reason: str = None):
        em = ErrorEmbed

        # No user provided
        if not member:
            st = (
                ':cowboy: Who do I need to kick round the clock?',
                'You\'ve not provided a victim'
            )

        # User is trying to ban yourself
        elif member.id == ctx.author.id:
            st = (
                ':man_facepalming: No... That\'s not how mafia works',
                'If you want to leave, do this, but don\'t try to kick yourself, that\'s stupid'
            )

        # User is trying to ban guild owner
        elif member.id == ctx.guild.owner.id:
            st = (
                ':oncoming_police_car: Wait, that\'s illegal',
                'You can\'t kick the police officer'
            )

        # User is trying to ban the bot
        elif member.id == self.bot.user.id:
            st = (
                ':face_with_symbols_over_mouth: NO',
                'I won\'t leave this guild even if you want to'
            )

        # No errors
        else:
            em = SuccessEmbed
            st = (
                f':boot: I\'m kicking {get(ctx.guild.members, id=member.id)} out',
                f'Reason:\n```{str(reason)}\n```'
            )
            await member.kick(reason=reason)

        await ctx.send(embed=em(
            author=ctx.author,
            title=st[0],
            description=st[1]
        ))

    @kick.error
    async def kick_error(self, ctx: Context, error: Exception):
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

    # TODO - Logging system


def setup(bot):
    bot.add_cog(Admin(bot))
