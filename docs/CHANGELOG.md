# Enigma Bot changelog

## [Unreleased]

## Released
### [v0.7] - 08.02.2021
#### Added
- `spotify` command.
#### Fixed
- `ping` commands was showing negative values.
- `giveaway` command embed.
#### Changed
- `suggest` command aliases and description.
- Settings are now more Python-friendly.

### [v0.6] - 04.02.2021
#### Added
- `unban` command.
- `servers` command.
- `whois` command.
- Logging guilds count.
- Logging amount of cogs loaded.
- Logging connection to Discord.
- Checking connection with database.
#### Fixed
- `randomnumber` command was disabled.
- `host` command without na argument no more raises an error.
#### Changed
- Command errors are now handled globally.
- `ping` command sends both ping and latency.
- `help` command do not sends classic representation if it's same as usage.
- `prune` command's error description slightly changed to be more precise.
- Logging is now more clear.
- SQL-Alchemy logging level set to WARNING.
- Version in settings is now a function.
- Normalized get function in `settings.py`.
#### Removed
- `error` command.

### [v0.5] - 03.02.2021
#### Added
- `suggest` command.
- `prune` command.
#### Changed
- Embeds have now fixed colors, based on message type.
- `error` cooldown increased from 30 seconds to 60.

### [v0.4] - 25.10.2020
#### Added
- `randomnumber` command.
- `choice` command.
- `coin` command.
#### Fixed
- Communication with database is now more safe.

### v0.3-hotfix
#### Fixed
- `help` command was disabled.

### [v0.3] - 21.10.2020
#### Added
- `invite` command.
- Error when giveaway result is too big is handled.
- `avatar`'s embed description simplified.
- `daily` command.
- `info` command.
- Custom `help` command.
#### Changed
- Using `giveaway` command requires "manage guild" permission.
- Increased `meme`'s cooldown from 4s to 6s.
- `giveaway`'s help is now more precise.
- `giveaway`'s name has to be 30 characters or less.
- `giveaway`'s quantity has to be 25 or less.
- Giveaway's preview message and final message have now fields instead of big descriptions.
- `user` parameter is now optional in `profile` command.
- Profile's now are on field instead of big description.
- Optional 3rd argument in `giveaway` is now asked for.
- Final `giveaway` massage is prettier.
- Cooldowns' messages no more include time, because it was incorrect.
- All commands are now enabled only in development or production.
#### Fixed
- First `daily` is not creating profile **and** adds cash.
- Value 0 is now possible in `manage` command.
- Using `daily` 2 and more times now shows correct message.

### [v0.2] - 16.10.2020
#### Added
- `meme` command.
- Choosing winners from giveaway.
- Optional argument how to group winners from giveaway.
- Cosmetics to giveaways' messages.
- Cooldown for `giveaway` and `iq`.
#### Changed
- Cooldown handler text is same everywhere.
- If `iq`'s command argument is Enigma bot itself it sends score 200.
- If `iq`'s command argument is any other bot it sends score 0.

### [v0.1] - 16.10.2020
#### Added
- Banning command.
- Kicking command.
- Checking bot's latency command.
- Giveaways command.
- Getting users' avatars command.
- Managing users' data command.
- Users' profiles command.
- Communication with the database using SQLAlchemy.


[Unreleased]: https://github.com/AnonymousX86/Enigma-Bot/compare/deploy...master
[v0.7]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.7
[v0.6]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.6
[v0.5]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.5
[v0.4]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.4
[v0.3]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.3
[v0.2]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.2
[v0.1]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.1

