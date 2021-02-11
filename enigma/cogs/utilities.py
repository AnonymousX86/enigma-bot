# -*- coding: utf-8 -*-
from discord import HTTPException, NotFound, Forbidden
from discord.ext.commands import Cog, command, Context, cooldown, BucketType
from spotipy import Spotify, SpotifyClientCredentials, SpotifyOauthError, SpotifyException
from youtubesearchpython import SearchVideos

from enigma.emebds.core import ErrorEmbed, SuccessEmbed
from enigma.settings import in_production, spotify_client_id, spotify_client_secret


class Utilities(Cog):
    def __init__(self, bot):
        self.bot = bot

    # noinspection SpellCheckingInspection
    @cooldown(1, 30, BucketType.user)
    @command(
        name='spotify',
        brief='Spotify lurker',
        description='Searching Spotify for a specified object and sends YouTube version.',
        help='Available Spotify types:\n'
             '- `track`,\n'
             '- `album`,\n'
             '- `artist`,\n'
             '- `playlist`\n'
             'For example:```\n>spotify 4uLU6hMCjMI75M1A2tKUQC track.\n```'
             'If you pass a valid link, bot is able to recognize type. Like:```\n'
             '>spotify https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC\n```',
        usage='<Spotify link|ID> [type]',
        enabled=in_production()
    )
    async def spotify(self, ctx: Context, url: str = None, type_: str = None):
        if not url:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Missing Spotify link or ID'
            ))
        elif not type_:
            try:
                type_ = url.split('&')[0].split('?')[0].split('/')[3]
            except IndexError:
                pass

        if type_ == 'user':
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: User profiles are not supported',
                description='...yet?'
            ))
        elif type_ not in ['track', 'album', 'artist', 'playlist']:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: What is this?',
                description='Is it `track`, `album`, `artist` or `playlist`?'
            ))

        if url.startswith(('http://open.spotify.com', 'https://open.spotify.com')):
            url = url.split('?')[0].split('/')[-1]

        type_ = type_.lower()

        try:
            sp = Spotify(auth_manager=SpotifyClientCredentials(
                client_id=spotify_client_id(),
                client_secret=spotify_client_secret()
            ))
        except SpotifyOauthError:
            sp = None

        if not sp:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Unable to connect to Spotify!'
            ))

        result = error_code = None
        em = SuccessEmbed(
            author=ctx.author
        ).set_author(
            name=f'{ctx.author.display_name} shared a{"n" if type_[0] == "a" else ""} {type_}:',
            icon_url=ctx.author.avatar_url
        )

        if type_ == 'track':
            try:
                result = sp.track(url)
            except SpotifyException as e:
                error_code = int(e.http_status)
        elif type_ == 'album':
            try:
                result = sp.album(url)
            except SpotifyException as e:
                error_code = int(e.http_status)
        elif type_ == 'playlist':
            try:
                result = sp.playlist(url)
            except SpotifyException as e:
                error_code = int(e.http_status)
        elif type_ == 'artist':
            try:
                result = sp.artist(url)
            except SpotifyException as e:
                error_code = int(e.http_status)
        else:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Unknown object type',
                description='Check `>help` for valid object types.'
            ))

        if error_code:
            if error_code == 400:
                d = 'Invalid ID or URL.'
            elif error_code == 429:
                d = 'Unable to do that now, please try again in 5 minutes.'
            elif str(error_code).startswith('5'):
                d = 'Spotify is not responding.'
            else:
                d = 'Unknown error. Please try again in a few minutes and please make sure URL or ID is valid.'
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: An error occurred!',
                description=d
            ))
        elif not result:
            return await ctx.send(embed=ErrorEmbed(
                author=ctx.author,
                title=':x: Unable to find anything on Spotify',
                description='Probably URL/ID is wrong.'
            ))

        title = result['name']

        # Artists
        if type_ not in ['artist', 'playlist']:
            artists = list(map(lambda x: [x['name'], x['external_urls']['spotify']], result['artists']))
        elif type_ in ['playlist']:
            artists = [[result['owner']['display_name'], result['owner']['external_urls']['spotify']]]
        else:
            artists = None

        # Released
        if type_ == 'track':
            released = result['album']['release_date']
        elif type_ == 'album':
            released = result['release_date']
        else:
            released = None

        # Genres
        if type_ in ['artist', 'album']:
            genres = ', '.join(result['genres']) or 'Not specified'
        else:
            genres = None

        ex_url = result['external_urls']['spotify']
        thumbnail = result['album']['images'][0]['url'] if type_ == 'track' else result['images'][0]['url']

        # Title
        if title:
            em.add_field(
                name='Name' if type_ in ['artist'] else 'Title',
                value=title
            )

        # Author / Artist(s)
        if artists:
            em.add_field(
                name='Author' if type_ == 'playlist' else 'Artist' if len(artists) == 1 else 'Artists',
                value=', '.join(map(lambda x: f'[{x[0]}]({x[1]} "Check it on Spotify")', artists))
            )

        # Followers
        if type_ in ['artist', 'playlist']:
            em.add_field(
                name='Followers',
                value=result['followers']['total']
            )

        # Album
        if type_ == 'track':
            em.add_field(
                name='Album',
                value=f'[{result["name"]}]({result["album"]["external_urls"]["spotify"]} "Check it on Spotify")'
            )

        # Released
        if released:
            em.add_field(
                name='Released',
                value=released
            )

        # Tracks
        if type_ in ['playlist', 'album']:
            em.add_field(
                name='Tracks',
                value=str(result['tracks']['total'])
            )

        # Genres
        if genres:
            em.add_field(
                name='Genres',
                value=genres
            )

        # Popularity
        if type_ in ['track', 'artist', 'album']:
            em.add_field(
                name='Popularity',
                value=str(result['popularity'])
            )

        # Label
        elif type_ == 'album':
            em.add_field(
                name='Label',
                value=result['label']
            )

        # Spotify link
        if ex_url:
            em.add_field(
                name='Spotify',
                value=ex_url,
                inline=False
            )

        # YouTube link
        if type_ == 'track':
            # Lookup YouTube
            query = '{} {}'.format(result['name'], ' '.join(map(lambda x: x['name'], result['artists'])))
            yt = SearchVideos(
                query,
                mode='dict',
                max_results=1
            ).result()
            # noinspection PyTypeChecker
            yt = yt['search_result'][0]['link'] if yt else None
            em.add_field(
                name='YouTube',
                value=yt,
                inline=False
            )

        # Thumbnail
        if thumbnail:
            em.set_thumbnail(
                url=thumbnail
            )

        await ctx.send(embed=em)

        try:
            await ctx.message.delete()
        except Forbidden or NotFound or HTTPException:
            pass


def setup(bot):
    bot.add_cog(Utilities(bot))
