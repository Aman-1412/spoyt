# -*- coding: utf-8 -*-

from dotenv import load_dotenv

load_dotenv()

from os import getenv

BOT_TOKEN: str = getenv('BOT_TOKEN')

# Maximum, visible tracks in playlist
MAX_QUERY: int = int(getenv('MAX_QUERY', 10))

SPOTIFY_CLIENT_ID: str = getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET: str = getenv('SPOTIFY_CLIENT_SECRET')

YOUTUBE_API_KEY: str = getenv('YOUTUBE_API_KEY')
OAUTH_CLIENT_ID: str = getenv('OAUTH_CLIENT_ID','')
OAUTH_CLIENT_SECRET: str = getenv('OAUTH_CLIENT_SECRET','')
