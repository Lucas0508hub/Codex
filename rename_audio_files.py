import os
import pandas as pd
import argparse
import re

def sanitize_filename(name):
    """Sanitize string to be safe for filenames."""
    name = name.replace(" ", "_")
    return re.sub(r'[\\/:*?"<>|]', '', name)

def rename_files(spreadsheet, audio_dir):
    if spreadsheet.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(spreadsheet, header=None)
    else:
        df = pd.read_csv(spreadsheet, header=None)

    for idx, row in df.iterrows():
        new_name_raw, old_filename = row[0], row[1]
        base, ext = os.path.splitext(old_filename)
        new_name = sanitize_filename(str(new_name_raw)) + ext
        old_path = os.path.join(audio_dir, old_filename)
        new_path = os.path.join(audio_dir, new_name)

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"Renamed {old_filename} -> {new_name}")
        else:
            print(f"File not found: {old_filename}")

def main():
    parser = argparse.ArgumentParser(description="Rename audio files based on spreadsheet mapping.")
    parser.add_argument("spreadsheet", help="Path to CSV or Excel file with two columns: new name, current filename")
    parser.add_argument("audio_dir", help="Directory containing the audio files")
    args = parser.parse_args()
    rename_files(args.spreadsheet, args.audio_dir)

if __name__ == "__main__":
    main()
