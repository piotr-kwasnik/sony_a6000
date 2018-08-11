#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import glob
import shutil
import argparse
import textwrap

logging.basicConfig(
    format='[%(levelname)s] >>> %(message)s',
    level=logging.INFO,
    # filename='logfile.txt',
    # filemode='w'
)


class SonyAlphaFileSystemHandler(object):
    """
    Basic file operations for Sony Alfa camera
    """

    def __init__(self, src_dir, dest_dir=None):
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def extract_files(self, file_extension):
        """
        Move all files of particular type to proper destination dir
        """

        logging.debug('Running get_files() for: {}'.format(file_extension))

        file_format_dest_dirs = {'JPG': os.path.join(self.dest_dir, 'Photos', 'JPG'),
                                 'ARW': os.path.join(self.dest_dir, 'Photos', 'RAW'),
                                 'MTS': os.path.join(self.dest_dir, 'Movies')}

        if file_extension in file_format_dest_dirs:
            file_format_dest_dir = file_format_dest_dirs[file_extension]
        else:
            logging.error('File format not supported!')
            exit(1)

        if not os.path.exists(file_format_dest_dir):
            os.makedirs(file_format_dest_dir)

        for src_file in glob.iglob('{}/**/*.{}'.format(self.src_dir, file_extension), recursive=True):
            logging.debug('Moving file: {} -> {}'.format(src_file, file_format_dest_dir))
            shutil.move(src_file, file_format_dest_dir)

    def delete_pointless_raws(self):
        """
        Delete all ARW files without corresponding JPGs
        """

        pass


def configure_arg_parser():
    """
    Configure command line argument parser
    """

    class ArgParser(argparse.ArgumentParser):
        def error(self, message):
            if len(sys.argv) == 1:
                self.print_help()
            else:
                sys.stderr.write('error: %s\n' % message)
            sys.exit(1)

    arg_parser = ArgParser(formatter_class=argparse.RawTextHelpFormatter,
                           description='Sony Alpha File System Utility',
                           epilog=textwrap.dedent('''
                           exmamples:
                           - python sony_a6000_utility.py --reorganise /media/sd /home/pio/foto
                           - python sony_a6000_utility.py --delete-arw /home/pio/foto/jpg /home/pio/foto/arw
                           '''),
                           )

    excl_group = arg_parser.add_mutually_exclusive_group(required=True, )

    arg_parser.add_argument('-d', '--debug',
                            action='store_true',
                            required=False,
                            help='enable debug mode')

    excl_group.add_argument('-r', '--reorganise',
                            action='store_true',
                            help=textwrap.dedent('''\
                            reorganise camera file structure
                            positional arguments:
                            src_dir  - must point to directory containing Sony Alpha file structure
                            dest_dir - must point to target directory for new file structure
                            '''))
    excl_group.add_argument('-a', '--delete-arw',
                            action='store_true',
                            help=textwrap.dedent('''\
                            delete ARW files without corresponding JPGs
                            positional arguments:
                            src_dir  - must point to directory containing JPG files
                            dest_dir - must point to directory containing ARW files
                            '''))

    arg_parser.add_argument('src_dir',
                            type=str,
                            help='source directory path')

    arg_parser.add_argument('dest_dir',
                            type=str,
                            # nargs='?',
                            help='destination directory path')

    return arg_parser


if __name__ == '__main__':

    parser = configure_arg_parser()
    arguments = parser.parse_args()

    if arguments.debug:
        logging.basicConfig(level=logging.DEBUG)

    if arguments.reorganise:
        logging.info('Reorganising file structure...')
        alpha = SonyAlphaFileSystemHandler(arguments.src_dir, arguments.dest_dir)
        alpha.get_files('JPG')
        alpha.get_files('ARW')
        alpha.get_files('MTS')
