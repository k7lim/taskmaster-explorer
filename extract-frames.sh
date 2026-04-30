#!/usr/bin/env bash
# Extract one screenshot per task from YouTube videos.
# Run locally where you have network access + ffmpeg installed.
#
# Usage: ./extract-frames.sh
# Output: frames/<task-id>.jpg (299 files, ~30MB total)
#
# Skips already-extracted frames, so safe to re-run after failures.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMES_DIR="$SCRIPT_DIR/frames"
TASKS_JSON="$SCRIPT_DIR/tasks-index-scored.json"

command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg not found. Install with: brew install ffmpeg"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }

mkdir -p "$FRAMES_DIR"

export SCRIPT_DIR FRAMES_DIR TASKS_JSON
python3 << 'PYEOF'
import json, subprocess, os, sys, time, shutil
from collections import defaultdict

SCRIPT_DIR = os.environ["SCRIPT_DIR"]
FRAMES_DIR = os.environ["FRAMES_DIR"]
TASKS_JSON = os.environ["TASKS_JSON"]

tasks = json.load(open(TASKS_JSON))

# Group by video_id
by_video = defaultdict(list)
for t in tasks:
    by_video[t["video_id"]].append(t)

total = len(tasks)
skipped = sum(1 for t in tasks
              if os.path.exists(os.path.join(FRAMES_DIR, f"{t['id']}.jpg"))
              and os.path.getsize(os.path.join(FRAMES_DIR, f"{t['id']}.jpg")) > 1000)

remaining = total - skipped
print(f"Total tasks: {total}, already done: {skipped}, to extract: {remaining}")
if remaining == 0:
    print("All frames already extracted!")
    sys.exit(0)

done = 0
failed = 0

for video_id, video_tasks in sorted(by_video.items(), key=lambda x: x[1][0]['id']):
    needed = [t for t in video_tasks
              if not os.path.exists(os.path.join(FRAMES_DIR, f"{t['id']}.jpg"))
              or os.path.getsize(os.path.join(FRAMES_DIR, f"{t['id']}.jpg")) < 1000]

    if not needed:
        done += len(video_tasks)
        continue

    url = f"https://youtube.com/watch?v={video_id}"
    print(f"\n--- Video {video_id} ({len(needed)} frames) ---")

    # Download full video at lowest quality to a temp file
    tmpfile = f"/tmp/tm_full_{video_id}.mp4"

    if not os.path.exists(tmpfile):
        sys.stdout.write(f"  Downloading (360p)... ")
        sys.stdout.flush()

        try:
            dl_result = subprocess.run(
                ["yt-dlp", "-f", "18/134/133/160", "--quiet", "--no-warnings",
                 "--cookies-from-browser", "brave",
                 "-o", tmpfile, url],
                capture_output=True, text=True, timeout=600
            )
        except subprocess.TimeoutExpired:
            print("FAIL (timeout - slow connection?)")
            # Clean up partial download
            for f in [tmpfile, tmpfile + ".part"]:
                if os.path.exists(f):
                    os.remove(f)
            failed += len(needed)
            done += len(needed)
            continue

        if not os.path.exists(tmpfile):
            print(f"FAIL")
            if dl_result.stderr:
                for line in dl_result.stderr.strip().split('\n')[-3:]:
                    print(f"    {line[:150]}")
            failed += len(needed)
            done += len(needed)
            continue
        size_mb = os.path.getsize(tmpfile) / 1024 / 1024
        # If suspiciously small (<5MB for a full episode), format 18 likely doesn't exist
        # Re-download with video-only format
        if size_mb < 5:
            print(f"TOO SMALL ({size_mb:.1f}MB), retrying with video-only format...")
            os.remove(tmpfile)
            try:
                dl_result = subprocess.run(
                    ["yt-dlp", "-f", "bestvideo[height<=360][ext=mp4]/bestvideo[height<=360]/worst[ext=mp4]",
                     "--quiet", "--no-warnings",
                     "--cookies-from-browser", "brave",
                     "-o", tmpfile, url],
                    capture_output=True, text=True, timeout=600
                )
            except subprocess.TimeoutExpired:
                print("  FAIL (timeout on retry)")
                failed += len(needed)
                done += len(needed)
                continue
            if not os.path.exists(tmpfile):
                print("  FAIL (retry)")
                failed += len(needed)
                done += len(needed)
                continue
            size_mb = os.path.getsize(tmpfile) / 1024 / 1024
        print(f"OK ({size_mb:.0f}MB)")
    else:
        print(f"  Using cached download")

    # Extract frames at each timestamp
    for t in needed:
        done += 1
        task_id = t["id"]
        ts = t["timestamp_seconds"]
        outfile = os.path.join(FRAMES_DIR, f"{task_id}.jpg")

        sys.stdout.write(f"  [{done}/{total}] {task_id} t={ts}s... ")
        sys.stdout.flush()

        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-ss", str(ts), "-i", tmpfile,
                 "-frames:v", "1", "-q:v", "2", "-vf", "scale=640:-1",
                 outfile],
                capture_output=True, text=True, timeout=15
            )
            if os.path.exists(outfile) and os.path.getsize(outfile) > 1000:
                print(f"OK ({os.path.getsize(outfile) // 1024}KB)")
            else:
                print("FAIL (ffmpeg)")
                failed += 1
                if os.path.exists(outfile):
                    os.remove(outfile)
        except Exception as e:
            print(f"FAIL ({e})")
            failed += 1

    # Delete the full video to save disk space
    os.remove(tmpfile)
    # Rate limit between videos
    time.sleep(2)

print(f"\n{'='*50}")
print(f"Done. {done - failed}/{total} frames. {failed} failed.")
total_size = sum(os.path.getsize(os.path.join(FRAMES_DIR, f))
                 for f in os.listdir(FRAMES_DIR) if f.endswith('.jpg'))
print(f"Total size: {total_size // 1024 // 1024}MB")
PYEOF

# Update tasks-index-scored.json with local frame paths
python3 -c "
import json, os
tasks = json.load(open('$TASKS_JSON'))
found = 0
for t in tasks:
    frame = f'frames/{t[\"id\"]}.jpg'
    if os.path.exists(os.path.join('$SCRIPT_DIR', frame)):
        t['thumbnail_url'] = frame
        found += 1
    else:
        t['thumbnail_url'] = f'https://i.ytimg.com/vi/{t[\"video_id\"]}/hqdefault.jpg'
with open('$TASKS_JSON', 'w') as f:
    json.dump(tasks, f, indent=2)
print(f'Updated {found} tasks with local frame paths')
"
