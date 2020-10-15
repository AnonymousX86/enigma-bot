# -*- coding: utf-8 -*-
from asyncio import TimeoutError as WaitTimeout
from typing import List, Union

from discord import Embed, Forbidden, TextChannel, NotFound
from discord.ext.commands import Cog, command, Context

from enigma.utils.colors import random_color
from enigma.utils.database import create_giveaway, get_giveaway_from_message, delete_giveaway
from enigma.utils.exceptions import DatabaseError
from enigma.utils.strings import number_suffix


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='giveaway',
        brief='Initiates a giveaway',
        help='Available options:'
             '- create, start; with argument <channel>'
             '- delete, stop; with argument <message ID>',
        usage='<option> <arg>',
        aliases=['ga']
    )
    async def giveaway(self, ctx: Context, option: str = '', arg: Union[TextChannel, int] = None):
        if not option:
            await ctx.send(embed=Embed(
                title=':x: Please specify an option',
                color=random_color()
            ))
        else:
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            if option in ['create', 'start']:
                if not arg:
                    await ctx.send(embed=Embed(
                        title=':x: Missing channel',
                        color=random_color()
                    ))
                elif type(arg) is not TextChannel:
                    await ctx.send(embed=Embed(
                        title=':x: Bad channel format',
                        color=random_color()
                    ))
                else:
                    perms = arg.permissions_for(ctx.guild.get_member(self.bot.user.id))
                    if not perms.read_messages:
                        await ctx.send(embed=Embed(
                            title=':x: I can\'s see that channel'
                        ))

                    elif not perms.send_messages:
                        await ctx.send(embed=Embed(
                            title=':x: I can\'s send messages to that channel'
                        ))

                    else:
                        channel_msg = f'Final message will be sent to {arg.mention}.\n'

                        msg = await ctx.send(embed=Embed(
                            title='Create giveaway',
                            description=f'{channel_msg}'
                                        f'Here will be displayed items added to giveaway.',
                            color=random_color()
                        ).set_footer(
                            text=f'Listening to {ctx.author.display_name}'
                        ))

                        things: List[List[str, str]] = []
                        description = ''
                        index = 0

                        info = await ctx.send(embed=Embed(
                            title='Preparing...',
                            color=random_color()
                        ))

                        while True:
                            index += 1
                            await info.edit(embed=Embed(
                                title=f':name_badge: {index}{number_suffix(index)} item name...',
                                color=random_color()
                            ))
                            try:
                                response_1 = await self.bot.wait_for('message', check=check, timeout=30)
                            except WaitTimeout:
                                await info.edit(embed=Embed(
                                    title=':x: Timed out',
                                    color=random_color()
                                ))
                                return
                            else:
                                if response_1.content.lower() in ['stop', 'end', 'x']:
                                    await response_1.delete()
                                    if len(things) == 0:
                                        await info.edit(embed=Embed(
                                            title=':x: Too few things',
                                            color=random_color()
                                        ))
                                        return
                                    break
                                await info.edit(embed=Embed(
                                    title=f':1234: {index}{number_suffix(index)} item quantity...',
                                    color=random_color()
                                ))
                                try:
                                    response_2 = await self.bot.wait_for('message', check=check, timeout=10)
                                except WaitTimeout:
                                    await info.edit(embed=Embed(
                                        title=':x: Timed out',
                                        color=random_color()
                                    ))
                                    try:
                                        await response_1.delete()
                                    except Forbidden:
                                        pass
                                    return
                                else:
                                    try:
                                        q = int(response_2.content)
                                        if q < 1:
                                            raise ValueError
                                    except ValueError:
                                        await info.edit(embed=Embed(
                                            title=':x: Bad format, quantity must be a number and higher than 0',
                                            color=random_color()
                                        ))
                                        try:
                                            await response_1.delete()
                                            await response_2.delete()
                                        except Forbidden:
                                            pass
                                        return

                                    # Creating message body
                                    things.append([response_1.content, response_2.content])
                                    description = ''
                                    for set_ in things:
                                        description += '{0[0]} x{0[1]}\n'.format(set_)

                                    await msg.edit(embed=Embed(
                                        title='Create giveaway',
                                        description=channel_msg+description,
                                        color=random_color()
                                    ).set_footer(
                                        text=f'Listening to {ctx.author.display_name}'
                                    ))
                                    try:
                                        await response_1.delete()
                                        await response_2.delete()
                                    except Forbidden:
                                        pass

                        await info.delete()
                        await msg.edit(embed=Embed(
                            title='Done!',
                            description=channel_msg+description,
                            color=random_color()
                        ).set_footer(
                            text=f'Created by {ctx.author.display_name}'
                        ))
                        try:
                            new_g = await arg.send(embed=Embed(
                                title=':gift: Giveaway!',
                                color=random_color()
                            ).add_field(
                                name='\u200b',
                                value=description,
                                inline=False
                            ).add_field(
                                name='\u200b',
                                value='React with `📝` to participate!',
                                inline=False
                            ))
                        except Forbidden:
                            await ctx.send(embed=Embed(
                                title=f':x: I have no permissions to send message in {arg.mention}',
                                color=random_color()
                            ))
                        else:
                            try:
                                await new_g.add_reaction(emoji='📝')
                            except Forbidden:
                                await ctx.send(embed=Embed(
                                    title=f':x: I can\'t add emoji to the message in {arg.mention}',
                                    color=random_color()
                                ))
                            else:
                                create_giveaway(new_g.id, ctx.guild.id, data=str(things))
            elif option in ['delete', 'stop']:
                if len(str(arg)) != 18:
                    await ctx.send(embed=Embed(
                        title=':x: Bad ID format',
                        color=random_color()
                    ))
                else:
                    giveaway = get_giveaway_from_message(arg)
                    if giveaway is None:
                        await ctx.send(embed=Embed(
                            title=':x: Giveaway do not exists',
                            color=random_color()
                        ))
                    elif giveaway.guild_id != ctx.guild.id:
                        await ctx.send(embed=Embed(
                            title=':x: This giveaway do not belongs to this guild',
                            color=random_color()
                        ))
                    else:
                        info = await ctx.send(embed=Embed(
                            title=':hourglass_flowing_sand: Please wait...',
                            color=random_color()
                        ))
                        giveaway_message = None
                        for channel in ctx.guild.text_channels:
                            try:
                                giveaway_message = await channel.fetch_message(arg)
                            except NotFound:
                                pass
                            else:
                                break
                        if giveaway_message is None:
                            await info.edit(embed=Embed(
                                title=':x: Message not found',
                                description='Giveaway exists but its message was probably removed,'
                                            ' so I\'m removing the giveaway.',
                                color=random_color()
                            ))
                            if not delete_giveaway(message_id=arg):
                                await self.bot.debug_log(
                                    ctx=ctx, e=DatabaseError(f'Unable to delete giveaway with message ID {arg}')
                                )
                        else:
                            await info.edit(embed=Embed(
                                title=':page_with_curl: Message found',
                                description=f'Link: <{giveaway_message.jump_url}>',
                                color=random_color()
                            ))
                            # TODO - Choosing winners
            else:
                await ctx.send(embed=Embed(
                    title=':x: Invalid option',
                    color=random_color()
                ))


def setup(bot):
    bot.add_cog(Fun(bot))
