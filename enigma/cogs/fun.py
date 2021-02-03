# -*- coding: utf-8 -*-
from ast import literal_eval
from asyncio import TimeoutError as WaitTimeout
from datetime import datetime as d
from json import loads as json_loads
from random import choice, randint
from typing import List, Union, Optional

from discord import Forbidden, TextChannel, NotFound, User, Message
from discord.ext.commands import Cog, command, Context, cooldown, BucketType, CommandOnCooldown, has_permissions, \
    MissingPermissions, CommandInvokeError
from praw import Reddit
from requests import request

from enigma.settings import reddit_settings, in_production, rapidapi_settings
from enigma.utils.colors import random_color
from enigma.utils.database import create_giveaway, get_giveaway_from_message, delete_giveaway
from enigma.utils.emebds.core import ErrorEmbed, InfoEmbed, SuccessEmbed
from enigma.utils.emebds.errors import TimeoutEmbed, CooldownEmbed
from enigma.utils.emebds.misc import PleaseWaitEmbed
from enigma.utils.exceptions import DatabaseError
from enigma.utils.strings import number_suffix


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permissions(manage_guild=True)
    @cooldown(1, 30, BucketType.guild)
    @command(
        name='giveaway',
        brief='Initiates a giveaway',
        help='Available options:\n'
             '- create, start, new;'
             ' with argument <channel>\n'
             '- delete, stop, end;'
             ' with argument <message ID>\n'
             '  Message ID could be found under the giveaway message.\n'
             'Maximum item\'s length is 30 characters and maximum amount is 25.',
        usage='<option> <additional argument> [group result by]',
        aliases=['ga'],
        enabled=in_production()
    )
    async def giveaway(self, ctx: Context, option: str = '', arg1: Union[TextChannel, int] = None):
        if not option:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Please specify an option',
                color=random_color()
            ))
        else:
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            if option in ['create', 'start', 'new']:
                if not arg1:
                    await ctx.send(embed=ErrorEmbed(
                        author=ctx.author,
                        title=':x: Missing channel'
                    ))
                elif type(arg1) is not TextChannel:
                    await ctx.send(embed=ErrorEmbed(
                        author=ctx.author,
                        title=':x: Bad channel format'
                    ))
                else:
                    perms = arg1.permissions_for(ctx.guild.get_member(self.bot.user.id))
                    if not perms.read_messages:
                        await ctx.send(embed=ErrorEmbed(
                            author=ctx.author,
                            title=':x: I can\'s see that channel'
                        ))
                    elif not perms.send_messages:
                        await ctx.send(embed=ErrorEmbed(
                            author=ctx.author,
                            title=':x: I can\'s send messages to that channel'
                        ))
                    else:
                        msg = await ctx.send(embed=InfoEmbed(
                            author=ctx.author,
                            title=':shopping_bags: Create giveaway',
                            description=f'Final message will be sent to {arg1.mention}.'
                        ))

                        things: List[List[str, str]] = []
                        index = 0

                        info = await ctx.send(embed=InfoEmbed(
                            author=ctx.author,
                            title='Preparing...'
                        ))

                        # Getting items for giveaway
                        while True:
                            index += 1
                            await info.edit(embed=InfoEmbed(
                                author=ctx.author,
                                title=f':name_badge: {index}{number_suffix(index)} item name...',
                            ))
                            try:
                                # Get item's name
                                response_1 = await self.bot.wait_for('message', check=check, timeout=30)
                            except WaitTimeout:
                                return await info.edit(embed=TimeoutEmbed(author=ctx.author))
                            else:
                                # Ended before adding at least one item
                                if response_1.content.lower() in ['stop', 'end', 'x']:
                                    try:
                                        await response_1.delete()
                                    except Forbidden:
                                        pass
                                    if len(things) == 0:
                                        return await info.edit(embed=ErrorEmbed(
                                            author=ctx.author,
                                            title=':x: Too few things'
                                        ))
                                    break
                                elif len(response_1.content) > 30:
                                    try:
                                        await response_1.delete()
                                    except Forbidden:
                                        pass
                                    await info.edit(embed=ErrorEmbed(
                                        author=ctx.author,
                                        title=':x: Name\'s too long',
                                        description='Keep it under 30 characters.'
                                    ))
                                    return
                                await info.edit(embed=InfoEmbed(
                                    author=ctx.author,
                                    title=f':1234: {index}{number_suffix(index)} item quantity...'
                                ))
                                try:
                                    # Get item's quantity
                                    response_2 = await self.bot.wait_for('message', check=check, timeout=10)
                                except WaitTimeout:
                                    await info.edit(embed=TimeoutEmbed(author=ctx.author))
                                    try:
                                        await response_1.delete()
                                    except Forbidden:
                                        pass
                                    return
                                else:
                                    # Checking if quantity is a number
                                    try:
                                        q = int(response_2.content)
                                        if q < 1:
                                            raise ValueError
                                    except ValueError:
                                        await info.edit(embed=ErrorEmbed(
                                            author=ctx.author,
                                            title=':x: Bad format, quantity must be a number and higher than 0'
                                        ))
                                        try:
                                            await response_1.delete()
                                            await response_2.delete()
                                        except Forbidden:
                                            pass
                                        return
                                    if int(response_2.content) > 25:
                                        try:
                                            await response_1.delete()
                                        except Forbidden:
                                            pass
                                        await info.edit(embed=ErrorEmbed(
                                            author=ctx.author,
                                            title=':x: Too much',
                                            description='Keep quantity under 25.'
                                        ))
                                        return

                                    await info.edit(embed=PleaseWaitEmbed(author=ctx.author))
                                    things.append([response_1.content, response_2.content])
                                    await msg.edit(embed=msg.embeds[0].add_field(
                                        name=things[-1][1],
                                        value=things[-1][0]
                                    ))
                                    try:
                                        await response_1.delete()
                                        await response_2.delete()
                                    except Forbidden:
                                        pass

                        await info.delete()
                        final_em = SuccessEmbed(
                            author=ctx.author,
                            title=':white_check_mark: Done!'
                        ).set_footer(
                            text=f'Created by {ctx.author.display_name}'
                        )
                        for thing in things:
                            final_em.add_field(
                                name=f'x{thing[1]}',
                                value=thing[0]
                            )
                        await msg.edit(embed=final_em)

                        # Preparing final giveaway message
                        final_em.title = ':gift: Giveaway!'
                        final_em.color = random_color()
                        final_em.add_field(
                            name='\u200b',
                            value='React with `📝` to participate!',
                            inline=False
                        )
                        # Sending final giveaway message
                        try:
                            new_g = await arg1.send(embed=final_em)
                        except Forbidden:
                            await ctx.send(embed=ErrorEmbed(
                                author=ctx.author,
                                title=f':x: I have no permissions to send message in {arg1.mention}'
                            ))
                        else:
                            # Adding message ID to footer
                            await new_g.edit(embed=new_g.embeds[0].add_field(name='\u200b', value=f'{new_g.id}'))
                            try:
                                await new_g.add_reaction(emoji='📝')
                            except Forbidden:
                                await ctx.send(embed=ErrorEmbed(
                                    author=ctx.author,
                                    title=f':x: I can\'t add emoji to the message in {arg1.mention}'
                                ))
                            else:
                                create_giveaway(new_g.id, ctx.guild.id, data=str(things))
            elif option in ['delete', 'stop', 'end']:
                # Discord ID has 18 digits
                if len(str(arg1)) != 18:
                    await ctx.send(embed=ErrorEmbed(
                        author=ctx.author,
                        title=':x: Bad ID format'
                    ))
                else:
                    giveaway = get_giveaway_from_message(arg1)

                    # Giveaway message ID do not exists in database
                    if giveaway is None:
                        await ctx.send(embed=ErrorEmbed(
                            author=ctx.author,
                            title=':x: Giveaway do not exists'
                        ))

                    # Users shouldn't end giveaway from another guild
                    elif giveaway.guild_id != ctx.guild.id:
                        await ctx.send(embed=ErrorEmbed(
                            author=ctx.author,
                            title=':x: This giveaway do not belongs to this guild'
                        ))

                    else:
                        info = await ctx.send(embed=PleaseWaitEmbed(author=ctx.author))

                        # Finding giveaway's message
                        giveaway_message: Optional[Message] = None
                        for channel in ctx.guild.text_channels:
                            try:
                                giveaway_message = await channel.fetch_message(arg1)
                            except NotFound:
                                pass
                            else:
                                break

                        # Message do not exists but giveaway do
                        if giveaway_message is None:
                            await info.edit(embed=ErrorEmbed(
                                author=ctx.author,
                                title=':x: Message not found',
                                description='Giveaway exists but its message was probably removed,'
                                            ' so I\'m removing the giveaway.'
                            ))
                            if not delete_giveaway(message_id=arg1):
                                await self.bot.debug_log(
                                    ctx=ctx, e=DatabaseError(f'Unable to delete giveaway with message ID {arg1}')
                                )
                        else:
                            # Claiming giveaway's reactions
                            participants = []
                            for reaction in giveaway_message.reactions:
                                if reaction.emoji == '📝':
                                    async for user in reaction.users():
                                        if not user.bot:
                                            participants.append(user)
                                    break
                                await ctx.send(embed=ErrorEmbed(
                                    author=ctx.author,
                                    title=':x: Giveaway reaction not found',
                                    description='Deleting giveaway without winners.'
                                ))
                                await giveaway_message.edit(
                                    embed=giveaway_message.embeds[0].add_field(
                                        name='\u200b',
                                        value=f'Ended on {d.now()[:16]}'
                                    )
                                )
                                if not delete_giveaway(message_id=arg1):
                                    await self.bot.debug_log(
                                        ctx=ctx, e=DatabaseError(f'Unable to delete giveaway with message ID {arg1}')
                                    )

                            # No one added reaction to giveaway
                            if not participants:
                                await ctx.send(embed=ErrorEmbed(
                                    author=ctx.author,
                                    title=':x: No participants found',
                                    description='Deleting giveaway without winners.'
                                ))
                                if not delete_giveaway(message_id=arg1):
                                    await self.bot.debug_log(
                                        ctx=ctx, e=DatabaseError(f'Unable to delete giveaway with message ID {arg1}')
                                    )

                            else:
                                # Prepare giveaway's data
                                giveaway_data: List[List[str, str]] = literal_eval(giveaway.data)
                                winners = {}
                                for item in giveaway_data:
                                    possibles = participants.copy()
                                    item_winners = []
                                    for quantity in range(int(item[1])):
                                        if len(possibles) == 0:
                                            possibles = participants.copy()
                                        random_winner = choice(possibles)
                                        item_winners.append(random_winner)
                                        possibles.remove(random_winner)
                                    winners[item[0]] = item_winners
                                # noinspection SpellCheckingInspection
                                win_em = SuccessEmbed(
                                    author=ctx.author,
                                    title=':tada: Winners'
                                )

                                await info.edit(embed=InfoEmbed(
                                    author=ctx.author,
                                    title='How you\'d like to group result?',
                                    description='Please type `item` or `user`.'
                                ))
                                try:
                                    response: Message = await self.bot.wait_for('message', check=check, timeout=10)
                                except WaitTimeout:
                                    await info.edit(embed=TimeoutEmbed(author=ctx.author))
                                    return

                                r = response.content.lower()
                                u = ['u', 'user', 'users']
                                i = ['i', 'item', 'items']

                                if r in [*u, *i]:
                                    try:
                                        await response.delete()
                                    except Forbidden:
                                        pass

                                # Group by users
                                if r in u:
                                    all_users = set()
                                    for item in winners:
                                        for users in winners[item]:
                                            all_users.add(users)
                                    user_items = {}
                                    for user in all_users:
                                        prizes = []
                                        checked = []
                                        for prize in winners:
                                            for winner_user in winners[prize]:
                                                if winner_user.id == user.id:
                                                    prizes.append(prize)
                                        n_prizes = []
                                        for prize in prizes:
                                            if prize not in checked:
                                                n_prizes.append(f'{prize} x{prizes.count(prize)}')
                                                checked.append(prize)
                                        user_items[user] = n_prizes
                                    for user in user_items:
                                        win_em.add_field(
                                            name=user.display_name,
                                            value='- ' + '\n- '.join(user_items[user])
                                        )

                                # Group by items
                                elif r in i:
                                    for item in winners:
                                        winners_f = {}
                                        for w in [el for i, el in enumerate(winners[item], 1) if
                                                  el not in winners[item][i:]]:
                                            winners_f[w] = winners[item].count(w)
                                        win_em.add_field(
                                            name=item,
                                            value='- ' + '\n- '.join(map(
                                                lambda x: x.mention + str(
                                                    ((" *x" + str(winners_f[x])) + "*") if winners_f[x] > 1 else ""
                                                ),
                                                set(sorted(winners[item], key=lambda x: x.display_name))
                                            ))
                                        )

                                else:
                                    await info.edit(embed=ErrorEmbed(
                                        author=ctx.author,
                                        title=f':x: Unknown option `{r}`'
                                    ))
                                    return

                                await ctx.send(embed=win_em)
                                try:
                                    await ctx.message.delete()
                                except Forbidden:
                                    pass
                                await giveaway_message.edit(
                                    embed=giveaway_message.embeds[0].set_footer(text=f'Ended on {str(d.now())[:16]}')
                                )
                                if not delete_giveaway(message_id=arg1):
                                    await self.bot.debug_log(
                                        ctx=ctx, e=DatabaseError(f'Unable to delete giveaway with message ID {arg1}')
                                    )
                                await info.delete()
            else:
                await ctx.send(embed=ErrorEmbed(
                    author=ctx.author,
                    title=':x: Invalid option'
                ))

    @giveaway.error
    async def giveaway_error(self, ctx: Context, error: Exception):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Command\'s on cooldown'
            ))
        elif isinstance(error, MissingPermissions):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: You\'re not allowed to do that',
                description='You need **manage server** permission.'
            ))
        elif isinstance(error, CommandInvokeError):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: There was a problem with the giveaway',
                description='Probably, there are too many items in the giveaway.'
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)

    @cooldown(2, 5, BucketType.guild)
    @command(
        name='iq',
        brief='Check your IQ',
        usage='[user]',
        enabled=in_production()
    )
    async def iq(self, ctx: Context, user: User = None):
        if not user:
            user = ctx.author
        if user.id == self.bot.user.id:
            iq = 200
        elif user.bot is True:
            iq = 0
        else:
            iq = int(user.id) % int(user.discriminator) % 115 + 5
        description = ''
        if iq == 0:
            # noinspection SpellCheckingInspection
            description = 'Bots are stuuupiiid.'
        elif iq < 10:
            description = 'Oh my... I didn\'t think it\'s possible to be that stupid.' \
                          ' *(You\'d be great friends with Paimon)*'
        elif iq < 25:
            description = 'It\'s sickness, you know?'
        elif iq < 40:
            description = 'Some potatoes are smarter than you.'
        elif iq < 60:
            description = 'Roomba is smarter than you LMFAO.'
        elif iq == 69:
            description = 'Nice.'
        elif iq < 70:
            description = 'In terms of law - you\'re retarded.\n' \
                          '> Intellectual disability (ID), also known as general learning disability and mental' \
                          ' retardation (MR), is a generalized neurodevelopmental disorder characterized by' \
                          ' significantly impaired intellectual and adaptive functioning. It is defined by an IQ' \
                          ' under 70, in addition to deficits in two or more adaptive behaviors that affect everyday,' \
                          ' general living.'
        elif iq < 90:
            description = 'It\'s okay, but still not so smart.'
        elif iq < 110:
            description = 'You\'re normal, ***b o r i n g***.'
        elif iq <= 120:
            description = 'Okay, your\'e smart and it\'s maximum value. Cheater...'
        elif iq == 200:
            description = 'Oh my... It\'s super duper smart!!1!'
        safe_name = str(user.display_name). \
            replace('*', '\\*'). \
            replace('_', '\\_'). \
            replace('~', '\\~'). \
            replace('>', '\\>')
        await ctx.send(embed=SuccessEmbed(
            author=ctx.author,
            title=f':abacus: {safe_name}\'s IQ is {iq}',
            description=description
        ))

    @iq.error
    async def iq_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=CooldownEmbed(author=ctx.author))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)

    @cooldown(1, 6, BucketType.guild)
    @command(
        name='meme',
        brief='Send a meme',
        description='Sends meme from r/dankmemes.',
        enabled=in_production()
    )
    async def meme(self, ctx: Context):
        reddit = Reddit(
            client_id=reddit_settings['client_id'],
            client_secret=reddit_settings['client_secret'],
            user_agent=reddit_settings['user_agent']
        )
        posts = []
        # noinspection SpellCheckingInspection
        for submission in reddit.subreddit('dankmemes').hot(limit=20):
            if not submission.archived:
                if submission.score > 50:
                    if not submission.is_self:
                        if not submission.over_18:
                            posts.append(submission)
        if posts:
            await ctx.send(embed=SuccessEmbed(
                author=ctx.author,
                title=':black_joker: Meme found'
            ).set_image(
                url=choice(posts).url
            ))
        else:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Meme not found',
                description='Just try again'
            ))

    @meme.error
    async def meme_error(self, ctx: Context, error: Exception):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=CooldownEmbed(author=ctx.author))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)

    # noinspection SpellCheckingInspection
    @command(
        name='randomnumber',
        brief='Sends random number',
        description='You can provide maximun and minimum number to choose.',
        usage='[max] [min]',
        aliases=['randomnum', 'randnumber', 'randnum'],
        enabled=not in_production()
    )
    async def randomnumber(self, ctx: Context, max_: int = 10, min_: int = 1):
        nums = list(range(min_, max_ + 1))
        if len(nums) == 0:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Invalid argument(s)',
                description='Please remember, that first argument is `max` and the second is `min`.'
            ))
        else:
            num = choice(nums)
            url = f'https://numbersapi.p.rapidapi.com/{num}/math'
            headers = {
                'x-rapidapi-host': 'numbersapi.p.rapidapi.com',
                'x-rapidapi-key': rapidapi_settings['key']
            }
            querystring = {"fragment": "false", "json": "false"}
            response = request("GET", url, headers=headers, params=querystring)
            result: Optional[dict] = json_loads(response.text) if response.status_code == 200 else None
            em = SuccessEmbed(
                author=ctx.author,
                title=f':1234: I\'ve chosen {num}'
            )
            if result and result['found']:
                em.add_field(
                    name='Funfact',
                    value=f'{result["text"].capitalize()}.'
                )
            await ctx.send(embed=em)

    @command(
        name='choice',
        brief='Helps with choosing',
        usage='<thing1> <thing2> [thingN]',
        enabled=in_production()
    )
    async def choice(self, ctx: Context, *, things: str):
        breakpoint()
        em = ErrorEmbed
        if not things:
            title = ':x: No items specified'
        elif len(things) < 2:
            title = ':x: Too few thing specified'
        else:
            title = f':abcd: I\'ve chosen {choice(things)}'
            em = SuccessEmbed
        await ctx.send(embed=em(
            author=ctx.author,
            title=title
        ))

    @command(
        name='coin',
        brief='Tosses a coin',
        descriptiom='O Valley of Plenty...',
        aliases=['toss'],
        enabled=in_production()
    )
    async def coin(self, ctx: Context):
        await ctx.send(embed=SuccessEmbed(
            author=ctx.author,
            title=':small_red_triangle_down: Tails' if randint(1, 2) == 1 else ':small_red_triangle: Heads'
        ))

    # TODO - Joke

    # TODO - Slapping

    # TODO - Psycho test

    # TODO - Random name generator

    # TODO - Random color

    # TODO - 8ball

    # TODO - How to

    # TODO - Curiosities/funfacts


def setup(bot):
    bot.add_cog(Fun(bot))
