# -*- coding: utf-8 -*-
from builtins import BaseException
from logging import basicConfig, INFO

from discord import Status, Game, Member
from discord.ext.commands import Bot, Context

from enigma.settings import general_settings, debug_settings
from enigma.utils.debug import debug_message, debug_embed

basicConfig(level=INFO)

bot = Bot(
    command_prefix='>',
    case_insensitive=False,
    owner_id=general_settings['owner_id'],
    description='General purpose bot',
)


@bot.event
async def on_ready():
    # Output login
    print('Logged on as: {0} ({0.id})'.format(bot.user))

    # Change presence
    status = Status.online
    game = Game(name='Cracking enigma codes. | ETA: 8y 23d 42m 18s')
    await bot.change_presence(status=status, activity=game)

    # Logging errors to specific channel
    # noinspection PyShadowingNames
    async def debug_log(ctx: Context = None, e: BaseException = None, member: Member = None):
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

    # Load cogs
    cogs = (
        'enigma.cogs.admin',
        'enigma.cogs.basics',
        'enigma.cogs.profiles',
        'enigma.cogs.stats'
    )
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(f'Loaded: {cog}')
        except BaseException as e:
            await debug_log(e=e)
            print(f'Can\'t load: {cog}')


# Start the bot
bot.run(general_settings['bot_token'])
