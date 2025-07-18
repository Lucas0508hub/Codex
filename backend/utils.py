import os
import csv
import ffmpeg
from tempfile import TemporaryDirectory
from typing import List, Tuple


def export_segments(wav_path: str, segments: List[Tuple[int, float, float, str]], out_dir: str) -> str:
    csv_path = os.path.join(out_dir, 'metadata.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['filename', 'transcript'])
        for idx, start, end, transcript in segments:
            clip_name = f'segment_{idx}.wav'
            clip_path = os.path.join(out_dir, clip_name)
            (
                ffmpeg
                .input(wav_path, ss=start, to=end)
                .output(clip_path)
                .overwrite_output()
                .run(quiet=True)
            )
            writer.writerow([clip_name, transcript])
    return csv_path
