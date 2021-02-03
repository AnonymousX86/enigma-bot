# -*- coding: utf-8 -*-
from asyncio import sleep

from discord import Embed, Member, NotFound, HTTPException
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, MissingPermissions, \
    BotMissingPermissions, UserNotFound, Context, cooldown, BucketType, CommandOnCooldown
from discord.utils import get

from enigma.settings import in_production
from enigma.utils.colors import random_color
from enigma.utils.emebds.core import ErrorEmbed, SuccessEmbed
from enigma.utils.emebds.errors import CooldownEmbed
from enigma.utils.emebds.misc import PleaseWaitEmbed


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
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.author)
            raise error

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
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.author)
            raise error

        await ctx.send(embed=Embed(
            title=':rolling_eyes: Whoops!',
            description=status,
            color=random_color()
        ))

    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    @cooldown(1, 30, BucketType.guild)
    @command(
        name='prune',
        biref='Clears messages',
        descriptions='Clears last X messages in current channel',
        help='You can delete 20 messages at once.',
        usage='[amount]',
        enabled=in_production()
    )
    async def prune(self, ctx: Context, amount: int = 0):
        if amount < 1:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Arguments error',
                description='Please provide amount of messages to prune.'
            ))
        elif amount > 20:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Too many messages',
                description='Please provide amount less than 20.'
            ))
        deleted = 0
        msg = await ctx.send(embed=PleaseWaitEmbed(author=ctx.author))
        await ctx.message.delete()
        async for m in ctx.channel.history(limit=amount + 1):
            if m.id == msg.id:
                continue
            try:
                await m.delete()
            except NotFound or HTTPException:
                pass
            else:
                deleted += 1
        if deleted < 1:
            await msg.edit(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Deleting failed'
            ))
        await msg.edit(embed=SuccessEmbed(
            author=ctx.author,
            title=f':wastebasket: Successfully deleted {deleted} message{"s" if deleted > 1 else ""}.'
        ))
        await sleep(3)
        await msg.delete()

    @prune.error
    async def prune_error(self, ctx: Context, error: Exception):
        if isinstance(error, MissingPermissions):
            st = 'You don\'t have **manage messages** permissions!'
        elif isinstance(error, BotMissingPermissions):
            st = 'I don\'t have **manage messages** or **read message history** permissions!'
        elif isinstance(error, CommandOnCooldown):
            return await ctx.send(embed=CooldownEmbed(author=ctx.author))
        else:
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.author)
            raise error
        await ctx.send(embed=ErrorEmbed(
            author=ctx.author,
            title=':x: Whoops!',
            description=st
        ))

    # TODO - Logging system


def setup(bot):
    bot.add_cog(Admin(bot))
