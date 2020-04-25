import glob
import os
import shutil
from pathlib import Path

import pandas as pd

from pytube import YouTube

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# whether or not to download videos to directory structure
MAKE_VIDS = True
# whether or not to clip out highlights according to timestamps
MAKE_CLIPS = True

# seconds relative each timestamp (before and after) to clip out
CLIP_WINDOW_START = 20
CLIP_WINDOW_END = 20
# same, but in the event of replays or slomos as determined in spreadsheet
CLIP_WINDOW_START_REPLAY = 10
CLIP_WINDOW_END_REPLAY = 40
# files will be written to this new folder in the current directory
WORKDIR = 'video_output/'
# judgement column values worthy of clipping
JUDGEMENT_TO_CLIP = ['nice', 'great', 'perf']


def prep_for_file_path(string):
    return '_'.join([w.strip() for w in string[:30].split()])


def main():

    if WORKDIR:
        os.makedirs(WORKDIR, exist_ok=True)
        for f in glob.glob(str(Path('./') / '*.csv')):
            shutil.copy2(f, WORKDIR)
        os.chdir(WORKDIR)

    for highlight_sheet in Path('./').rglob('*.csv'):
        highlight = str(highlight_sheet)
        highlight = highlight[:highlight.index('.')]

        print(f'processing vids for {highlight}...')

        df = pd.read_csv(highlight_sheet)
        os.makedirs(highlight, exist_ok=True)

        # after grouping by link:
        # download each link, adding relevant timestamp rows as one entry in bout queue
        # iterate over bout queue, to clip timestamps out of respective video

        bout_queue = []

        for link, df_bout in df.groupby('link'):
            if pd.notna(link):
                # construct folder/file name
                try:
                    vid = YouTube(link)
                except:
                    print(f'pytube blew up on video: {link}')
                    continue
                name = prep_for_file_path(vid.title)
                folder_name = Path(highlight) / Path(name)

                bout_queue.append((df_bout, folder_name))

                if MAKE_VIDS:
                    # downloading the video if none exists in folder
                    if not [v for v in folder_name.rglob('*.mp4') if os.path.isfile(v)]:

                        os.makedirs(folder_name, exist_ok=True)
                        print(f'downloading {name}')

                        stream = (
                            vid.streams
                            # progressive: audio and video in one file
                            # mp4: to work with ffmpeg
                            .filter(progressive=True, file_extension='mp4')
                            # retrieve highest resolution
                            .order_by('resolution')
                            .desc()
                            .first()
                        )

                        stream.download(folder_name)
                    else:
                        print(f'video exists in {name}... skipping')

        if MAKE_CLIPS:

            for df_bout, folder_name in bout_queue:
                # required that there's a video in this directory!
                if not os.listdir(folder_name):
                    continue

                video_name = os.listdir(folder_name)[0]
                assert video_name

                offset_start = CLIP_WINDOW_START
                offset_end = CLIP_WINDOW_END
                if df_bout.replay.any():
                    print(f'{video_name[:20]} has replay, increasing clip length')

                    offset_start = CLIP_WINDOW_START_REPLAY
                    offset_end = CLIP_WINDOW_END_REPLAY

                for i, series in df_bout.iterrows():
                    judgement = series['judgement']

                    if judgement in JUDGEMENT_TO_CLIP:
                        timestamp = series['timestamp']
                        min, sec = timestamp.split(':')
                        window = int(min) * 60 + int(sec)
                        window_start = window - offset_start
                        window_end = window + offset_end

                        desc = prep_for_file_path(series['description'])
                        blurb = f'{judgement}__{desc}'
                        if pd.notna(series['comment']):
                            comment = prep_for_file_path(series['comment'][:10])
                            blurb += f'__{comment}'

                        vid_in_name = str(folder_name) + '/' + video_name
                        clip_out_name = f'{highlight}/{prep_for_file_path(video_name[:20])}__{blurb}.mp4'

                        ffmpeg_extract_subclip(vid_in_name, window_start,
                                               window_end, clip_out_name)


if __name__ == '__main__':
    main()
