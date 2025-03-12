# Changes in the fork

- uv package management
- env management via .env file (Copy .env.example to .env and fill the values)
- Track conversions between:
  - Spotify -> YouTube and YouTube Music
  - YouTube -> Spotify and YouTube Music
  - YouTube Music -> Spotify and YouTube
- (Try to) choose optimal Music and Video respectively for YouTube Music and YouTube Video
- Handle some edge cases around YouTube video detection (may not be 100% accurate)
- Better thumbnails for each platform
- Fixed a couple of typos
- The code is pretty unoptimized, as it was written in a couple of hours:
  - no try/excepts where I should have used them lol
  - no proper type hinting
  - code duplication
  - had to use `ctx.defer()` because of long wait times due to multiple YouTube calls
  - I'll fix these when I have time (inb4: never happening)


***


# Spoyt

Discord bot that allows you to "convert" Spotify links to YouTube videos.

### ...but, why?

The project was created out of necessity. On a certain server there was a group of people using Spotify and another group using YouTube (Music). The first group could share songs with each other without hindrance. For this, the second could only theoretically listen to songs from Spotify, but in practice with great limitations and difficulties. That's when the idea for this bot was conceived. With this project, a group of Spotify users can share songs for both groups at once.

## Usage

1. Invite the bot with this link: <https://discord.com/api/oauth2/authorize?client_id=948274806325903410&permissions=2147485696&scope=bot%20applications.commands>.

1. Use `/track` or `/playlist` command to search. Bot will try to find the track or playlist (respectively) using Spotify API, and search it in YouTube (also using API).

### Note

YouTube searching currently applies only to `/track`. I'm currently working on [YouTube API connector](https://github.com/AnonymousX86/yt-api).

## Support

You can join my server: <https://discord.gg/SRdmrPpf2z>.

