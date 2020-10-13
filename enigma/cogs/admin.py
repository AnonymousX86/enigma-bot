# -*- coding: utf-8 -*-
import asyncio
from builtins import BaseException

from discord import Embed
from discord.errors import Forbidden  # If bot has no permissions for deleting message
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions, MissingPermissions, \
    BotMissingPermissions
from discord.utils import get

from enigma.settings import general_settings
from enigma.src.bad_words import bad_words
from enigma.utils.colors import random_color
from enigma.utils.databases import postgre_connect, cache_client
from enigma.utils.searching import find_user


class Admin(Cog):
    """
    Admin commands and moderation tools

    Commands:
        ban: bans member
        kick: kicks member

    Listeners:
        event on_message: looking for bad words
    """

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
    async def ban(self, ctx, user_id=None):
        # No user provided
        if user_id is None:
            await ctx.send(embed=Embed(
                title=':face_with_raised_eyebrow: Who do I need to ban?',
                description='You\'ve not provided a victim',
                color=random_color()
            ))
            return

        else:
            user_id = find_user(user_id)

            # The user cannot be found
            if user_id is None:
                await ctx.send(embed=Embed(
                    title=':man_detective: I can\' find that guy',
                    description='Try asking local mafia for help',
                    color=random_color()
                ))
                return

            # Now target user is found, checking if...
            else:
                # User is trying to ban yourself
                if user_id == ctx.message.author.id:
                    await ctx.send(embed=Embed(
                        title=':clown: You can\'t ban yourself',
                        description='Ask someone to help you commit sepuku or something...',
                        color=random_color()
                    ))
                    return

                # User is trying to ban guild owner
                elif user_id == ctx.guild.owner.id:
                    await ctx.send(embed=Embed(
                        title=':crown: You can\'t ban guild owner',
                        description='He\'s the almighty one, sorry',
                        color=random_color()
                    ))
                    return

                # User is trying to ban the bot
                elif user_id == self.bot.user.id:
                    await ctx.send(embed=Embed(
                        title=':zany_face: I can\'t ban myself',
                        description='Even if I would I can\'t, sorry',
                        color=random_color()
                    ))
                    return

                # No errors
                else:
                    await ctx.send(embed=Embed(
                        title=f':hammer: Banning {get(ctx.guild.members, id=user_id)}',
                        description='(Just kidding, I\'m still in development)',
                        color=random_color()
                    ))
                    return
                    # TODO - enable banning

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            status = 'You don\'t have **ban** permissions!'

        elif isinstance(error, BotMissingPermissions):
            status = 'I don\' have **ban** permissions!'

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
    async def kick(self, ctx, user_id=None):
        # No user provided
        if user_id is None:
            await ctx.send(embed=Embed(
                title=':cowboy: Who do I need to kick round the clock?',
                description='You\'ve not provided a victim',
                color=random_color()
            ))

        else:
            user_id = find_user(user_id)

            # The user cannot be found
            if user_id is None:
                await ctx.send(embed=Embed(
                    title=':tired_face: Sorry...',
                    description='After 1337ms of work I can\'t find that guy',
                    color=random_color()
                ))

            # Now target user is found, checking if...
            else:
                # User is trying to ban yourself
                if user_id == ctx.message.author.id:
                    await ctx.send(embed=Embed(
                        title=':man_facepalming: No... That\'s not how mafia works',
                        description='If you want to leave, do this, but don\'t try to kick yourself, that\'s stupid',
                        color=random_color()
                    ))

                # User is trying to ban guild owner
                elif user_id == ctx.guild.owner.id:
                    await ctx.send(embed=Embed(
                        title=':oncoming_police_car: Wait, that\'s illegal',
                        description='You can\'t kick the police officer',
                        color=random_color()
                    ))

                # User is trying to ban the bot
                elif user_id == self.bot.user.id:
                    await ctx.send(embed=Embed(
                        title=':face_with_symbols_over_mouth: NO',
                        description='I won\'t leave this guild even if you want to',
                        color=random_color()
                    ))

                # No errors
                else:
                    await ctx.send(embed=Embed(
                        title=f':boot: I\'m kicking {get(ctx.guild.members, id=user_id)} a\\*s',
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

        else:
            status = 'Unknown error has occurred!'
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)

        await ctx.send(embed=Embed(
            title=':rolling_eyes: Whoops!',
            description=status,
            color=random_color()
        ))

    @command(
        name='mute',
        brief='Mutes user',
        description='You can provide user ID or mention someone',
        usage='<user>'
    )
    async def mute(self, ctx, user_id=None):
        # Config mode
        if user_id is not None and user_id.lower() == 'config':
            msg = await ctx.send(embed=Embed(
                title=':gear: Please send here role ID...',
                color=random_color()
            ))

            # Checking if response in same channel and from the same member
            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            # Now user have to send mute role ID
            try:
                response = await self.bot.wait_for('message', check=check, timeout=20.0)

            # After 20 seconds bot stops listening
            except asyncio.TimeoutError:
                await msg.edit(embed=Embed(
                    title=':hourglass: Timed out',
                    description='Try typing faster next time',
                    color=random_color()
                ))

            # User sent some data (not sure what it is)
            else:
                # Nice looking output
                await msg.edit(embed=Embed(
                    title=':gear: Working on it...',
                    color=random_color()
                ))

                # Arg is probably an ID
                if len(response.content) == 18:
                    # Trying to convert arg to integer
                    try:
                        new_mute_role_id = int(response.content)

                    # Provided text that's not ID
                    except TypeError:
                        await msg.edit(embed=Embed(
                            title=':no_entry: Bad ID format',
                            color=random_color()
                        ))
                        return

                    finally:
                        await response.delete()

                    # Searching if that role exists in guild
                    new_mute_role = ctx.guild.get_role(new_mute_role_id)

                    # Role doesn't exist
                    if new_mute_role is None:
                        await msg.edit(embed=Embed(
                            title=':rolling_eyes: Uhh...',
                            description=f'I can\'t find role with ID: `{new_mute_role_id}`',
                            color=random_color()
                        ))

                    # Role exists
                    else:
                        try:
                            db = postgre_connect()
                            c = db.cursor()

                            # Trying if guild is in database
                            c.execute(
                                'SELECT * FROM guilds WHERE guild_id = %s::bigint;',
                                (
                                    int(ctx.guild.id),
                                )
                            )
                            if c.fetchone() is None:
                                c.execute(
                                    'INSERT INTO guilds (guild_id) VALUES (%s::bigint);',
                                    (
                                        int(ctx.guild.id),
                                    )
                                )

                            # Now guild is in database for sure
                            c.execute(
                                'UPDATE guilds SET mute_role_id = %s::bigint WHERE guild_id = %s::bigint;',
                                (
                                    int(new_mute_role_id),
                                    int(ctx.guild.id)
                                )
                            )

                            # Saving data to database
                            db.commit()
                            c.close()
                            db.close()

                            # Saving data to cache
                            client = cache_client()
                            client.set(f'{ctx.guild.id}_mute_role_id', new_mute_role_id, time=600)

                            await msg.edit(embed=Embed(
                                title=':zipper_mouth: Mute role set',
                                description=f'Now it\'s `@{new_mute_role}`',
                                color=random_color()
                            ))

                        # Something bad happened while trying to save role ID to database
                        except BaseException as e:
                            await self.bot.debug_log(ctx=ctx, e=e)
                            await msg.edit(embed=Embed(
                                title=':no_entry: Can\'t set mute role',
                                color=random_color()
                            ))

                # User provided something else than standard Discord ID (18 position integer)
                else:
                    await msg.edit(embed=Embed(
                        title=':no_entry: Bad ID format'
                    ))

        # Muting mode
        else:
            # Find mute role ID
            client = cache_client()
            result = client.get(f'{ctx.guild.id}_mute_role_id')
            if result is None:
                db = postgre_connect()
                c = db.cursor()
                c.execute(
                    'SELECT mute_role_id FROM guilds WHERE guild_id = %s::bigint;',
                    (
                        int(ctx.guild.id),
                    )
                )
                result = c.fetchone()
                db.close()

            # Can't find mute role
            if result is None:
                await ctx.send(embed=Embed(
                    title=':gear: No mute role has been specified',
                    description='Please run `mute config` to add one',
                    color=random_color()
                ))
                return

            # Mute role ID is found
            else:
                client.set(f'{ctx.guild.id}_mute_role_id', result, time=600)
                # No user provided
                if user_id is None:
                    await ctx.send(embed=Embed(
                        title=':gun: You don\' specified who do I need to shut down',
                        description='You\'ve not provided a victim',
                        color=random_color()
                    ))
                    return

                else:
                    user_id = find_user(user_id)

                    # The user cannot be found
                    if user_id is None:
                        await ctx.send(embed=Embed(
                            title=':face_with_monocle: Who?',
                            description='I don\'t know about who are you talking about',
                            color=random_color()
                        ))
                        return

                    # Now target user is found, checking if...
                    else:
                        # User is trying to ban yourself
                        if user_id == ctx.message.author.id:
                            await ctx.send(embed=Embed(
                                title=':zipper_mouth: Don\'t do that',
                                description='Just be quiet',
                                color=random_color()
                            ))
                            return

                        # User is trying to ban guild owner
                        elif user_id == ctx.guild.owner.id:
                            await ctx.send(embed=Embed(
                                title=':moyai: Nope',
                                description='You can\'t do that to the ***O W N E R***',
                                color=random_color()
                            ))
                            return

                        # User is trying to ban the bot
                        elif user_id == self.bot.user.id:
                            await ctx.send(embed=Embed(
                                title=':worried: Hey...',
                                description='I love talking, okay?',
                                color=random_color()
                            ))
                            return

                        # No errors
                        else:
                            await ctx.send(embed=Embed(
                                title=f':shushing_face: I\'m muting {get(ctx.guild.members, id=user_id)}',
                                description='(Just kidding, I\'m still in development)',
                                color=random_color()
                            ))
                            return

    # TODO - unmute command

    @Cog.listener()
    async def on_message(self, message):
        if message.channel.is_nsfw() is False:
            words = message.content.split()
            for word in words:
                if word in bad_words:
                    try:
                        await message.delete()
                        await message.channel.send(embed=Embed(
                            title=f':zipper_mouth: {message.author.display_name}, watch your language!',
                            description=f'You think it\'s a bug? Report this to <@!{general_settings["owner_id"]}>',
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
