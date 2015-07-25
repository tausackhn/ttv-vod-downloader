# coding=utf-8
""" Asynchronous twitch broadcast downloader """
__author__ = 'Kirill'

import argparse
import sys
from twitch_api import download_ids
from twitch_api import download_all
import time
import os

parser = argparse.ArgumentParser(description='Download specific Twitch broadcasts by id or all from specific channel.')
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
parser.add_argument('-t', '--threads',
                    metavar='NUM',
                    type=int,
                    default=20,
                    help='number of downloading threads (default: %(default)s)')
parser.add_argument('-p', '--path',
                    metavar='PATH',
                    default='.',
                    help='path to directory where to save broadcasts')

args = vars(parser.parse_args())
start = time.clock()

if args['id'] is None and args['ids'] is None:
    print('At least one id required.\nUsage: %s --help' % sys.argv[0])
    sys.exit(1)

if args['path']:
    os.chdir(args['path'])
if args['id']:
    print('Download v%i...\n' % args['id'])
    download_ids([args['id']], resume=args['continue'], num_threads=args['threads'])
elif args['ids']:
    print('Download ids: ' + str(args['ids']).strip('[]') + '...\n')
    download_ids(args['ids'], resume=args['continue'], num_threads=args['threads'])
elif args['channel_name']:
    print('Download vods from channel %s...\n' % args['channel_name'])
    download_all(args['channel_name'], resume=args['continue'], num_threads=args['threads'])

print('\nTotal time taken: %.0f sec.' % str(time.clock() - start))
