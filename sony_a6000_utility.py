#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import glob
import shutil
import argparse
import textwrap
import collections

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

        if os.path.exists(file_format_dest_dir):
            logging.error('Destination directory already exists...')
            exit(1)
        else:
            logging.debug('Crating destination directory: {}'.format(file_format_dest_dir))
            if not arguments.dry_run:
                os.makedirs(file_format_dest_dir)

        glob_pattern = '{}/**/*.{}'.format(self.src_dir, file_extension)
        file_paths = [src_file for src_file in glob.iglob(glob_pattern, recursive=True)]
        # file_paths.sort(key=lambda x: os.path.getmtime(x))
        file_paths.sort(key=os.path.getmtime)

        file_names = [os.path.basename(path) for path in file_paths]

        if len(file_names) == len(set(file_names)):
            logging.debug('There are no duplicates for {}'.format(file_extension))
        else:
            print(['{}->{}'.format(item, count) for item, count in collections.Counter(file_names).items() if count > 1])

        for path in file_paths:
            stat_info = os.stat(path)
            logging.debug('File {} --- created ---> {}'.format(path, time.ctime(stat_info.st_mtime)))

            # dest_file = os.path.join(file_format_dest_dir, os.path.basename(src_file))
            # logging.debug('Checking existence of destination file: {}'.format(dest_file))
            # tmp_dest_file = self._check_dest_file(dest_file)
            #
            # if dest_file != tmp_dest_file:
            #     dest_file = tmp_dest_file
            #     logging.debug('Moving file (update): {} -> {}'.format(src_file, dest_file))
            #
            # if not arguments.dry_run:
            #     shutil.move(src_file, dest_file)

    def _check_dest_file(self, file_path):
        if os.path.exists(file_path):
            logging.critical('Destination path already exists: {}'.format(file_path))

            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            file_base, file_extension = os.path.splitext(file_name)

            # Incrementing the digit part of file name
            if file_extension == '.MTS':
                # 00000.MTS -> 00001.MTS
                new_file_name = '{:05d}.MTS'.format(int(file_base) + 1)
            else:
                raise NotImplementedError
                # DSC05366.JPG
                # DSC05366.ARW

            new_file_path = os.path.join(file_dir, new_file_name)
            logging.debug('Checking {}'.format(new_file_path))
            return self._check_dest_file(new_file_path)

        else:
            return file_path

    def delete_pointless_raws(self):
        """
        Delete all ARW files without corresponding JPGs
        """

        logging.debug('Running delete_pointless_raws()')

        for dest_file in glob.iglob('{}/*.{}'.format(self.dest_dir, 'ARW')):
            dest_file_name = os.path.basename(dest_file)
            dest_file_base, dest_file_extension = os.path.splitext(dest_file_name)
            jpg_equivalent_file = os.path.join(self.src_dir, '{}.{}'.format(dest_file_base, 'JPG'))

            if not os.path.exists(jpg_equivalent_file):
                logging.debug('Deleting ARW file without corresponding JPG: {}'.format(dest_file))
                if not arguments.dry_run:
                    os.remove(dest_file)


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

    epilog = textwrap.dedent('''
             exmamples:
             - python sony_a6000_utility.py --reorganise /media/sd /home/pio/album
             - python sony_a6000_utility.py --delete-arw /home/pio/album/Photos/JPG /home/pio/album/Photos/RAW''')

    arg_parser = ArgParser(formatter_class=argparse.RawTextHelpFormatter,
                           description='Sony Alpha File System Utility',
                           epilog=epilog)

    excl_group = arg_parser.add_mutually_exclusive_group(required=True)

    arg_parser.add_argument('-d', '--debug',
                            action='store_true',
                            required=False,
                            help='enable debug mode')

    arg_parser.add_argument('-n', '--dry_run',
                            action='store_true',
                            required=False,
                            help='enable dry run mode')

    excl_group.add_argument('-r', '--reorganise',
                            action='store_true',
                            help=textwrap.dedent('''\
                            reorganise camera file structure
                            positional arguments:
                            src_dir  - must point to directory containing Sony Alpha file structure
                            dest_dir - must point to target directory for new file structure
                            '''))

    excl_group.add_argument('-a', '--delete_arw',
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
        logging.getLogger().setLevel(logging.DEBUG)

    if arguments.dry_run:
        logging.info('Dry run mode enabled...')

    if arguments.reorganise:
        logging.info('Reorganising file structure...')
        alpha = SonyAlphaFileSystemHandler(arguments.src_dir, arguments.dest_dir)
        # alpha.extract_files('JPG')
        # alpha.extract_files('ARW')
        alpha.extract_files('MTS')

    if arguments.delete_arw:
        logging.info('Deleting pointless ARW files...')
        alpha = SonyAlphaFileSystemHandler(arguments.src_dir, arguments.dest_dir)
        alpha.delete_pointless_raws()


os.scandir()