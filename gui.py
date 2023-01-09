import PySimpleGUI as gui
from sb_log import logging
from video import *
from threading import Thread

STATUS = gui.Text('Awaiting URL')

layout = [
    [gui.Text("Paste the URL to the video you want to download and cut with SponsorBlock.:")],
    [gui.InputText(), gui.Button('Go')],
    [STATUS]
]

window = gui.Window("SponsorBlock Downloader", layout=layout, icon='sponsorblock.ico')


if __name__ == '__main__':
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break

        logging.info(values)
        url = values[0]
        title = get_video_title(url)
        if not title:
            STATUS.update(f'Invalid URL {url}. Please paste valid YouTube video URL starting with https://')
            continue

        STATUS.update(f'Downloading "{VIDEO.title}"')
        download_thread = Thread(target=download_video, args=(url,))
        download_thread.start()

        STATUS.update(f'Downloaded {VIDEO.filename}, getting SponsorBlock data.')
        get_sponsorblock(url)

        if not VIDEO.block_list:
            STATUS.update(f'{title} has no SponsorBlock\'s, unable to process.')
        else:
            STATUS.update(f'Stitching {len(VIDEO.block_list)} blocks (this may take a while).')
            success = False
            try:
                t = Thread(target=process_video)
                t.start()
                t.join()
                success = True
            except:
                pass
            finally:
                if success:
                    STATUS.update(f'Finished ad_free_{VIDEO.filename}.')
                else:
                    STATUS.update(f'Error occurred when processing {VIDEO.filename}.')


