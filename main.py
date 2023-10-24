"""
This script automates the process of playing YouTube videos, liking them, commenting on them, and setting the video quality to 144p. 

The script uses Playwright to interact with the YouTube website and perform the following actions:
- Play a video
- Skip ads
- Like a video
- Comment on a video
- Mute a video
- Set video quality to 144p
- Checks if full video have been played


The script requires the following inputs:
- VIDEOS_LIST: a list of YouTube video URLs to play
- LIKE_VALUE: a boolean value to determine whether to like the video or not
- COMMENT_VALUE: a boolean value to determine whether to comment on the video or not

This script can concurrently play diffrent videos from different account.

To define the different accounts, just place your state file in the **loginState Folder**

The script can be run by executing the main() function.
"""

from playwright.async_api import async_playwright
from playwright.async_api import Page, BrowserContext
from datetime import datetime, timedelta
import asyncio
import random
import os

VIDEOS_LIST = [
    'https://www.youtube.com/watch?v=IqwIOlhfCak',
    'https://www.youtube.com/watch?v=ElZfdU54Cp8',
    'https://www.youtube.com/watch?v=Gp1RNYBckBs',
    'https://www.youtube.com/watch?v=ts7oLiVqwb0',
    'https://www.youtube.com/watch?v=I-_LHvTeVy4'

]
LIKE_VALUE = True  # True or False
COMMENT_VALUE = False  # True or False


# xpaths slectors of various components
play_btn = "//button[@data-title-no-tooltip='Play']"
pause_btn = "//button[@data-title-no-tooltip='Pause']"

ad_skip_btn = "//button[contains(@class, 'ytp-ad-skip-button')]"
ad_skip_btn_notVisible = "//div//span[@style='display: none;']//button[contains(@class, 'ytp-ad-skip-button')]"

video_player = "//div[contains(@id, 'movie_player')]"

like_btn = "(//div[@id='segmented-like-button'])[1]//button"

comment_box = '//div//*[@role = "textbox"]'
comment_input = '//div[@id="contenteditable-root"]'
comment_btn = '//button[@aria-label = "Comment"]'

setting_btn = '(//button[@data-tooltip-target-id="ytp-settings-button"])[1]'
quality_btn = '//div[@class="ytp-menuitem-label" and contains(text(), "Quality")]'
quality_panel = "//div[@class = 'ytp-panel ytp-quality-menu']"
quality_item = "//div[@class = 'ytp-panel ytp-quality-menu']//div[@class='ytp-menuitem']//div[@class='ytp-menuitem-label']//span[contains(text(),'144p')]"

mute_btn = "//button[contains(@class,'ytp-mute-button ytp-button') and (@title = 'Mute (m)' or @title='Unmute (m)')]"

time_current_loc = "(//div[contains(@class,'ytp-chrome-controls')]//span[@class='ytp-time-current'])[1]"
total_duration_loc = "(//div[contains(@class,'ytp-chrome-controls')]//span[@class='ytp-time-duration'])[1]"


async def is_fully_played(page: Page):
    '''Closes the page when a video is completly played'''

    await page.locator(like_btn).hover()
    await page.wait_for_timeout(1000)

    playing_or_paused = await page.locator(video_player).get_attribute("class")

    if not ("ad-in" in playing_or_paused):

        await page.locator(video_player).hover()
        current_time = await page.locator(time_current_loc).inner_text()
        total_duration = await page.locator(total_duration_loc).inner_text()

        try:
            current_delta = datetime.strptime(
                current_time, '%M:%S') - datetime(1900, 1, 1)
        except ValueError:
            try:
                current_delta = datetime.strptime(
                    current_time, '%H:%M:%S') - datetime(1900, 1, 1)
            except ValueError:
                current_delta = timedelta(seconds=int(current_time))

        try:
            total_delta = datetime.strptime(
                total_duration, '%M:%S') - datetime(1900, 1, 1)
        except ValueError:
            try:
                total_delta = datetime.strptime(
                    total_duration, '%H:%M:%S') - datetime(1900, 1, 1)
            except ValueError:
                total_delta = timedelta(seconds=int(total_duration))

        remaining_delta = total_delta - current_delta

        if current_delta + timedelta(seconds=4) > total_delta:
            print(remaining_delta.total_seconds())
            await page.close()

            return True
        else:
            return False
    return False


def random_comment_generator():
    '''generates a random comment from the fixed adjectives, nouns, and emojis'''
    # List of fixed words
    adjectives = ["amazing", "awesome", "cool", "fantastic", "great",
                  "incredible", "nice", "super", "terrific", "wonderful"]
    nouns = ["animation", "clip", "footage", "movie", "production", "show", "trailer", "video", "vlog", "webinar", "documentary", "tutorial", "review",
             "montage", "compilation", "highlight reel", "stream", "livestream", "podcast", "interview", "behind-the-scenes", "bloopers", "outtakes"]
    emojis = ["👍", "👌", "🙌", "💯", "🔥", "😍", "😎", "🤩", "👀", "🎉"]

    # Generate a random comment
    noun = random.choice(nouns)
    comment = f"{random.choice(adjectives)} {noun} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)} {random.choice(emojis)}!"
    return comment


