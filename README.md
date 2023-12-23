# VEEAM sync scripts task

This repository contains two Python scripts designed for synchronizing files and directories from a source folder to a replica (destination) folder. 

## Scripts

1. **sync-loop.py**: This script is designed to run continuously in a loop, with a specified interval between synchronization operations.
2. **sync-cron.py**: This script also runs in a loop, but is intended to be run via cron. It includes a mechanism to prevent concurrent executions. It also loops indifinitely, but if the process crashes for whatewer reason, it can be restarted automatically via cron. This is in my opinion prefferable way to do periodical syncs.

## Features

- **Synchronization**: Synchronizing the directories and file from source to replica.
- **Logging**: All operations (file copying, file removal, etc.) are logged in logfile.
- **Optimized MD5 Checksums**: The scripts uses filesize and time of last modification to detect if the files have been modified in order to reduce the amount of MD5 hashes the scripts need to calculate. The md5 of files is calculated only if the filesize and time of last modification are the same in source and replica.
- **Skip Symbolic Links**: An optional flag allows the scripts to skip symbolic links and special files, which can be useful in certain synchronization contexts. Prevents for example infinite loops, if the device file the directory is stored in the sync directory.

## Usage

### sync-loop.py

` python sync-loop.py <source> <replica> <interval> <log_file> [--skip-symlinks] `

- `source`: Path to the source directory.
- `replica`: Path to the replica directory.
- `interval`: Time in seconds between synchronization operations.
- `log_file`: Path to the log file.
- `--skip-symlinks`: Optional flag to skip symbolic links and special files.

### sync-cron.py

` python sync-cron.py <source> <replica> <interval> <log_file> [--skip-symlinks] `

- The arguments are the same as `sync-loop.py`.
