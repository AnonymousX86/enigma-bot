# -*- coding: utf-8 -*-
from logging import basicConfig, getLogger

from discord import Status, Game, Member, Intents, Guild
from discord.ext.commands import Bot, Context, CommandNotFound, MissingPermissions, BotMissingPermissions, \
    CommandOnCooldown, UserNotFound, DisabledCommand
from dotenv import load_dotenv, find_dotenv
from rich.logging import RichHandler

from enigma.emebds.core import ErrorEmbed
from enigma.emebds.errors import DebugEmbed
from enigma.emebds.misc import JoinGuildEmbed, OnlineEmbed, RemoveGuildEmbed, ConnectionChangedEmbed
from enigma.settings import debug_channel_id, bot_version, system_channel_id, in_production, bot_token
from enigma.utils.database import check_connection


async def update_presence():
    status = Status.online
    activity = Game(name='Enigma codes')
    await bot.change_presence(status=status, activity=activity)


# noinspection PyShadowingNames
async def debug_log(ctx: Context = None, e: Exception = None, member: Member = None):
    if ch := bot.debug_channel:
        await ch.send(
            embed=DebugEmbed(
                author=bot.get_user(bot.owner_id),
                ctx=ctx,
                e=e,
                member=member
            )
        )


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    # noinspection PyArgumentList
    basicConfig(
        level='INFO',
        format='%(message)s',
        datefmt='[%x]',
        handlers=[RichHandler()]
    )
    getLogger('sqlalchemy.engine').setLevel('WARNING')
    log = getLogger('rich')
    bot = Bot(
        command_prefix='>',
        case_insensitive=False,
        owner_id=309270832683679745,
        description='General purpose bot',
        help_command=None,
        intents=Intents(
            guilds=True,
            members=True,
            bans=True,
            guild_messages=True
        )
    )
    bot.system_channel = None
    bot.debug_channel = None
    bot.owner = None


    @bot.event
    async def on_ready():
        # Find system channel
        system_channel = await bot.fetch_channel(system_channel_id())
        if not system_channel:
            log.error('No system channel found!')
        else:
            bot.system_channel = system_channel
        bot_owner = await bot.fetch_user(bot.owner_id)
        # Find debug channel
        debug_channel = await bot.fetch_channel(debug_channel_id())
        if not debug_channel:
            log.error('No debug channel found!')
        else:
            bot.debug_channel = debug_channel
        # Find bot owner
        if not bot_owner:
            log.error('No bot owner found!')
        else:
            bot.owner = bot_owner
        # Post login things
        log.info(f'Logged on as: {bot.user}')
        guilds = len(bot.guilds)
        log.info(f'Connected guilds: {guilds}')
        await update_presence()
        bot.debug_log = debug_log
        bot.version = bot_version()
        loaded = 0
        for cog in (f'enigma.cogs.{name}' for name in (
                'admin',
                'basics',
                'fun',
                'game_seeker',
                'profiles',
                'utilities'
        )):
            try:
                bot.load_extension(cog)
                log.debug(f'Loaded: {cog}')
                loaded += 1
            except Exception as e:
                await debug_log(e=e)
                log.critical(f'Failed loading "{cog}", details: {e}')
        log.info(f'Loaded cogs: {loaded}')

        log.info('Database connection OK') if check_connection() else log.critical(f'Failed to connect to database')

        log.info('On ready - done!')

        if ch := system_channel:
            await ch.send(embed=OnlineEmbed(author=bot_owner))


    @bot.event
    async def on_connect():
        st = ':large_blue_diamond: Connected to Discord'
        log.info(st)
        if ch := bot.system_channel:
            await ch.send(embed=ConnectionChangedEmbed(
                author=bot.owner,
                title=f' {st}'
            ))


    @bot.event
    async def on_disconnect():
        st = ':large_orange_diamond: Disconnected from Discord'
        log.info(st)
        if ch := bot.system_channel:
            await ch.send(embed=ConnectionChangedEmbed(
                author=bot.owner,
                title=f' {st}'
            ))


    @bot.event
    async def on_resumed():
        st = ':arrows_counterclockwise: Resumed to Discord'
        log.info(st)
        if ch := bot.system_channel:
            await ch.send(embed=ConnectionChangedEmbed(
                author=bot.owner,
                title=f' {st}'
            ))


    @bot.event
    async def on_guild_join(guild: Guild):
        log.info(f'Joined guild: {str(guild)}')
        await update_presence()
        if ch := bot.system_channel:
            await ch.send(embed=JoinGuildEmbed(
                author=bot.owner,
                guild=guild
            ))


    @bot.event
    async def on_guild_remove(guild: Guild):
        log.info(f'Removed from guild: {str(guild)}')
        await update_presence()
        if ch := bot.system_channel:
            await ch.send(embed=RemoveGuildEmbed(
                author=bot.owner,
                guild=guild
            ))


    @bot.event
    async def on_command_error(ctx: Context, error: Exception):
        log.debug('Event "on_command_error" registered')
        if isinstance(error, CommandNotFound):
            if in_production():
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':x: Command not found',
                    description=f'There is no command named `{ctx.message.content[1:].split(" ")[0]}`.'
                                f' Check available commands with `>help`.'
                ))
            else:
                log.info(f'Undefined action "{ctx.message.content}"')
        elif isinstance(error, MissingPermissions):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Missing permissions',
                description=f'You do not have those permissions:```\n{", ".join(error.missing_perms).upper()}\n```'
            ))
        elif isinstance(error, BotMissingPermissions):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Missing permissions',
                description=f'Bot does not have those permissions:```\n{", ".join(error.missing_perms).upper()}\n```'
            ))
        elif isinstance(error, UserNotFound):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: User not found',
                description='Please make sure that you have passed right name or ID.\n'
                            'If you are looking for a server member,  it is better to use @mention.'
            ))
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Command is on cooldown',
                description='Please try again in a minute.'
            ))
        elif isinstance(error, DisabledCommand):
            if in_production():
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':x: Command is disabled'
                ))
        else:
            await debug_log(ctx=ctx, e=error, member=ctx.author)
            raise error


    bot.run(bot_token())