async def mute_video(page: Page):
    '''Tries to mute the video (it is a lttle buggy)'''
    muted_or_unmuted = await page.locator(mute_btn).get_attribute("Title")
    if muted_or_unmuted == "Unmute (m)":
        print('Video is MUted')
    elif muted_or_unmuted == "Mute (m)":
        await page.locator(mute_btn).click()
        print("Video is muted")
        muted = True


async def set_quality_144p(page: Page):
    '''sets the quality of video to 144p to save resources'''

    playing_or_paused = await page.locator(video_player).get_attribute("class")
    while "ad-in" in playing_or_paused:
        await page.wait_for_timeout(500)
        playing_or_paused = await page.locator(video_player).get_attribute("class")

    await page.locator(setting_btn).click()
    await page.locator(quality_btn).click()
    await page.locator(quality_item).click()


async def add_comment(page: Page, comment_text):
    '''Adds a comment to the video.
    pass comment_text = "RANDOM" to generate random comments on videos
    or you can pass a static text, which is not suggested to do. '''

    if comment_text == "RANDOM":
        comment_text = random_comment_generator()
    await page.locator(comment_box).click()
    await page.locator(comment_input).click()
    await page.locator(comment_input).fill(comment_text)
    await page.locator(comment_btn).click()
    print(f"commented on video: {comment_text}")
    return True


async def add_like(page: Page):
    '''Likes the video'''
    if await (page.locator(like_btn).get_attribute('aria-pressed')) == 'false':
        print("liked video")
        await page.locator(like_btn).click()


async def ensure_playing(page: Page):
    '''This function makes sure that a videos doesn't get paused,
    in any circumstances'''
    should_play = True

    while should_play:
        playing_or_paused = await page.locator(video_player).get_attribute("class")
        await page.wait_for_timeout(500)

        # making video always in playing mode (even if it is paused by us or any other means)
        if ("paused-mode" in playing_or_paused) or ("unstarted-mode" in playing_or_paused):

            # print("paused mode")
            await page.locator(play_btn).click()
            # video_is_playing = True
            # print("playing mode")

        should_play = not (await is_fully_played(page))

    await page.close()
    print("VIDEO PLAYED SUCCESSFULLY")


async def skip_add(page: Page):
    '''Skips the skippable adv. by clicking the skip ad button'''

    try:
        while True:
            playing_or_paused = await page.locator(video_player).get_attribute("class")
            if ("ad-in" in playing_or_paused):
                while True:
                    await page.wait_for_timeout(500)
                    playing_or_paused = await page.locator(
                        video_player).get_attribute("class")
                    if ("ad-in" in playing_or_paused):
                        is_adv = True
                        print("ad mode")
                        await page.wait_for_timeout(1000)
                        try:
                            await page.locator(ad_skip_btn).click(force=True)
                        except Exception:
                            print("Add not skippable")
                    else:
                        break
    except Exception:
        pass


async def watch_video(page: Page, video_url, like=False, comment=False):
    '''This functions is responsible for watching a video,
    it handles all the other features of liking,
    commenting, skipping adv, muting etc.'''

    await page.goto(video_url, timeout=0)
    await page.wait_for_timeout(1000)
    await page.locator(play_btn).click()

    await page.reload()

    await page.wait_for_timeout(1000)

    t1 = asyncio.create_task(ensure_playing(page=page))
    t2 = asyncio.create_task(skip_add(page=page))

    await mute_video(page)

    await set_quality_144p(page)

    if like:
        await add_like(page)

    await page.wait_for_timeout(2000)
    await page.mouse.wheel(0, 200)

    if comment:
        await add_comment(page=page, comment_text="RANDOM")

    await page.locator(video_player).focus()
    await page.mouse.wheel(0, -200)

    try:
        await t1, t2
    except Exception:
        pass


async def run_all_videos(context: BrowserContext):
    '''This Functions maps all the videos to a differnet page and runs the watch_videos method on it'''

    tasks = []
    for video_url in VIDEOS_LIST:

        page = await context.new_page()
        # running the watch video function
        task = asyncio.create_task(watch_video(
            page, video_url=video_url, like=LIKE_VALUE, comment=COMMENT_VALUE))

        tasks.append(task)
        await page.wait_for_timeout(500)

    for task in tasks:
        try:
            await task
        except Exception as e:
            # print(f"Exception occurred in task {task}")
            pass


async def main():

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        tasks = []
        import os

        folder_path = "loginStates"
        file_names = os.listdir(folder_path)
        state_file_paths = [os.path.join(folder_path, file_name)
                            for file_name in file_names]

        context_tasks = []
        for state_path in state_file_paths:
            context = await browser.new_context(storage_state=state_path)

            context_task = asyncio.create_task(run_all_videos(context))
            context_tasks.append(context_task)

        for task in context_tasks:
            try:
                await task
            except Exception as e:
                print(f"Exception occurred in Context task {task}")


asyncio.run(main())
