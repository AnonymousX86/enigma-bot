# -*- coding: utf-8 -*-
from builtins import BaseException
from datetime import datetime as d

from discord import Embed
from discord.ext.commands import command, Cog, has_permissions, MissingPermissions
from discord.utils import get as discord_find

from enigma.utils.colors import random_color
from enigma.utils.databases import *
from enigma.utils.datetime import utc_to_local, execute_time
from enigma.utils.exceptions import NoError
from enigma.utils.strings import chars


class Basics(Cog):
    """
    Basic commands

    Commands:
        error: raises "NoError" - testing purpose
        ping: checks bot latency based on difference between "await ctx.send()" and command "created_at" timestamp
        query: gets all data from "users" database - testing purpose
        flushall: clears cache
    """

    def __init__(self, bot):
        self.bot = bot

    # TODO help command
    # @command(
    #     name='help',
    #     description='Shows this message.\n'
    #                 '`<...>` - Needed argument.\n'
    #                 '`[...]` - Optional argument.\n'
    #                 '`<..|..>` - Choose 1 needed argument from many.\n'
    #                 '`[..|..]` - Choose 1 optional argument from many.\n',
    #     brief='Help command',
    #     usage='[command]',
    #     aliases=['h', ]
    # )
    # async def help(self, ctx, arg: str = ''):
    #     if arg == '':
    #         pass

    @Cog.listener()
    async def on_member_update(self, before, after):
        if str(after.status) == 'offline':
            if before.bot is False:
                db = postgre_connect()
                c = db.cursor()
                try:
                    c.execute(
                        'UPDATE users SET last_seen = %s WHERE user_id = %s;',
                        (
                            d.now().strftime('%Y-%m-%d %H:%M:%S'),
                            int(before.id)
                        )
                    )
                    db.commit()

                    client = cache_client()
                    client.flush_all()

                except BaseException as e:
                    await self.bot.debug_log(e=e, member=before)

                finally:
                    c.close()
                    db.close()

    @command(
        name='error',
        brief='Raises an example error',
        description='Only specific users have access to this command',
        aliases=['err'],
        hidden=True
    )
    @has_permissions(administrator=True)
    async def error_cmd(self, ctx):
        await self.bot.debug_log(ctx=ctx, e=NoError())
        await ctx.send(embed=Embed(
            title=':exclamation: Raised `NoError`',
            description='Bot\'s owner should be notified',
            color=random_color()
        ))

    @error_cmd.error
    async def error_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(embed=Embed(
                title=':man_technologist: You\'re not an IT specialist',
                description='Only those can use this command',
                color=random_color()
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)

    @command(
        name='ping',
        brief='Checks bot latency',
        description='Counts time difference between command execution time and bot\'s response'
    )
    async def ping(self, ctx):
        start_time = d.timestamp(utc_to_local(ctx.message.created_at))
        await ctx.send(embed=Embed(
            title=':ping_pong: Pong!',
            description=f'It took me: {execute_time(start_time)}',
            color=random_color()
        ))
        return

    @command(
        name='query',
        brief='Gets sample data from or into database',
        description='Default mode is `get`, other is `post`',
        aliases=['q'],
        usage='[mode]'
    )
    async def query(self, ctx, mode: str = 'get'):
        """Connect to PostgreSQL database and posts or gets users' data"""
        start_time = d.timestamp(utc_to_local(ctx.message.created_at))
        author_id = int(ctx.message.author.id)

        default_color = random_color()

        post_title_exec = ':outbox_tray: Posting data to database'
        post_title_error = ':no_entry: Cannot **POST** data'
        post_title_done = ':white_check_mark: Posting data done'

        get_title_exec = ':inbox_tray: Getting data from database'
        get_title_error = ':no_entry: Cannot **GET** data'
        get_title_done = ':white_check_mark: Getting data done'

        # Upload data
        if mode == 'post':
            msg = await ctx.send(embed=Embed(
                title=post_title_exec,
                color=default_color
            ))
            db = None
            c = None
            try:
                result: list = query_single_user(author_id)
                db = postgre_connect()
                c = db.cursor()

                # If user is in database they should be updated
                if len(result) > 0:
                    c.execute(
                        'UPDATE users SET last_seen = %s WHERE user_id = %s;',
                        (
                            utc_to_local(ctx.message.created_at).strftime('%Y-%m-%d %H:%M:%S'),
                            author_id
                        )
                    )
                    action = 'Data has been **updated**'

                # If there's no such user in database - insert they then
                else:
                    c.execute(
                        'INSERT INTO users (user_id, last_seen) VALUES (%s, %s);',
                        (
                            author_id,
                            utc_to_local(ctx.message.created_at).strftime('%Y-%m-%d %H:%M:%S')
                        )
                    )
                    action = 'Data has been **inserted**'

                await msg.edit(embed=Embed(
                    title=post_title_done,
                    description=action,
                    color=default_color
                ).set_footer(
                    text=f'Executed in: {execute_time(start_time)}'
                ))
                db.commit()
                db.close()

            except BaseException as e:
                await msg.edit(embed=Embed(
                    title=post_title_error,
                    color=default_color
                ))
                await self.bot.debug_log(ctx=ctx, e=e)

            finally:
                for i in (c, db):
                    if i:
                        i.close()
                try:
                    client = cache_client()
                    if client:
                        client.flush_all()
                except BaseException as e:
                    await self.bot.debug_log(ctx=ctx, e=e)

        # Download data
        elif mode == 'get':
            msg = await ctx.send(embed=Embed(
                title=get_title_exec,
                description='Getting data from cache...',
                color=default_color
            ))
            get_method = None

            # Trying to connect to cache server
            try:
                client = cache_client()
                client.enable_retry_delay(True)
            except BaseException as e:
                await self.bot.debug_log(ctx=ctx, e=e)
                await msg.edit(embed=Embed(
                    title=get_title_exec,
                    description='Can\'t connect to cache service',
                    color=default_color
                ))
                client = None

            result = []

            # When connected to cache server, trying to get data from it
            if client:
                try:
                    # noinspection PyTypeChecker
                    result = client.get('query_get')
                    get_method = 'cache'
                except BaseException as e:
                    await self.bot.debug_log(ctx=ctx, e=e)
                    await msg.edit(embed=Embed(
                        title=get_title_exec,
                        description='Can\'t get data from cache',
                        color=default_color
                    ))

            # Get data from SQL query if there's no data in cache
            if not result:
                await msg.edit(embed=Embed(
                    title=get_title_exec,
                    description='Connecting to SQL database...',
                    color=default_color
                ))

                # Trying to connect to SQL database
                try:
                    result = query_all_users()
                    get_method = 'SQL query'
                    if client is not None:
                        client.set('query_get', result, time=600)
                except BaseException as e:
                    await self.bot.debug_log(ctx=ctx, e=e)
                    await msg.edit(embed=Embed(
                        title=get_title_error,
                        description='Can\'t connect to any data source',
                        color=default_color
                    ))

            # There should be some data, if there's still no data that exception is handled above
            if result:
                data = ''
                for row in result:
                    user_data = {
                        'user_name': f'{discord_find(ctx.guild.members, id=int(row[0]))}',
                        'user_xp': f'{row[1]} XP',
                        'user_cash': f'{row[2]} {chars["bitcoin"]}',
                        'last_seen': f'{row[3]}',
                        'user_massages': f'{row[4]} messages'
                    }

                    for key, value in user_data.items():
                        data += f'- {value} \n'

                    if row != result[-1]:
                        data += '#====================#\n'

                await msg.edit(embed=Embed(
                    title=get_title_done,
                    description=f'```glsl\n'
                                f'{data}'
                                f'```\n'
                                f'Data get from {get_method}',
                    color=default_color
                ).set_footer(
                    text=f'Executed in: {execute_time(start_time)}'
                ))

        # Bad mode specified
        else:
            await ctx.send(embed=Embed(
                title=':no_entry: Bad query mode!',
                description='Use instead `post` or `get` (default)',
                color=default_color
            ))

    @command(
        name='flushall',
        brief='Removes all keys from cache'
    )
    @has_permissions(administrator=True)
    async def flushall(self, ctx):
        try:
            client = cache_client()
            client.flush_all()
            await ctx.send(embed=Embed(
                title=':broom: Flushed cache successfully',
                color=random_color()
            ))
        except BaseException as e:
            await self.bot.debug_log(ctx=ctx, e=e)
            await ctx.send(embed=Embed(
                title=':no_entry: Can\'t flush cache',
                color=random_color()
            ))

    @flushall.error
    async def flushall_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(embed=Embed(
                title=':man_mechanic: Only techs can do that',
                description='Maybe ask one of them to help you?',
                color=random_color()
            ))


def setup(bot):
    bot.add_cog(Basics(bot))
