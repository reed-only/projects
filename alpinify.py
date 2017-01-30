"""
Build an Alpine-compatible MP3 USB drive.

This is applicable for Alpine CDE-135BT and likely other models.

Alpine will not recognize more than 100 folder or more than 100 files per folder.  This script transforms your locally
stored MP3 collection into a directory structure that is Alpine-compatible and still organized by band.

Assumptions:
  1. Given a music folder, files are organized by band_name --> album_name --> music_file_name
  2. Music files have extension .mp3
  3. Destination directory contains no conflicting directories

Procedure:
  1. Step through top level directories (band name).
  2. Step through second level directories (album name).
  3. Create a folder, if it does not exist, for the band and add the music files for each album.
  4. Music file name will be altered to include the album name.  Ex. Polly.mp3 becomes Nevermind-Polly.mp3
  5. If the music files in an album will overflow the max 100 files per folder, create a new folder with underscore and
     number.  Ex. Nirvana_2
  6. If maximum of 100 folders is reached, exit.

Usage: python alpinify.py -B "Nirvana" "Reel Big Fish"
"""

import os
import argparse
import shutil

MUSIC_DIR = '~/Music/Albums'
DESTINATION_DIR = '/Volumes/Alpine'
FILE_EXT = '.mp3'
MAX_FILES_PER_DIRECTORY = 100


def main():
    """
    Transfer MP3 files from local Music folder to destination folder, accounting for file count constraints
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-M', '--music_dir', type=str, default=MUSIC_DIR, help='Path to music directory')
    parser.add_argument('-D', '--dest_dir', type=str, default=DESTINATION_DIR, help='Path to destination directory')
    parser.add_argument('-B', '--bands', nargs='*', help='Optional space-separated list of bands to include')
    args = parser.parse_args()
    music_path = os.path.expanduser(args.music_dir)
    dest_path = os.path.expanduser(args.dest_dir)
    bands = args.bands

    band_directory_map = dict()

    # Walk through bands in music directory
    for band in os.listdir(music_path):
        band_path = os.path.join(music_path, band)

        # Check if band is a folder and if it's in the requested list of bands
        if os.path.isdir(band_path) and (not bands or band in bands):

            # Walk through albums in band directory
            for album in os.listdir(band_path):
                album_path = os.path.join(band_path, album)

                # Check if album is a folder
                if os.path.isdir(album_path):
                    songs_to_transfer = list()

                    # Walk through songs in album directory
                    for song in os.listdir(album_path):
                        song_path = os.path.join(album_path, song)

                        # Check if song is a file and has mp3 extension
                        if os.path.isfile(song_path) and song.lower().endswith(FILE_EXT):
                            songs_to_transfer.append((song_path, song))

                    # If we found songs to transfer, determine destination folder
                    if songs_to_transfer:
                        band_dest_directory = get_band_dest_directory(band, len(songs_to_transfer), band_directory_map)

                        # For each song, copy contents to new location, adding album name to song filename
                        for (song_path, song) in songs_to_transfer:
                            dest_directory = os.path.join(dest_path, band_dest_directory)
                            create_directory(dest_directory)
                            dest_song_path = os.path.join(dest_directory, album + '-' + song)
                            print song_path, '-->', dest_song_path
                            shutil.copy(song_path, dest_song_path)


def get_band_dest_directory(band, files_in_album, band_directory_map):
    """
    Update the band_directory_map and return the destination band name directory

    Nominally we take the band name directory as is, but when we exceed 100 files per directory, we create a new one
    with index appended.  Ex: Nirvana_2

    :param band: band name from source directory
    :param files_in_album: Number of song files in album directory
    :param band_directory_map: Map of band to {directory, folder_count, file_count}
    :return: destination band directory
    """
    if band not in band_directory_map:
        band_directory_map[band] = {
            'directory': band,
            'folder_count': 1,
            'file_count': files_in_album
        }
    file_count = band_directory_map[band]['file_count'] + files_in_album
    if file_count > MAX_FILES_PER_DIRECTORY:
        band_directory_map[band]['folder_count'] += 1
        band_directory_map[band]['file_count'] = files_in_album
        band_directory_map[band]['directory'] = band + '_' + str(band_directory_map[band]['folder_count'])
    else:
        band_directory_map[band]['file_count'] = file_count
    return band_directory_map[band]['directory']


def create_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


if __name__ == '__main__':
    main()
