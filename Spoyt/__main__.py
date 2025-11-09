# -*- coding: utf-8 -*-
from logging import INFO, basicConfig
from urllib.parse import urlparse

from discord import ApplicationContext, Bot, DiscordException, Option
from discord.ext.commands import BucketType, cooldown, CommandOnCooldown
from rich.logging import RichHandler

from Spoyt.api.spotify import search_track, search_playlist, url_to_id, search_track_by_name_and_artist
from Spoyt.api.youtube import search_video,  \
    youtube_url_to_id, search_youtube_music_by_name, search_youtube_music_by_id
from Spoyt.embeds import CommandOnCooldownEmbed, ErrorEmbed, IncorrectInputEmbed, SpotifyPlaylistkNotFoundEmbed, \
    SpotifyTrackEmbed, \
    SpotifyPlaylistEmbed, SpotifyTrackNotFoundEmbed, SpotifyUnreachableEmbed, YouTubeVideoEmbed, \
    UnderConstructionEmbed, YouTubeMusicEmbed, TitleResponseEmbed
from Spoyt.exceptions import SpotifyNotFoundException, SpotifyUnreachableException, YouTubeException
from Spoyt.logger import log
from Spoyt.settings import BOT_TOKEN
from Spoyt.utils import check_env

if __name__ == '__main__':
    basicConfig(
        level=INFO,
        format='%(message)s',
        datefmt='[%x]',
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    if not check_env():
        log.critical('Aborting start')
        exit()

    log.info('Starting Discord bot')

    bot = Bot()

    @bot.event
    async def on_ready() -> None:
        log.info(f'Logged in as "{bot.user}"')

    @bot.event
    async def on_application_command_error(
        ctx: ApplicationContext,
        exception: DiscordException
    ) -> None:
        if isinstance(exception, CommandOnCooldown):
            await ctx.respond(embed=CommandOnCooldownEmbed(
                description=f'Retry in {int(exception.retry_after)} second(s).'
            ))
        else:
            raise exception

    @bot.slash_command(
        name='track',
        description='Search for a track'
    )
    @cooldown(1, 5.0, BucketType.guild)
    async def track(
        ctx: ApplicationContext,
        url: Option(
            input_type=str,
            name='url',
            description='Starts with "https://open.spotify.com/track/..."',
            required=True
    )) -> None:
        # YOUTUBE MUSIC
        if urlparse(url).hostname.replace('www.', '') == 'music.youtube.com':
            log.info(f"Received a Youtube Music link - {url}")
            await ctx.defer()
            ytm_details = search_youtube_music_by_id(youtube_url_to_id(url))
            youtube_query = '{} {}'.format(ytm_details.title, ' '.join(ytm_details.artists))

            try:
                spotify_track = search_track_by_name_and_artist(ytm_details.title, " ,".join(ytm_details.artists))
            except SpotifyNotFoundException:
                await ctx.respond(embed=SpotifyTrackNotFoundEmbed())
                return
            except SpotifyUnreachableException:
                await ctx.respond(embed=SpotifyUnreachableEmbed())
                return

            try:
                youtube_result = search_video(youtube_query)
            except YouTubeException as e:
                await ctx.channel.send(embed=ErrorEmbed(
                    description=f'```diff\n- {e}\n```'
                ))
                return

            # await ctx.respond("\u200b")
            # await ctx.respond(f"{" ,".join(ytm_details.artists)} - {ytm_details.title}")

            await ctx.respond(embed=TitleResponseEmbed(f"{' ,'.join(spotify_track.artists)} - {spotify_track.name}"))

            await ctx.channel.send(embed=YouTubeMusicEmbed(ytm_details))
            await ctx.channel.send(embed=YouTubeVideoEmbed(youtube_result))
            await ctx.channel.send(embed=SpotifyTrackEmbed(spotify_track))
            await ctx.channel.send(spotify_track.track_url)

            log.info(f'Successfully converted {url}')

            return

        # YOUTUBE
        if urlparse(url).hostname.replace('www.', '') in ('youtube.com', 'youtu.be'):
            log.info(f"Received a Youtube video link - {url}")
            await ctx.defer()
            youtube_video_id = youtube_url_to_id(url)
            # Search YouTube Music for the YouTube video
            ytm_details = search_youtube_music_by_id(youtube_video_id)

            # Search again, we rely on YouTube Music to give us the correct song
            youtube_query = '{} {}'.format(ytm_details.title, ' '.join(ytm_details.artists))
            ytm_details = search_youtube_music_by_name(youtube_query)


            try:
                spotify_track = search_track_by_name_and_artist(ytm_details.title, " ,".join(ytm_details.artists))
            except SpotifyNotFoundException:
                await ctx.respond(embed=SpotifyTrackNotFoundEmbed())
                return
            except SpotifyUnreachableException:
                await ctx.respond(embed=SpotifyUnreachableEmbed())
                return

            try:
                youtube_result = search_video(youtube_query, given_video_id=youtube_video_id)
            except YouTubeException as e:
                await ctx.channel.send(embed=ErrorEmbed(
                    description=f'```diff\n- {e}\n```'
                ))
                return

            await ctx.respond(embed=TitleResponseEmbed(f"{' ,'.join(spotify_track.artists)} - {spotify_track.name}"))

            await ctx.channel.send(embed=YouTubeMusicEmbed(ytm_details))
            await ctx.channel.send(embed=YouTubeVideoEmbed(youtube_result))
            await ctx.channel.send(embed=SpotifyTrackEmbed(spotify_track))
            await ctx.channel.send(spotify_track.track_url)

            log.info(f'Successfully converted {url}')

            return

        # NON-YOUTUBE OR SPOTIFY
        if not url.startswith('https://open.spotify.com/track/'):
            await ctx.respond(embed=IncorrectInputEmbed())
            return

        # SPOTIFY
        log.info(f"Received a Spotify link - {url}")
        await ctx.defer()
        track_id = url_to_id(url)
        try:
            spotify_track = search_track(track_id)
        except SpotifyNotFoundException:
            await ctx.respond(embed=SpotifyTrackNotFoundEmbed())
            return
        except SpotifyUnreachableException:
            await ctx.respond(embed=SpotifyUnreachableEmbed())
            return

        youtube_query = '{} {}'.format(spotify_track.name, ' '.join(spotify_track.artists))
        try:
            youtube_result = search_video(youtube_query)
        except YouTubeException as e:
            await ctx.channel.send(embed=ErrorEmbed(
                description=f'```diff\n- {e}\n```'
            ))
            return

        try:
            ytm_details = search_youtube_music_by_name(youtube_query)
        except YouTubeException as e:
            await ctx.channel.send(embed=ErrorEmbed(
                description=f'```diff\n- {e}\n```'
            ))
            return

        await ctx.respond(embed=TitleResponseEmbed(f"{' ,'.join(spotify_track.artists)} - {spotify_track.name}"))
        await ctx.channel.send(embed=YouTubeMusicEmbed(ytm_details))
        await ctx.channel.send(embed=YouTubeVideoEmbed(youtube_result))
        await ctx.channel.send(embed=SpotifyTrackEmbed(spotify_track))
        await ctx.channel.send(spotify_track.track_url)

        log.info(f'Successfully converted {url}')

    @bot.slash_command(
        name='playlist',
        description='Search for a playlist'
    )
    @cooldown(1, 30.0, BucketType.guild)
    async def playlist(
        ctx: ApplicationContext,
        url: Option(
            input_type=str,
            name='url',
            description='Starts with "https://open.spotify.com/playlist/..."',
            required=True
        )
    ) -> None:
        if not url.startswith('https://open.spotify.com/playlist/'):
            await ctx.respond(embed=IncorrectInputEmbed())
            return

        playlist_id = url_to_id(url)
        try:
            playlist = search_playlist(playlist_id)
        except SpotifyNotFoundException:
            await ctx.respond(embed=SpotifyPlaylistkNotFoundEmbed())
            return
        except SpotifyUnreachableException:
            await ctx.respond(embed=SpotifyUnreachableEmbed())
            return

        await ctx.respond(embed=SpotifyPlaylistEmbed(playlist))

        await ctx.channel.send(embed=UnderConstructionEmbed(
            description='YouTube searching is currently available only for `/track`.'
        ))
        log.info('Playlist conversion issued.')

    bot.run(BOT_TOKEN)
