## Overview

A Playwright script which automates the process of playing multiple YouTube videos from multiple accounts, liking them, commenting on them, and setting the video quality to 144p. This script uses Playwright to interact with the YouTube website and perform the following actions:

- Play a video
- Skip ads
- Like a video
- Comment on a video
- Mute a video
- Set video quality to 144p
- Checks if full video have been played

## Inputs

The script requires the following inputs:

- VIDEOS_LIST: a list of YouTube video URLs to play
- LIKE_VALUE: a boolean value to determine whether to like the video or not
- COMMENT_VALUE: a boolean value to determine whether to comment on the video or not

## Functions

The script contains the following functions:

### is_fully_played

This function checks if the video has been fully played and closes the page if it has. It takes a page object as input and returns a boolean value.

### random_comment_generator

This function generates a random comment from a list of fixed adjectives, nouns, and emojis. It returns a string.

### mute_video

This function tries to mute the video. It takes a page object as input and returns None.

### set_quality_144p

This function sets the quality of the video to 144p to save resources. It takes a page object as input and returns None.

### add_comment

This function adds a comment to the video. It takes a page object and a comment text as input and returns a boolean value.

### add_like

This function likes the video. It takes a page object as input and returns None.

### ensure_playing

This function makes sure that a video doesn't get paused, in any circumstances. It takes a page object as input and returns None.

### skip_add

This function skips the skippable ads by clicking the skip ad button. It takes a page object as input and returns None.

### watch_video

This function is responsible for watching a video, it handles all the other features of liking, commenting, skipping ads, muting, etc. It takes a page object, a video URL, a like boolean value, and a comment boolean value as input and returns None.

### run_all_videos

This function maps all the videos to a different page and runs the watch_videos method on it. It takes a browser context object as input and returns None.

### main

This function is the main function that runs the script. It launches the browser, creates a context for each login state file, and runs the run_all_videos function on each context. It returns None.
