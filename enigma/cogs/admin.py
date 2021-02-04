# -*- coding: utf-8 -*-
from discord import Member, NotFound, HTTPException, User
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, Context, cooldown, BucketType
from discord.utils import get

from enigma.settings import in_production
from enigma.utils.emebds.core import ErrorEmbed, SuccessEmbed
from enigma.utils.emebds.misc import PleaseWaitEmbed


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='ban',
        brief='Bans user',
        usage='<user> [reason]',
        enabled=in_production()
    )
    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def ban(self, ctx: Context, member: Member = None, *, reason: str = None):
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
                    title=f':hammer: Banning {get(ctx.guild.members, id=member.id)}'
                ).add_field(
                    name='REASON',
                    value=str(reason)
                ))
                await member.ban(reason=reason)

    @has_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    @command(
        name='unban',
        brief='Unbans user',
        help='Because user of course isn\'t in server, provide user\'s name or ID.',
        uasge='<user> [reason]',
        enabled=not in_production()
    )
    async def unban(self, ctx: Context, user: User = None, *, reason: str = None):
        if not user:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: User not found'
            ))
        else:
            try:
                await ctx.guild.unban(user, reason=reason)
            except HTTPException as e:
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':x: Can\'t unban user'
                ))
                await self.bot.debug_log(ctx=ctx, e=e, user=user)
            else:
                await ctx.send(embed=SuccessEmbed(
                    author=ctx.author,
                    title=':white_check_mark: User unbanned',
                    description=f'**{user.display_name}** now can join back to **{ctx.guild.name}**.'
                ).add_field(
                    name='REASON',
                    value=str(reason)
                ))

    @command(
        name='kick',
        brief='Kicks user',
        description='You can provide user ID or mention someone',
        usage='<user> [reason]',
        enabled=in_production()
    )
    @has_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: Member = None, *, reason: str = None):
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
            await ctx.send(embed=SuccessEmbed(
                author=ctx.author,
                title=f':boot: I\'m kicking {get(ctx.guild.members, id=member.id)} out'
            ).add_field(
                name='REASON',
                value=str(reason)
            ))
            await member.kick(reason=reason)
            return
        await ctx.send(embed=ErrorEmbed(
            author=ctx.author,
            title=st[0],
            description=st[1]
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
        await msg.delete(delay=3.0)

    # TODO - Logging system


def setup(bot):
    bot.add_cog(Admin(bot))
