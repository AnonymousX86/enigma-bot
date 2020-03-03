# -*- coding: utf-8 -*-
from logging import basicConfig, INFO
from .settings import BOT_TOKEN, OWNER_ID

from discord.ext.commands import Bot
from discord import Status, Game


basicConfig(level=INFO)

bot = Bot(
    command_prefix='>',
    case_insensitive=False,
    owner_id=OWNER_ID,
    description='General purpose bot',
)


@bot.event
async def on_ready():
    # Output login
    print('Logged on as: {0} ({0.id})'.format(bot.user))

    # Change presence
    status = Status.online
    game = Game(name='Tic Tac Toe with myself')
    await bot.change_presence(status=status, activity=game, afk=False)

    # Load cogs
    bot.load_extension('enigma.cogs.basics')

    return


# Start the bot
bot.run(BOT_TOKEN)
