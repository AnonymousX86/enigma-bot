# Enigma Bot changelog

## [Unreleased]
### v0.3
#### Added
- `invite` command.
- Error when giveaway result is too big is handled.
- `avatar`'s embed description simplified.
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

## Released

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


[Unreleased]: https://github.com/AnonymousX86/Enigma-Bot/compare/v1.0...HEAD
[v0.2]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.2
[v0.1]: https://github.com/AnonymousX86/Enigma-Bot/releases/tag/v0.1

