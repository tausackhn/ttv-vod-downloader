# ttv-vod-downloader
Twitch broadcast downloader which support new HLS video format.

Script realise asynchronous downloading of video chunks. This method is really faster than sequential downloading by ffmpeg.
```
Usage: ttv-vod-downloader.py [-h] [-i ID [ID ...] | -n NAME] [-c] [-t NUM] [ID]

positional arguments:
  ID                    an twitch vod id, ignore other arguments if declared

optional arguments:
  -h, --help            show this help message and exit
  -i ID [ID ...], --ids ID [ID ...]
                        download vods by twitch ids
  -n NAME, --channel_name NAME
                        download all available vods by twitch channel name
  -c, --continue        continue previous downloading, require "_finished"
                        file in directory with finished vod
  -t NUM, --threads NUM
                        number of downloading threads (default: 20)
```
