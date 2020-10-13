# -*- coding: utf-8 -*-
from discord import Embed
from discord.ext.commands import command, Cog, has_permissions, bot_has_permissions
from discord.utils import get

from enigma.utils.colors import random_color
from enigma.utils.databases import cache_client, postgre_connect
from enigma.utils.exceptions import StatsError


class Stats(Cog):

    def __init__(self, bot):
        self.bot = bot

    enabled = False

    @command(
        name='stats',
        brief='Main stats command',
        help='Options:\n'
             '`config` - initializing guild statistics with default settings\n'
             '`delete` - deletes all channels inside stats category, deletes stats category itself, and erases save '
             'from bot\'s database',
        description='Command is useless until you will provide argument(s)',
        usage='<option>'
    )
    @has_permissions(manage_channels=True)
    @bot_has_permissions(manage_channels=True)
    async def stats(self, ctx, arg=None):
        """
        Manages guild stats.

        :param ctx: Context object.
        :param arg: "config" or "delete".
        :return: True if configured or deleted and False if not.
        """
        if not self.enabled:
            await ctx.send(embed=Embed(
                title=':gear: This is under construction',
                description='Please be patient',
                color=random_color()
            ))
            return False

        if not arg:
            await ctx.send(embed=Embed(
                title=':woman_tipping_hand: What should I do?',
                description='See available options by executing `help stats`',
                color=random_color()
            ))
            return False

        else:
            arg = arg.lower()

            # Adding stats to guild
            if arg == 'config':
                # Trying to get channel ID from database
                db = postgre_connect()
                c = db.cursor()
                c.execute(
                    '''
                    SELECT settings_stats.stats_category_id
                    FROM settings_stats
                    NATURAL JOIN guilds
                    WHERE guild_id = %s::bigint;
                    ''',
                    (
                        int(ctx.guild.id),
                    )
                )
                result = c.fetchone()

                if type(result) is tuple:
                    result = result[0]

                # If channel ID is not set in database
                if result is None:
                    msg = await ctx.send(embed=Embed(
                        title=':gear: No stats are found on this guild',
                        description='Bot will create those for you with default settings',
                        color=random_color()
                    ))

                    # Enabling default settings for guild
                    c.execute(
                        '''
                        INSERT INTO settings_stats (guild_id)
                        VALUES (%s::bigint);
                        ''',
                        (
                            int(ctx.guild.id),
                        )
                    )
                    db.commit()

                    new_category = await ctx.guild.create_category_channel('Stats', reason='Adding stats')

                    c.execute(
                        '''
                        UPDATE settings_stats
                        SET stats_category_id = %s::bigint
                        WHERE guild_id = %s::bigint;
                        ''',
                        (
                            int(new_category.id),
                            int(ctx.guild.id)
                        )
                    )
                    db.commit()

                    c.execute(
                        '''
                        SELECT members_total,
                               members_online,
                               members_max,
                               members_users,
                               members_bots,
                               guild_bans
                        FROM settings_stats
                        NATURAL JOIN guilds
                        WHERE guild_id = %s::bigint
                        ''',
                        (
                            int(ctx.guild.id),
                        )
                    )
                    result = c.fetchone()

                    # db_settings = dict(
                    #     members_total=result[0],
                    #     members_online=result[1],
                    #     members_max=result[2],
                    #     members_users=result[3],
                    #     members_bots=result[4],
                    #     guild_bans=result[5],
                    # )

                    names = (
                        'Total members: ',
                        'Now online: ',
                        'All time max: ',
                        'Humans: ',
                        'Bots: ',
                        'Bans: '
                    )
                    channels_columns = (
                        'total',
                        'online',
                        'max',
                        'users',
                        'bots',
                        'bans'
                    )

                    # Creating channels and saving them to database
                    for i in range(6):
                        if result[i] is True:
                            # FIXME - initialized stats are by default 0
                            new_channel = await ctx.guild.create_voice_channel(name=str(names[i] + '0'),
                                                                               category=new_category,
                                                                               reason='Adding stats')
                            c.execute(
                                '''
                                UPDATE settings_stats
                                SET {} = %s::bigint
                                WHERE guild_id = %s::bigint
                                '''.format(f'channel_id_{channels_columns[i]}'),
                                (
                                    int(new_channel.id),
                                    int(ctx.guild.id)
                                )
                            )
                    db.commit()

                    c.close()
                    db.close()

                    await msg.edit(embed=Embed(
                        title=':ballot_box_with_check: Stats successfully created',
                        description=f'It\'s `{new_category.name}`',
                        color=random_color()
                    ))
                    return True

                # Channel ID is set in database
                else:
                    await ctx.send(embed=Embed(
                        title=':grey_exclamation: Stats are already set',
                        description=f'Category ID: {result}',
                        color=random_color()
                    ))
                    return False

            # Removing stats
            elif arg == 'delete':
                msg = await ctx.send(embed=Embed(
                    title=':wastebasket: Stats are being deleted...',
                    color=random_color()
                ))

                # Trying to get channel ID from database
                db = postgre_connect()
                c = db.cursor()
                c.execute(
                    '''
                    SELECT settings_stats.stats_category_id
                    FROM settings_stats
                    NATURAL JOIN guilds
                    WHERE guild_id = %s::bigint;
                    ''',
                    (
                        int(ctx.guild.id),
                    )
                )
                result = c.fetchone()

                if type(result) is tuple:
                    result = result[0]

                if result is None:
                    await msg.edit(embed=Embed(
                        title=':grey_exclamation: Sats are not set for this guild',
                        description='Please run `stats config`',
                        color=random_color()
                    ))
                    return False

                else:
                    del_category_id = ctx.guild.get_channel(result).id
                    del_channels_ids = []
                    for channel in ctx.guild.voice_channels:
                        if channel.category_id == del_category_id:
                            del_channels_ids.append(channel.id)

                    for channel_id in del_channels_ids:
                        await ctx.guild.get_channel(channel_id).delete(reason='Deleting stats')
                    await ctx.guild.get_channel(del_category_id).delete(reason='Deleting stats')

                    db = postgre_connect()
                    c = db.cursor()
                    c.execute(
                        '''
                        DELETE
                        FROM settings_stats
                        WHERE guild_id = %s::bigint;
                        ''',
                        (
                            int(ctx.guild.id),
                        )
                    )
                    db.commit()
                    c.close()
                    db.close()

                    await msg.edit(embed=Embed(
                        title=':ballot_box_with_check: Done!',
                        color=random_color()
                    ))
                    return True

            # Unknown option
            else:
                await ctx.send(embed=Embed(
                    title=':man_bowing: Bad option',
                    description='You don\'t specified what should I do properly',
                    color=random_color()
                ))
                return False

    # @stats.error
    # async def stats_error(self, ctx, error):
    #     if isinstance(error, MissingPermissions):
    #         status = 'You don\'t have **manage channels** permissions!'
    #
    #     elif isinstance(error, BotMissingPermissions):
    #         status = 'I don\' have **manage channels** permissions!'
    #
    #     else:
    #         status = 'Unknown error has occurred!'
    #         await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)
    #
    #     await ctx.send(embed=Embed(
    #         title=':rolling_eyes: Whoops!',
    #         description=status,
    #         color=random_color()
    #     ))

    @Cog.listener(name='on_member_join')
    async def update_member_join(self, member):
        # FIXME - stats are not updated
        if self.enabled:
            client = cache_client()

            channel_id_total = client.get('channel_id_total')
            channel_id_users = client.get('channel_id_users')
            channel_id_bots = client.get('channel_id_bots')

            if channel_id_total is None or channel_id_users is None or channel_id_bots is None:
                db = postgre_connect()
                c = db.cursor()
                c.execute(
                    '''
                    SELECT channel_id_total,
                           channel_id_users,
                           channel_id_bots
                    FROM settings_stats
                    NATURAL JOIN guilds
                    WHERE guild_id = %s::bigint
                    ''',
                    (
                        int(member.guild.id),
                    )
                )
                result = c.fetchone()
                channel_id_total = result[0]
                channel_id_users = result[1]
                channel_id_bots = result[2]
                c.close()
                db.close()

            for channel_id in (channel_id_total, channel_id_users, channel_id_bots):
                stat_channel = get(member.guild.chahhenls, id=channel_id, type='ChannelType.voice')
                for index, char in enumerate(stat_channel):
                    # "Humans: 10"
                    if char == ':':
                        if channel_id is channel_id_total:
                            new_stat = str(len(member.guild.members))

                        elif channel_id is channel_id_users:
                            humans = 0
                            for member in member.guild.members:
                                if member.bot is False:
                                    humans += 1
                            new_stat = str(humans)

                        elif channel_id is channel_id_bots:
                            bots = 0
                            for member in member.guild.members:
                                if member.bot is False:
                                    bots += 1
                            new_stat = str(bots)

                        else:
                            new_stat = 'Error'

                        await stat_channel.edit(
                            name=stat_channel.name[0:index + 1] + new_stat
                        )
                        continue

                    await self.bot.debug_log(e=StatsError, member=member)


def setup(bot):
    bot.add_cog(Stats(bot))
