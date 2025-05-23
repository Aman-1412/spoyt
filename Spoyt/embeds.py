# -*- coding: utf-8 -*-
from discord import Embed, Color

from Spoyt.api.spotify import Playlist, Track
from Spoyt.api.youtube import YouTubeVideo, YoutubeMusic
from Spoyt.settings import MAX_QUERY
from Spoyt.utils import markdown_url


YOUTUBE_COLOR = Color.from_rgb(255, 0, 0)
YOUTUBE_MUSIC_COLOR = Color.from_rgb(255, 28, 119)


class BaseEmbed(Embed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.color = Color.blurple()

# Searching

class SearchingEmbed(BaseEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = '\u23f3 Searching platform'


class SearchingSpotify(SearchingEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = '\u23f3 Searching Spotify'


class SearchingYouTube(SearchingEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = '\u23f3 Searching YouTube'

# Unreachable

class UnreachableEmbed(BaseEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Oh no'
        self.description = 'Platform is out of service.'
        self.color = Color.red()


class SpotifyUnreachableEmbed(UnreachableEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.description = 'Spotify is out of service.'


class YouTubeUnreachableEmbed(UnreachableEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.description = 'YouTube is out of service.'

# Not found

class NotFoundEmbed(BaseEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Content not found'
        self.color = Color.red()


class VideoNotFound(NotFoundEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Video not found'


class SpotifyTrackNotFoundEmbed(NotFoundEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Spotify track not found'


class SpotifyPlaylistkNotFoundEmbed(NotFoundEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Spotify playlist not found'

# Other errors

class ErrorEmbed(BaseEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'There was an error'
        self.color = Color.red()


class CommandOnCooldownEmbed(ErrorEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Command on cooldown'

class IncorrectInputEmbed(ErrorEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.description = 'Your input is incorrect.'

# Other embeds, with no errors

class SpotifyTrackEmbed(BaseEmbed):
    def __init__(self, track: Track, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = track.name
        self.description = markdown_url(track.track_url)
        self.color = Color.green()
        self.set_thumbnail(url=track.cover_url)
        self.add_field(
            name='Artist{}'.format('' if track.is_single_artist else 's'),
            value=', '.join(track.artists),
            inline=track.is_single_artist
        )
        self.add_field(
            name='Released',
            value=track.release_date
        )


class SpotifyPlaylistEmbed(BaseEmbed):
    def __init__(self, playlist: Playlist, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if (d := playlist.description):
            description = f'{d}\n\n{playlist.url}'
        else:
            description = playlist.url
        self.title = playlist.name
        self.description = description
        self.color = Color.green()
        self.set_thumbnail(url=playlist.cover_url)
        self.set_author(
            name=playlist.owner.name,
            url=playlist.owner.user_url,
            icon_url=playlist.owner.avatar_url
        )
        first_tracks = '\n'.join(map(
            lambda a: f'- {markdown_url(a.track_url, a.name)}',
            playlist.tracks[:MAX_QUERY]
        ))
        if (tr := playlist.total_tracks) > MAX_QUERY:
            first_tracks += f'\nAnd {tr - MAX_QUERY} more.'
        self.add_field(
            name='Tracks',
            value=first_tracks
        )


class YouTubeVideoEmbed(BaseEmbed):
    def __init__(self, video: YouTubeVideo, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title=video.title
        self.description=markdown_url(video.video_link)
        self.color = YOUTUBE_COLOR
        self.set_thumbnail(url=video.video_thumbnail)
        self.add_field(
            name='Description',
            value=video.description,
            inline=False
        )
        self.add_field(
            name='Published',
            value=video.published_date
        )

class YouTubeMusicEmbed(BaseEmbed):
    def __init__(self, ytm_result: YoutubeMusic, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title=ytm_result.title
        self.description=markdown_url(ytm_result.track_link)
        self.color = YOUTUBE_MUSIC_COLOR
        self.set_thumbnail(url=ytm_result.thumbnail)
        self.add_field(
            name='Artist{}'.format('' if len(ytm_result.artists) == 1 else 's'),
            value=', '.join(ytm_result.artists),
        )

class TitleResponseEmbed(BaseEmbed):
    def __init__(self, track_details: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = track_details

class UnderConstructionEmbed(BaseEmbed):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = 'Function under construction'
        self.color = Color.gold()
