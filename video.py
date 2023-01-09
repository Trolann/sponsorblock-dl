import pytube

from sb_log import logging  # Standard logging
from pytube import YouTube, exceptions  # To download videos
from moviepy.editor import *  # To stitch videos together
import sponsorblock as sb  # For block times
import os
from dataclasses import dataclass, asdict, field


# Must also ensure FFMPEG is installed


@dataclass
class VideoInfo:
    title: str = ""
    location: str = ""
    filename: str = ""
    block_list: list = field(default_factory=lambda : [])
    length: int = 0


VIDEO = VideoInfo()


def get_video_title(url) -> bool:
    try:
        VIDEO.title = YouTube(url).title
        return True
    except exceptions.RegexMatchError as e:
        return False


def download_video(url) -> None:
    """
    Downloads the given video URL and returns the file location and filename
    :param url:
    :return:
    """
    logging.info(f'Downloading {url} begin')
    video = YouTube(url)
    logging.info(f'Found {video.title} looking for streams')
    stream = video.streams.filter(res='360p', file_extension='mp4')[0]
    logging.info(f'Found {stream.default_filename} to download, starting ')
    VIDEO.location = stream.download()
    logging.info(f'{VIDEO.location} downloaded')
    VIDEO.filename = stream.default_filename


def get_sponsorblock(url) -> None:
    """
    Queries SponsorBlock API and returns a list of Segment objects
    :param video_title:
    :param url:
    :return:
    """
    logging.info(f'Getting SponsorBlock content for {VIDEO.title} | {url}')
    sb_client = sb.Client()
    segments = sb_client.get_skip_segments(url)
    VIDEO.block_list = [s for s in segments if s.category == "sponsor"]
    logging.info(f'Got {len(VIDEO.block_list)} sponsor blocks for {VIDEO.title}')


def process_video() -> None:
    """
    Processes a single video given a list of block Segments.
    :param video_title:
    :param video_location:
    :param block_list:
    :return:
    """
    clips = list()

    last_time = 0
    logging.info(f'Processing {len(VIDEO.block_list)} blocks for {VIDEO.title}')
    video_end = VideoFileClip(VIDEO.location).end # Need the overall video length

    for i, ad_read in enumerate(VIDEO.block_list): # For each block
        # Make the audio clip
        audio = AudioFileClip(VIDEO.location)
        audio = audio.cutout(int(ad_read.start), video_end)
        audio = audio.cutout(0, last_time)
        logging.info(f'Got audio starting at {last_time} until {ad_read.start}')

        # Make the video clip and then set hte audio to the previously extracted clip
        clip = VideoFileClip(VIDEO.location, audio=True).subclip(last_time, int(ad_read.start))
        clip = clip.set_audio(audio)
        #clip.write_videofile(f'clip{i+1}_{VIDEO.filename}', audio=True, fps=30, audio_codec='aac')
        logging.info(f'Got video starting at {last_time} until {ad_read.start}')

        # Prepare for next loop
        clips.append(clip)
        last_time = int(ad_read.end)

        logging.info(f'Block #{i + 1} completed, advancing...')

    # Create the chunk after the last block
    # Cutoff the start
    last_audio = AudioFileClip(VIDEO.location)
    audio = last_audio.cutout(0, last_time)

    # Create the video clip and add the audio
    last_clip = VideoFileClip(VIDEO.location).subclip(last_time, video_end)
    last_clip = last_clip.set_audio(audio)
    clips.append(last_clip)

    # Create the clip
    logging.info(f'Final clip for {VIDEO.title} created, creating video.')
    ad_free = concatenate_videoclips(clips)

    ad_free.write_videofile(f'ad_free_{VIDEO.filename}', audio=True, fps=30, audio_codec='aac')
    logging.info(f'Processing done for {VIDEO.title}')


def run():
    """
    Basic run function
    :return:
    """
    # TODO: Allow for playlists
    # TODO: Add Dockerfile, update ENV
    # TODO: replit support
    url = input('What YouTube video do you want downloaded and SponsorBlocked?: ')
    #url = "https://www.youtube.com/watch?v=kypGBUTTTHs"
    download_video(url)
    get_sponsorblock(url)
    process_video()


if __name__ == "__main__":
    run()
