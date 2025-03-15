# -*- coding: utf-8 -*-
from typing import Optional
from urllib.parse import parse_qs, urlparse
from json import loads as json_loads
from pathlib import Path

from requests import get as requests_get
from ytmusicapi import YTMusic, OAuthCredentials

from Spoyt.exceptions import YouTubeException, YouTubeForbiddenException
from Spoyt.logger import log
from Spoyt.settings import YOUTUBE_API_KEY, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET

if Path("oauth.json").exists():
    log.info("Found oauth.json")
    ytmusic = YTMusic("oauth.json", oauth_credentials=OAuthCredentials(client_id=OAUTH_CLIENT_ID, client_secret=OAUTH_CLIENT_SECRET))
else:
    log.info("No auth.json found. Skipping auth")
    ytmusic = YTMusic()

class YouTubeVideo:
    def __init__(self, payload: dict) -> None:
        snippet: dict = payload.get('snippet', {})
        self.video_id: str = payload.get('id', {}).get('videoId', '')
        self.title: str = snippet.get('title')
        self.description: str = snippet.get('description')[:100] + '...'
        self.published_date: str = snippet.get('publishTime', snippet.get('publishedAt', 'xxxx-xx-xx'))[:10]

    @property
    def video_link(self) -> str:
        return f'https://www.youtube.com/watch?v={self.video_id}'

    @property
    def video_thumbnail(self) -> str:
        return f'https://i.ytimg.com/vi/{self.video_id}/0.jpg'


class YoutubeMusic:
    def __init__(self, yt_search_result: Optional[dict] = None) -> None:
        if yt_search_result is None:
            pass
        else:
            self.track_id: str = yt_search_result['videoId']
            self.track_link: str = f"https://music.youtube.com/watch?v={self.track_id}"
            self.title: str = yt_search_result['title']
            self.thumbnail: str = yt_search_result['thumbnails'][0]['url'].split('=')[0]
            self.artists: list[str]  = [artist['name'] for artist in yt_search_result['artists']]



# Priority Order:
# Video given by user
# Official Video among the search results
# Top search result that is an OMV
# Top search result

def search_video(query: str, given_video_id: str=None) -> YouTubeVideo:
    # If user provided a video, prioritize that
    if given_video_id:
        log.info(f'Getting details for YouTube video with id: "{given_video_id}"')
        yt_r = requests_get(
            'https://www.googleapis.com/youtube/v3/videos'
            '?key={}'
            '&part=snippet'
            '&id={}'.format(YOUTUBE_API_KEY, given_video_id)
        )
        yt_video = json_loads(yt_r.content).get('items', [{}])[0]
        yt_video['id'] = {'videoId': yt_video['id']}

    else:
        log.info(f'Searching YouTube: "{query}"')
        yt_r = requests_get(
            'https://www.googleapis.com/youtube/v3/search'
            '?key={}'
            '&part=snippet'
            '&maxResults=5'
            '&q={}'.format(YOUTUBE_API_KEY, query)
        )
        yt_response_json = json_loads(yt_r.content)

        omv_videos = []
        official_video = {}
        for yt_result in yt_response_json.get('items', [{}]):
            video_id = yt_result.get('id', {}).get('videoId')
            #  Only process videos. This API also returns playlists and channels, ignore those.
            if video_id is None:
                continue
            video_type = ytmusic.get_song(video_id)['videoDetails'].get('musicVideoType', '')
            # Only choose Original Music Video
            if video_type == 'MUSIC_VIDEO_TYPE_OMV':
                omv_videos.append(yt_result)
            # Prioritize if the video title contains 'Official Video'
            if 'Official Video' in yt_result['snippet']['title']:
                official_video = yt_result
                log.info("Found official video")
                break
        yt_video = official_video if len(official_video) != 0 else yt_response_json.get('items', [{}])[0] if len(omv_videos) == 0 else omv_videos[0]

    if (error_code := yt_r.status_code) == 200:
        video = YouTubeVideo(yt_video)
        log.info(f'Found YouTube video "{video.title}" ({video.video_link})')
    elif error_code == 403:
        log.critical(yt_video['error']['message'])
        raise YouTubeForbiddenException
    else:
        log.error(yt_video['error']['message'])
        raise YouTubeException
    return video


def search_youtube_music_by_name(query: str) -> YoutubeMusic:
    log.info(f'Searching Youtube Music: "{query}"')
    yt_search_results = ytmusic.search(query, filter='songs')[:5]
    yt_search_result = [x for x in yt_search_results if x['videoType'] == 'MUSIC_VIDEO_TYPE_ATV'][0]

    log.info(f"Found Youtube Music details for id - {yt_search_result['videoId']}")
    return YoutubeMusic(yt_search_result)

def search_youtube_music_by_id(video_id: str):
    log.info(f"Searching Youtube Music for id - {video_id}")

    ytm_track_details = ytmusic.get_song(video_id)
    ytm_details  = YoutubeMusic()
    ytm_details.track_id = video_id
    ytm_details.track_link = f"https://music.youtube.com/watch?v={video_id}"
    ytm_details.title = ytm_track_details['videoDetails']['title']
    ytm_details.artists = ytm_track_details['videoDetails']['author'].split(' & ')
    ytm_details.thumbnail = ytm_track_details['videoDetails']['thumbnail']['thumbnails'][0]['url'].split('=')[0]

    log.info(f"Found Youtube Music details for link - {ytm_details.track_link}")
    return ytm_details


def youtube_url_to_id(url: str) -> str:
    log.info(f"Converting youtube url - {url} to id")
    return parse_qs(urlparse(url).query)["v"][0]
