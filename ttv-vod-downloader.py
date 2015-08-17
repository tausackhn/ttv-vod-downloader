# coding=utf-8
""" Asynchronous twitch broadcast downloader """
__author__ = 'Kirill'

import argparse
import sys
import time
import os

from twitch_api import download_ids
from twitch_api import download_all
from twitch_api import parse_twitch_url


def get_id_list(path):
    id_list = []
    if os.path.exists(path):
        with open(path, 'r') as file:
            for line in file:
                url = parse_twitch_url(line)
                if url is None:
                    print('Incorrect: %s' % line)
                else:
                    id_list.append(url['id'])
    else:
        print('Path can not be resolved.')
    return id_list


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
                    default=True,
                    help='continue previous downloading, require "_finished" file in directory with finished vod '
                         '(default: %(default)s)')
parser.add_argument('url',
                    metavar='URL',
                    nargs='?',
                    help='an twitch vod url, ignore other arguments if declared')
parser.add_argument('-t', '--threads',
                    metavar='NUM',
                    type=int,
                    default=4,
                    help='number of downloading threads (default: %(default)s)')
parser.add_argument('-p', '--path',
                    metavar='PATH',
                    default='.',
                    help='path to directory where to save broadcasts')
parser.add_argument('--max_cache_size',
                    metavar='SIZE',
                    default=100,
                    help='maximal size of cache list, 1 corresponds to ~1MB (default: %(default)s)')
parser.add_argument('--urls_file',
                    metavar='FILE',
                    help='path to file with a list of urls, one per line.')

args = vars(parser.parse_args())

start = time.clock()
if args['url'] and args['ids'] and args['urls_file']:
    print('Require at least a broadcast url.\nShort manual: %s -h' % sys.argv[0])
    sys.exit(1)
try:
    if args['path']:
        os.chdir(args['path'])
    if args['url']:
        info = parse_twitch_url(args['url'])
        if info is None:
            print('Incorrect url passed.')
            sys.exit(1)
        else:
            if info['type'] == 'b':
                print('Old format broadcasts is not supported.')
                sys.exit(1)
            elif info['type'] == 'c':
                print('Old format highlights is not supported.')
                sys.exit(1)
            elif info['type'] == 'v':
                print('Downloading /v/%s...' % info['id'])
                download_ids([info['id']],
                             resume=args['continue'],
                             num_threads=args['threads'],
                             max_cache_size=args['max_cache_size'])
            else:
                print('Unsupported broadcast format.')
                sys.exit(1)
    elif args['urls_file']:
        urls = get_id_list(args['urls_file'])
        if not urls:
            print('No correct urls in file.')
        else:
            print('Download past broadcasts from %s...' % args['urls_file'])
            download_ids(urls,
                         resume=args['continue'],
                         num_threads=args['threads'],
                         max_cache_size=args['max_cache_size'])
    elif args['ids']:
        print('Download ids: ' + str(args['ids']).strip('[]') + '...')
        download_ids(args['ids'],
                     resume=args['continue'],
                     num_threads=args['threads'],
                     max_cache_size=args['max_cache_size'])
    elif args['channel_name']:
        print('Download vods from channel %s...\n' % args['channel_name'])
        download_all(args['channel_name'],
                     resume=args['continue'],
                     num_threads=args['threads'],
                     max_cache_size=args['max_cache_size'])

    print('\nTotal time taken: %.0f sec.' % (time.clock() - start))
except KeyboardInterrupt:
    pass
