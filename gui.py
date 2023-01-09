import PySimpleGUI as gui
from sb_log import logging
from video import *
from threading import Thread
from asyncio import run as async_run
from time import perf_counter as counter

STATUS = gui.Text('Awaiting URL')
URL_BOX = gui.InputText()

layout = [
    [gui.Text("Paste the URL to the video you want to download and cut with SponsorBlock.:")],
    [URL_BOX, gui.Button('Go')],
    [STATUS]
]

window = gui.Window("SponsorBlock Downloader", layout=layout, icon='sponsorblock.ico')


if __name__ == '__main__':
    while True:
        event, values = window.read(timeout=10)
        if event == gui.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break

        if event != 'Go':
            if VIDEO.perf_counter_start:
                seconds = int(counter() - VIDEO.perf_counter_start)
                if seconds < 1:
                    continue
                time = f'{seconds} seconds' if seconds < 60 else f'{int(seconds/60)} minutes'
                time = time[:-1] if seconds == 1 or 60 < seconds < 120 else time
                STATUS.update(f'Stitching {len(VIDEO.block_list) + 1} blocks taken {time}.')
                window.refresh()
            continue

        url = values[0]
        title = get_video_title(url)
        if not title:
            STATUS.update(f'Invalid URL {url}. Please paste valid YouTube video URL starting with https://')
            continue

        STATUS.update(f'Downloading "{VIDEO.title}"')
        window.refresh()
        async_run(download_video(url))

        STATUS.update(f'Downloaded {VIDEO.filename}, getting SponsorBlock data.')
        window.refresh()
        get_sponsorblock(url)

        if not VIDEO.block_list:
            STATUS.update(f'{title} has no SponsorBlock\'s, unable to process.')
            window.refresh()
        else:
            try:
                if not VIDEO.perf_counter_start:
                    STATUS.update(f'Stitching {len(VIDEO.block_list) + 1} blocks (this may take a while).')
                    window.refresh()
                    VIDEO.perf_counter_start = counter()
                    t = Thread(name='processing', target=process_video, args=())
                    t.start()
                #process_video()
                    logging.info('got here')
                else:
                    logging.info('trying to stitch')
                    STATUS.update(f'Stitching {len(VIDEO.block_list) + 1} blocks taken {counter() - VIDEO.perf_counter_start}')
                    window.refresh()
            except:
                pass
            finally:
                if VIDEO.perf_counter_start > 0 and VIDEO.processing_done:
                    VIDEO.perf_counter_start = 0
                    STATUS.update(f'Finished ad_free_{VIDEO.filename}.')
                    URL_BOX.update('')
                elif VIDEO.perf_counter_start > 0 and not t.is_alive():
                    STATUS.update(f'Error occurred when processing {VIDEO.filename}.')
                window.refresh()


