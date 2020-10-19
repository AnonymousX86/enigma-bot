# -*- coding: utf-8 -*-
from ast import literal_eval
from asyncio import TimeoutError as WaitTimeout
from datetime import datetime as d
from random import choice
from typing import List, Union, Optional

from discord import Embed, Forbidden, TextChannel, NotFound, User, Message
from discord.ext.commands import Cog, command, Context, cooldown, BucketType, CommandOnCooldown, has_permissions, \
    MissingPermissions, CommandInvokeError
from praw import Reddit

from enigma.settings import reddit_settings
from enigma.utils.colors import random_color
from enigma.utils.database import create_giveaway, get_giveaway_from_message, delete_giveaway
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
             ' with argument <message ID> and optional [group by], could be "item" (default) or "user"\n'
             '  Message ID could be found under the giveaway message.\n'
             'Maximum item\'s length is 30 characters and maximum amount is 25.',
        usage='<option> <additional argument> [group result by]',
        aliases=['ga']
    )
    async def giveaway(self, ctx: Context, option: str = '', arg1: Union[TextChannel, int] = None, arg2: str = 'item'):
        if not option:
            await ctx.send(embed=Embed(
                title=':x: Please specify an option',
                color=random_color()
            ))
        else:
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            if option in ['create', 'start', 'new']:
                if not arg1:
                    await ctx.send(embed=Embed(
                        title=':x: Missing channel',
                        color=random_color()
                    ))
                elif type(arg1) is not TextChannel:
                    await ctx.send(embed=Embed(
                        title=':x: Bad channel format',
                        color=random_color()
                    ))
                else:
                    perms = arg1.permissions_for(ctx.guild.get_member(self.bot.user.id))
                    if not perms.read_messages:
                        await ctx.send(embed=Embed(
                            title=':x: I can\'s see that channel'
                        ))
                    elif not perms.send_messages:
                        await ctx.send(embed=Embed(
                            title=':x: I can\'s send messages to that channel'
                        ))
                    else:
                        msg = await ctx.send(embed=Embed(
                            title=':shopping_bags: Create giveaway',
                            description=f'Final message will be sent to {arg1.mention}.',
                            color=random_color()
                        ).set_footer(
                            text=f'Listening to {ctx.author.display_name}'
                        ))

                        things: List[List[str, str]] = []
                        index = 0

                        info = await ctx.send(embed=Embed(
                            title='Preparing...',
                            color=random_color()
                        ))

                        # Getting items for giveaway
                        while True:
                            index += 1
                            await info.edit(embed=Embed(
                                title=f':name_badge: {index}{number_suffix(index)} item name...',
                                color=random_color()
                            ))
                            try:
                                # Get item's name
                                response_1 = await self.bot.wait_for('message', check=check, timeout=30)
                            except WaitTimeout:
                                await info.edit(embed=Embed(
                                    title=':x: Timed out',
                                    color=random_color()
                                ))
                                return
                            else:
                                # Ended before adding at least one item
                                if response_1.content.lower() in ['stop', 'end', 'x']:
                                    try:
                                        await response_1.delete()
                                    except Forbidden:
                                        pass
                                    if len(things) == 0:
                                        await info.edit(embed=Embed(
                                            title=':x: Too few things',
                                            color=random_color()
                                        ))
                                        return
                                    break
                                elif len(response_1.content) > 30:
                                    try:
                                        await response_1.delete()
                                    except Forbidden:
                                        pass
                                    await info.edit(embed=Embed(
                                        title=':x: Name\'s too long',
                                        description='Keep it under 30 characters.',
                                        color=random_color()
                                    ))
                                    return
                                await info.edit(embed=Embed(
                                    title=f':1234: {index}{number_suffix(index)} item quantity...',
                                    color=random_color()
                                ))
                                try:
                                    # Get item's quantity
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
                                    # Checking if quantity is a number
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
                                    if int(response_2.content) > 25:
                                        try:
                                            await response_1.delete()
                                        except Forbidden:
                                            pass
                                        await info.edit(embed=Embed(
                                            title=':x: Too much',
                                            description='Keep quantity under 25.',
                                            color=random_color()
                                        ))
                                        return

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
                        final_em = Embed(
                            title=':white_check_mark: Done!',
                            color=random_color()
                        ).set_footer(
                            text=f'Created by {ctx.author.display_name}'
                        )
                        for thing in things:
                            final_em.add_field(
                                name=thing[1],
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
                            await ctx.send(embed=Embed(
                                title=f':x: I have no permissions to send message in {arg1.mention}',
                                color=random_color()
                            ))
                        else:
                            # Adding message ID to footer
                            await new_g.edit(embed=new_g.embeds[0].set_footer(text=f'{new_g.id}'))
                            try:
                                await new_g.add_reaction(emoji='📝')
                            except Forbidden:
                                await ctx.send(embed=Embed(
                                    title=f':x: I can\'t add emoji to the message in {arg1.mention}',
                                    color=random_color()
                                ))
                            else:
                                create_giveaway(new_g.id, ctx.guild.id, data=str(things))
            elif option in ['delete', 'stop', 'end']:
                # Discord ID has 18 digits
                if len(str(arg1)) != 18:
                    await ctx.send(embed=Embed(
                        title=':x: Bad ID format',
                        color=random_color()
                    ))
                else:
                    giveaway = get_giveaway_from_message(arg1)

                    # Giveaway message ID do not exists in database
                    if giveaway is None:
                        await ctx.send(embed=Embed(
                            title=':x: Giveaway do not exists',
                            color=random_color()
                        ))

                    # Users shouldn't end giveaway from another guild
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
                            await info.edit(embed=Embed(
                                title=':x: Message not found',
                                description='Giveaway exists but its message was probably removed,'
                                            ' so I\'m removing the giveaway.',
                                color=random_color()
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
                                        user: User
                                        if not user.bot:
                                            participants.append(user)
                                    break
                                await ctx.send(embed=Embed(
                                    title=':x: Giveaway reaction not found',
                                    description='Deleting giveaway without winners.',
                                    color=random_color()
                                ))
                                await giveaway_message.edit(
                                    embed=giveaway_message.embeds[0].set_footer(text=f'Ended on {d.now()[:16]}')
                                )
                                if not delete_giveaway(message_id=arg1):
                                    await self.bot.debug_log(
                                        ctx=ctx, e=DatabaseError(f'Unable to delete giveaway with message ID {arg1}')
                                    )

                            # No one added reaction to giveaway
                            if not participants:
                                await ctx.send(embed=Embed(
                                    title=':x: No participants found',
                                    description='Deleting giveaway without winners.',
                                    color=random_color()
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
                                win_em = Embed(
                                    title=':tada: Winners',
                                    color=random_color()
                                )

                                # Group by users
                                if arg2 == 'user':
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
                                else:
                                    for item in winners:
                                        win_em.add_field(
                                            name=item,
                                            value='- ' + '\n- '.join(map(
                                                lambda u: u.mention, sorted(winners[item], key=lambda u: u.display_name)
                                            ))
                                        )

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
                await ctx.send(embed=Embed(
                    title=':x: Invalid option',
                    color=random_color()
                ))

    @giveaway.error
    async def giveaway_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=Embed(
                title=f':x: Command\'s on cooldown',
                color=random_color()
            ))
        elif isinstance(error, MissingPermissions):
            await ctx.send(embed=Embed(
                title=':x: You\'re not allowed to do that',
                description='You need **manage guild** permission.',
                color=random_color()
            ))
        elif isinstance(error, CommandInvokeError):
            await ctx.send(embed=Embed(
                title=':x: There was a problem with the giveaway',
                description=f'Probably, there are too many items in the giveaway.'
                            f' Ask <@!{self.bot.owner_id}> for help.',
                color=random_color()
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)

    @cooldown(2, 5, BucketType.guild)
    @command(
        name='iq',
        brief='Check your IQ',
        usage='[user]'
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
            description = 'It\'s okay, ~~to be g...~~ but still not so smart.'
        elif iq < 110:
            description = 'You\'re normal, ***b o r i n g***.'
        elif iq <= 120:
            description = 'Okay, your\'e smart and it\'s maximum value. Cheater...'
        elif iq == 200:
            description = 'Oh my... It\'s super duper smart!!1!'
        safe_name = str(user.display_name).\
            replace('*', '\\*').\
            replace('_', '\\_').\
            replace('~', '\\~').\
            replace('>', '\\>')
        await ctx.send(embed=Embed(
            title=f':abacus: {safe_name}\'s IQ is {iq}',
            description=description,
            color=random_color()
        ))

    @iq.error
    async def iq_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=Embed(
                title=f':x: Try again in {str(error)[-5:]}',
                color=random_color()
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)

    @cooldown(1, 6, BucketType.guild)
    @command(
        name='meme',
        brief='Send a meme',
        description='Obtaining a meme could be a little slow.'
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
            await ctx.send(embed=Embed(
                title=':black_joker: Meme found',
                color=random_color()
            ).set_image(
                url=choice(posts).url
            ))
        else:
            await ctx.send(embed=Embed(
                title=':x: Meme not found',
                description='Just try again',
                color=random_color()
            ))

    @meme.error
    async def meme_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=Embed(
                title=f':x: Try again in {str(error)[-5:]}',
                color=random_color()
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error)


def setup(bot):
    bot.add_cog(Fun(bot))
