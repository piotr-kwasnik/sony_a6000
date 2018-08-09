#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import glob
import shutil

logging.basicConfig(
    format='[%(levelname)s] >>> %(message)s',
    level=logging.DEBUG,
    filename='logfile.txt',
    filemode='w'
)


class SonyAlphaFileHandler(object):
    """
    Basic file operations for Sony Alfa camera
    """

    def __init__(self, src_dir, dest_dir):
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def get_files(self, file_extension):
        """
        Move all files of particular type to proper destination dir
        """

        logging.debug('Running get_files() for: {}'.format(file_extension))

        file_format_dest_dirs = {'JPG': os.path.join(self.dest_dir, 'Photos', 'JPG'),
                                 'ARW': os.path.join(self.dest_dir, 'Photos', 'RAW'),
                                 'MTS': os.path.join(self.dest_dir, 'Movies'),
        }

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


if __name__ == '__main__':

    src_dir = '/media/pio/Data&Foto_Slave/SD_2'
    dest_dir = '/media/pio/Data&Foto_Slave/cool'

    alpha = SonyAlphaFileHandler(src_dir, dest_dir)
    alpha.get_files('JPG')
    alpha.get_files('ARW')
    alpha.get_files('MTS')
