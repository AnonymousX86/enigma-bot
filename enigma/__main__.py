# -*- coding: utf-8 -*-
from logging import basicConfig, INFO, getLogger

from discord import Status, Game, Member, Intents, Guild
from discord.ext.commands import Bot, Context, CommandNotFound, MissingPermissions, BotMissingPermissions, \
    CommandOnCooldown, UserNotFound, DisabledCommand
from rich.logging import RichHandler

from enigma.settings import general_settings, debug_settings, version, in_production
from enigma.utils.emebds.core import ErrorEmbed
from enigma.utils.emebds.errors import DebugEmbed
from enigma.utils.emebds.misc import JoinGuildEmbed


async def update_presence():
    status = Status.online
    game = Game(name=f'Cracking enigma codes in {len(bot.guilds)} servers')
    await bot.change_presence(status=status, activity=game)


# noinspection PyShadowingNames
async def debug_log(ctx: Context = None, e: Exception = None, member: Member = None):
    debug_channel = bot.get_channel(debug_settings['channel'])
    await debug_channel.send(
        embed=DebugEmbed(
            author=bot.get_user(bot.owner_id),
            ctx=ctx,
            e=e,
            member=member
        )
    )


if __name__ == '__main__':
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
        owner_id=general_settings['owner_id'],
        description='General purpose bot',
        help_command=None,
        intents=Intents(
            guilds=True,
            members=True,
            bans=True,
            guild_messages=True
        )
    )


    @bot.event
    async def on_ready():
        # Output login
        log.info(f'Logged on as: {bot.user}')
        guilds = len(bot.guilds)

        # Change presence
        log.info(f'Connected guilds: {guilds}')
        await update_presence()

        bot.debug_log = debug_log

        # Custom values
        bot.version = version
        loaded = 0
        for cog in (f'enigma.cogs.{name}' for name in (
                'admin',
                'basics',
                'fun',
                'game_seeker',
                'profiles',
        )):
            try:
                bot.load_extension(cog)
                log.debug(f'Loaded: {cog}')
                loaded += 1
            except Exception as e:
                await debug_log(e=e)
                log.critical(f'Failed loading "{cog}", details: {e}')
        log.info(f'Loaded cogs: {loaded}')

        log.info('On ready - done!')


    @bot.event
    async def on_guild_join(guild: Guild):
        log.info(f'Joined guild: {str(guild)}')
        await update_presence()
        await bot.get_channel(debug_settings['channel']).send(embed=JoinGuildEmbed(
            author=bot.get_user(bot.owner_id),
            guild=guild
        ))


    @bot.event
    async def on_guild_remove(guild: Guild):
        log.info(f'Removed from guild: {str(guild)}')
        await update_presence()


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
                title=':x: Command is not cooldown',
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


    bot.run(general_settings['bot_token'])
