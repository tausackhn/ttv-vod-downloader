# TwitchTV VOD downloader
The downloader support new HLS video format (only). Example url with HLS broadcast:
`http://www.twitch.tv/mushisgosu/v/9794595`

Script realise asynchronous downloading of video chunks. This method is really faster than sequential downloading by ffmpeg.
## Usage
```
python ttv-vod-downloader.py [-h] [-i ID [ID ...] | -n NAME] [-c] [-t NUM]
                             [-p PATH] [--max_cache_size SIZE]
                             [ID]

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
                        number of downloading threads (default: 4)
  -p PATH, --path PATH  path to directory where to save broadcasts
  --max_cache_size SIZE
                        maximal size of cache list, 1 corresponds to ~1MB
                        (default: 100)
```
## Using examples
`python ttv-vod-downloader.py 9794595`

`python ttv-vod-downloader.py -c -n mushisgosu`

`python ttv-vod-downloader.py -i 9794595 9558360 9551422`
