# -*- coding: utf-8 -*-
from discord import TextChannel
from discord.ext.commands import command, Cog, has_permissions, MissingPermissions, Context, cooldown, BucketType, \
    CommandOnCooldown, CommandError, Command

from enigma.settings import in_production, general_settings
from enigma.utils.emebds.core import InfoEmbed, ErrorEmbed, SuccessEmbed
from enigma.utils.emebds.errors import CooldownEmbed
from enigma.utils.emebds.misc import SuggestionEmbed
from enigma.utils.exceptions import NoError


class Basics(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(
        name='help',
        brief='Shows this message',
        usage='[category|command]',
        enabled=in_production()
    )
    async def help(self, ctx: Context, arg: str = None):
        help_em = InfoEmbed(
            author=ctx.author,
            title=':grey_question: Help'
        )
        help_category = 'You can also type `>help <category>` for more info on a category.'
        help_command = 'Type `>help <command>` for more info on a command.'
        if arg is None:
            help_em.description = f'{help_category}\n{help_command}'
            for cog in self.bot.cogs:
                help_em.add_field(
                    name=str(cog),
                    value=', '.join(map(lambda x: f'`{x.name}`', self.bot.cogs[cog].get_commands())),
                    inline=False
                )
        else:
            cmd: Command = self.bot.get_command(arg)
            if not cmd:
                cog: Cog = self.bot.get_cog(arg.capitalize())
                if not cog:
                    help_em.description = f'No command or category called `{arg}` found.'
                # Cog found
                else:
                    help_em.description = help_command
                    help_em.add_field(
                        name='Category',
                        value=f'```\n{cog.qualified_name}\n```',
                        inline=False
                    )
                    for cmd in cog.get_commands():
                        try:
                            if await cmd.can_run(ctx):
                                help_em.add_field(
                                    name=f'`{cmd}`',
                                    value=cmd.brief or '\u200b'
                                )
                        except CommandError:
                            pass
            # Command found
            else:
                help_em.description = help_category
                help_em.add_field(
                    name='Command',
                    value=f'```\n{cmd.name}\n```',
                    inline=False
                )
                if cmd.description:
                    help_em.add_field(
                        name='Description',
                        value=cmd.description,
                        inline=False
                    )
                if cmd.aliases:
                    help_em.add_field(
                        name='Aliases',
                        value=', '.join(map(lambda x: f'`{x}`', cmd.aliases)),
                        inline=False
                    )
                if cmd.usage:
                    help_em.add_field(
                        name='Usage',
                        value=f'`>{cmd.name} {cmd.usage}`',
                        inline=False
                    )
                if cmd.help:
                    help_em.add_field(
                        name='Additional help',
                        value=cmd.help,
                        inline=False
                    )
                if cmd.aliases or cmd.usage:
                    base = cmd.name if not cmd.aliases else f'[{"|".join([cmd.name, *cmd.aliases])}]'
                    tail = cmd.usage or ''
                    help_em.add_field(
                        name='Classic representation',
                        value=f'```\n>{base} {tail}\n```'
                    )

        await ctx.send(embed=help_em)

    @command(
        name='error',
        brief='Raises an example error',
        description='Only specific users have access to this command',
        aliases=['err'],
        hidden=True
    )
    @cooldown(1, 30, BucketType.user)
    @has_permissions(administrator=True)
    async def error_cmd(self, ctx: Context):
        await self.bot.debug_log(ctx=ctx, e=NoError())
        await ctx.send(embed=ErrorEmbed(
            author=ctx.author,
            title=':exclamation: Raised `NoError`',
            description='Bot\'s owner should be notified'
        ))

    @error_cmd.error
    async def error_error(self, ctx: Context, error: Exception):
        if isinstance(error, MissingPermissions):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':man_technologist: You\'re not an IT specialist',
                description='Only those can use this command'
            ))
        elif isinstance(error, CommandOnCooldown):
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Command\'s on cooldown'
            ))
        else:
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)

    @command(
        name='ping',
        brief='Checks bot latency',
        description='Counts time difference between command execution time and bot\'s response',
        enabled=in_production()
    )
    async def ping(self, ctx: Context):
        await ctx.send(embed=SuccessEmbed(
            author=ctx.author,
            title=':ping_pong: Pong!',
            description=f'Current latency is: {round(self.bot.latency * 1000)}ms'
        ))

    @command(
        name='invite',
        brief='Sends bot\'s invite link',
        enabled=in_production()
    )
    async def invite(self, ctx: Context):
        await ctx.send(embed=InfoEmbed(
            author=ctx.author,
            title=':mailbox_with_mail: Check at top.gg',
            description='**\u00bb [Click me!](https://top.gg/bot/678357487560425555) \u00ab**'
        ).add_field(
            name='Important info',
            value='Remember, that you need **manage users** permission to add me to the server.'
        ))

    @command(
        name='info',
        brief='Sends short bot\'s info',
        description='Sends info about bot itself and its author. This is NOT help command.',
        aliases=['about', 'github', 'code'],
        enabled=in_production()
    )
    async def info(self, ctx: Context):
        await ctx.send(embed=InfoEmbed(
            author=ctx.author,
            title=':desktop: Source code',
            description='This bot is made on open source, GNU GPL v3.0 license.'
        ).add_field(
            name='Links',
            value='\u00b7 [GitHub homepage](https://github.com/AnonymousX86/Enigma-Bot)\n'
                  '\u00b7 [Changelog](https://github.com/AnonymousX86/Enigma-Bot/'
                  'blob/master/docs/CHANGELOG.md#enigma-bot-changelog)\n',
            inline=False
        ).add_field(
            name='Support',
            value='If you\'d like to help to develop this bot please check GitHub. (Link above)\n'
                  'And if **you** need support please check'
                  ' [support server](https://discord.gg/SRdmrPpf2z "3N1GMA Support Server").',
            inline=False
        ).add_field(
            name='More about bot',
            value=f'Version: `{self.bot.version}`.\n'
                  f'Author: `{str(self.bot.get_user(self.bot.owner_id))}`.',
            inline=False
        ))

    @cooldown(1, 120, BucketType.user)
    @command(
        name='suggest',
        brief='Suggest a change',
        description='Ask dev(s) for a functionality.',
        help='Keep your message between 25 and 120 characters.',
        usage='<message>',
        aliases=['change'],
        enabled=not in_production()
    )
    async def change(self, ctx: Context, *, message: str = None):
        if not message:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Whoops!',
                description='You forget to add a message.'
            ))
        elif len(message) < 25:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Whoops!',
                description='Suggestion is too short. Write more, please.'
            ))
        elif len(message) > 120:
            await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Whoops!',
                description='Suggestion is too long. Write less, please.'
            ))
        else:
            channel: TextChannel = self.bot.get_channel(general_settings['suggestions_channel'])
            msg = await channel.send(embed=SuggestionEmbed(
                author=ctx.author,
                message=message
            ))
            await ctx.send(embed=SuccessEmbed(
                author=ctx.author,
                title=':thumbsup: Thanks for suggestion!',
                description=f'Check your suggestion here: {channel.mention} or click'
                            f' [here]({msg.jump_url} "Direct message link").'
            ))
            await msg.add_reaction(emoji='👍')
            await msg.add_reaction(emoji='👎')

    @change.error
    async def change_error(self, ctx: Context, error: Exception):
        if isinstance(error, CommandOnCooldown):
            await ctx.send(embed=CooldownEmbed(author=ctx.author))
        else:
            await self.bot.debug_log(ctx=ctx, e=error, member=ctx.message.author)
            raise error

    # TODO - Ticket system


def setup(bot):
    bot.add_cog(Basics(bot))
