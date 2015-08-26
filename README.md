TwitchTV VOD downloader
========
The downloader support new HLS video format (only). Example url with HLS broadcast:
`http://www.twitch.tv/mushisgosu/v/9794595`

Latest builds: ![Windows](https://github.com/tausackhn/ttv-vod-downloader/releases/latest)

Script realise asynchronous downloading of video chunks. This method is really faster than sequential downloading by ffmpeg.
Broadcasts will be downloaded in separate folders 
`./{channel_name}/{vod_id}/` 
in a `{vod_id}.ts` file, `info.txt` with json info and `_finished` file if downloading has been finished.
Later you can easily convert *.ts files in another with ffmpeg.
### Usage
```
python ttv-vod-downloader.py [-h] [-i ID [ID ...] | -n NAME] [-r] [-t NUM]
                             [-p PATH] [--max_cache_size SIZE]
                             [--urls_file FILE]
                             [URL]

Download Twitch broadcasts by url or ids list or all vods from specific
channel.

positional arguments:
  URL                   an twitch vod url, ignore other arguments if declared

optional arguments:
  -h, --help            show this help message and exit
  -i ID [ID ...], --ids ID [ID ...]
                        download vods by twitch ids
  -n NAME, --channel_name NAME
                        download all available vods by twitch channel name
  -r, --reload          ignore finished broadcasts, if _finished file exists
                        (default: False)
  -t NUM, --threads NUM
                        number of downloading threads (default: 4)
  -p PATH, --path PATH  path to directory where to save broadcasts
  --max_cache_size SIZE
                        maximal size of cache list, 1 corresponds to ~1MB
                        (default: 100)
  --urls_file FILE      path to file with a list of urls, one per line.
```
### Using examples
`python ttv-vod-downloader.py http://www.twitch.tv/guit88man/v/11188942`

`python ttv-vod-downloader.py -r -n mushisgosu`

`python ttv-vod-downloader.py -i 9794595 9558360 9551422`

`python ttv-vod-downloader.py --url_file best_vods.txt`

### Credits
Special thanks:
* Tester who wants to remain anonymous.
