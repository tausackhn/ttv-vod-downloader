""" Asynchronous twitch broadcast downloader """
__author__ = 'Kirill'

import argparse
import sys
from twitch_api import download_ids
from twitch_api import download_all

parser = argparse.ArgumentParser(description='Download the vod by id, all vods by channel name.')
group = parser.add_mutually_exclusive_group()
group.add_argument('-i', '--ids',
                   nargs='+',
                   type=int,
                   metavar='ID',
                   help='download vods by twitch ids')
group.add_argument('-n', '--channel_name',
                   metavar='NAME',
                   help='download all available vods by twitch channel name')
parser.add_argument('-c', '--continue',
                    action='store_true',
                    help='continue previous downloading, require "_finished" file in directory with finished vod')
parser.add_argument('id',
                    metavar='ID',
                    nargs='?',
                    type=int,
                    help='an twitch vod id, ignore other arguments if declared')

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = vars(parser.parse_args())
if args['id']:
    print('Downloading /v%i' % args['id'])
    download_ids([args['id']])
elif args['ids']:
    print('Downloading ids: ' + str(args['ids']).strip('[]'))
    if args['continue']:
        download_ids(args['ids'], resume=True)
    else:
        download_ids(args['ids'])
elif args['channel_name']:
    print('Downloading vods from channel %s' % args['channel_name'])
    if args['continue']:
        download_all(args['channel_name'], resume=True)
    else:
        download_all(args['channel_name'])
