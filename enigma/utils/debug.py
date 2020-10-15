from datetime import datetime as d

from discord import Embed, Member
from discord.ext.commands import Context

from enigma.settings import general_settings
from enigma.utils.colors import random_color


def debug_message():
    return f'Hey, <@{general_settings["owner_id"]}> I\'ve got a problem... :sweat:\n'


def debug_embed(ctx: Context = None, e: BaseException = None, member: Member = None):
    data = ''
    if ctx is not None:
        data += f'<@{ctx.message.author.id}> raised an error in <#{ctx.channel.id}>.\n\n' \
                f'**[Message Link]({ctx.message.jump_url})**\n\n' \
                f'**MESSAGE INFO:**' \
                '```xl\n' \
                f'Channel ID  - {ctx.channel.id}\n' \
                f'User ID     - {ctx.message.author.id}\n' \
                f'Datetime    - {str(d.now())[:19]}\n' \
                f'```\n' \
                f'**MESSAGE CONTENT:**\n' \
                f'```\n' \
                f'{ctx.message.content}\n' \
                f'```\n'

    if e is not None:
        data += f'**ERROR:**\n' \
                f'```diff\n' \
                f'- {e.__class__.__name__}: {e}\n' \
                f'```'

    if member is not None:
        data += f'Member {member.mention} raised an error.'

    return Embed(description=data, color=random_color())
