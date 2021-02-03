# -*- coding: utf-8 -*-
from logging import basicConfig, INFO, getLogger

from discord import Status, Game, Member, Intents, Guild
from discord.ext.commands import Bot, Context
from rich.logging import RichHandler

from enigma.settings import general_settings, debug_settings, version
from enigma.utils.debug import debug_message, debug_embed
from enigma.utils.emebds.misc import JoinGuildEmbed

# noinspection PyArgumentList
basicConfig(
    level='INFO',
    format='%(message)s',
    datefmt='[%x]',
    handlers=[RichHandler()]
)
getLogger('sqlalchemy.engine').setLevel(INFO)
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


async def update_presence(bot_: Bot):
    status = Status.online
    game = Game(name=f'Cracking enigma codes in {len(bot_.guilds)} servers')
    await bot_.change_presence(status=status, activity=game)


@bot.event
async def on_ready():
    # Output login
    log.info('Logged on as: {0} ({0.id})'.format(bot.user))
    guilds = len(bot.guilds)
    log.info('Guilds count: ', guilds)

    # Change presence
    await update_presence(bot)

    # Logging errors to specific channel
    # noinspection PyShadowingNames
    async def debug_log(ctx: Context = None, e: Exception = None, member: Member = None):
        debug_channel = bot.get_channel(debug_settings['channel'])
        await debug_channel.send(
            debug_message(),
            embed=debug_embed(
                ctx=ctx,
                e=e,
                member=member
            )
        )

    bot.debug_log = debug_log

    # Custom values
    bot.version = version

    # Load cogs
    cogs = (f'enigma.cogs.{name}' for name in (
        'admin',
        'basics',
        'fun',
        'game_seeker',
        'profiles',
    ))
    for cog in cogs:
        try:
            bot.load_extension(cog)
            log.debug(f'Loaded: {cog}')
        except Exception as e:
            await debug_log(e=e)
            log.warning(f'Can\'t load: {cog}')

    log.info('On ready - done!')


@bot.event
async def on_guild_join(guild: Guild):
    log.info(f'Joined guild: {str(guild)}')
    await update_presence(bot)
    await bot.get_channel(debug_settings['channel']).send(embed=JoinGuildEmbed(
        author=bot.get_user(bot.owner_id),
        guild=guild
    ))


@bot.event
async def on_guild_remove(guild: Guild):
    log.info(f'Removed from guild: {str(guild)}')
    await update_presence(bot)


# Start the bot
bot.run(general_settings['bot_token'])
