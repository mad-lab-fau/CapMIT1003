import os
import warnings
from shutil import unpack_archive
from typing import Union
from urllib.request import urlretrieve

import pandas as pd
import sqlite3


class CapMIT1003:
    """
    Lightweight wrapper around CapMIT1003 SQLite3 database.

    It provides utility functions for loading labeled images with captions and their associated click paths. To use it,
    you first need to download the database from https://redacted.com/scanpath.db.
    """

    def __init__(self, db_path: Union[str, bytes, os.PathLike] = 'capmit1003.db',
                 img_path: Union[str, bytes, os.PathLike] = os.path.join('mit1003', 'ALLSTIMULI')):
        """

        Parameters
        ----------
        db_path: str or bytes or os.PathLike
            Path pointing to the location of the `scanpath.db` SQLite3 database.
        img_path: str or bytes or os.PathLike
            Path pointing to the location of the MIT1003 stimuli images.
        """
        self.db_path = db_path
        self.img_path = os.path.join(img_path, '')
        if not os.path.exists(db_path) and not os.path.isfile(db_path):
            warnings.warn('Could not find database at {}'.format(db_path))
        if not os.path.exists(img_path) and not os.path.isdir(img_path):
            warnings.warn('Could not find images at {}'.format(img_path))

    def __enter__(self):
        self.cnx = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, type, value, traceback):
        self.cnx.close()

    def get_captions(self) -> pd.DataFrame:
        """ Retrieve image-caption pairs of CapMIT1003 database.

        Returns
        -------
        pd.DataFrame
            Data frame with columns `obs_uid`, `usr_uid`, `start_time`, `caption`, `img_uid`, and `img_path`. See
            accompanying readme for full documentation of columns.
        """
        captions = pd.read_sql_query('SELECT * FROM captions o LEFT JOIN images i USING(img_uid)', self.cnx)
        captions['img_path'] = self.img_path + captions['img_path']
        return captions

    def get_click_path(self, obs_uid: str) -> pd.DataFrame:
        """ Retrieve click path for a specific image-caption pair.

        Parameters
        ----------
        obs_uid: str
            The unique id of the image-caption pair for which to retrieve the click path.

        Returns
        -------
        pd.DataFrame
            Data frame with columns `click_id`, `obs_uid`, `x`, `y`, and `click_time`. See accompanying readme for full
            documentation of columns.
        """
        return pd.read_sql_query('SELECT x, y, click_time AS time FROM clicks WHERE obs_uid = ?', self.cnx,
                                 params=[obs_uid])

    @staticmethod
    def download_images(quiet=False):
        """ Download stimuli images for MIT1003.

        Parameters
        ----------
        quiet: bool
            Flag that suppresses command-line outputs.
        """
        if not os.path.exists('mit1003'):
            if not os.path.exists('mit1003.zip'):
                print('Downloading MIT1003 Stimuli') if not quiet else None
                urlretrieve('http://people.csail.mit.edu/tjudd/WherePeopleLook/ALLSTIMULI.zip', 'mit1003.zip')
            print('Extracting MIT1003 Stimuli') if not quiet else None
            unpack_archive('mit1003.zip', 'mit1003')
