import os
import shutil
import argparse
import time
import hashlib
import logging
from logging.handlers import RotatingFileHandler

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# check first length and last modification times, if they are the same, than check md5
def file_needs_update(src_file, dst_file):
    if not os.path.exists(dst_file):
        return True
    src_stat = os.stat(src_file)
    dst_stat = os.stat(dst_file)
    if src_stat.st_size != dst_stat.st_size or src_stat.st_mtime > dst_stat.st_mtime:
        return True
    return md5(src_file) != md5(dst_file)

def sync_folders(source, replica, skip_symlinks=True):
    for src_dir, dirs, files in os.walk(source):
        dst_dir = src_dir.replace(source, replica, 1)
        # Creating new directories
        if not os.path.exists(dst_dir):
            try:
                os.makedirs(dst_dir)
                shutil.copystat(src_dir, dst_dir)
                logging.info(f"Directory created: {dst_dir}")
            except OSError as e:
                logging.error(f"Failed to create directory {dst_dir}: {e}")
                continue  # Skip to the next directory

        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if skip_symlinks and (os.path.islink(src_file) or not os.path.isfile(src_file)):
                continue  # Skip symbolic links and special files based on the argument
            try:
                if file_needs_update(src_file, dst_file):
                    shutil.copy2(src_file, dst_file)
                    logging.info(f"Copied: {src_file} to {dst_file}")
            except Exception as e:
                logging.error(f"Error copying {src_file} to {dst_file}: {e}")


    # removing files
    for rep_dir, dirs, files in os.walk(replica):
        src_dir = rep_dir.replace(replica, source, 1)
        for file_ in files:
            rep_file = os.path.join(rep_dir, file_)
            src_file = os.path.join(src_dir, file_)
            if not os.path.exists(src_file):
                try:
                    os.remove(rep_file)
                    logging.info(f"Removed: {rep_file}")
                except Exception as e:
                    logging.error(f"Error removing {rep_file}: {e}")
    # removing old directories, all files in them were removed in previous step
    for rep_dir, dirs, files in os.walk(replica, topdown=False):
        src_dir = rep_dir.replace(replica, source, 1)
        if not os.path.exists(src_dir):
            try:
                os.rmdir(rep_dir)
                logging.info(f"Removed directory: {rep_dir}")
            except OSError as e:
                logging.error(f"Error removing directory {rep_dir}: {e}")


def setup_logging(log_file):
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Log file path")
    parser.add_argument("--skip-symlinks", action='store_true', help="Skip symbolic links and special files")
    args = parser.parse_args()

    setup_logging(args.log_file)

    while True:
        sync_folders(args.source, args.replica, args.skip_symlinks)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()