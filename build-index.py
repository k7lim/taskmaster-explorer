#!/usr/bin/env python3
"""
build-index.py -- Build a structured JSON index of all Taskmaster tasks.

Reads:
  - episodes-index.json  (video IDs, heatmaps, per episode)
  - all-tasks-by-season.md  (task descriptions, timestamps, types)

Writes:
  - tasks-index.json
"""

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# 1. Load the episodes index
# ---------------------------------------------------------------------------
def load_episodes_index():
    with open(BASE / "episodes-index.json") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------------

def ts_to_seconds(ts_str: str) -> int | None:
    """Convert a timestamp string like '07:30', '1:23:45', '02:00' to seconds."""
    if not ts_str:
        return None
    parts = ts_str.strip().split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return None


def seconds_to_display(s: int) -> str:
    """Convert seconds to MM:SS or HH:MM:SS display string."""
    if s is None:
        return ""
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f"{h}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"


def get_heatmap_peak(heatmap: list[dict]) -> tuple[float, str]:
    """Return (peak_value, peak_time_display) from a heatmap array.
    Skips the first bucket (the 0:00 auto-play spike)."""
    if not heatmap or len(heatmap) < 2:
        return (0.0, "")
    # skip first bucket (index 0) which is always the initial play spike
    best = max(heatmap[1:], key=lambda h: h.get("value", 0))
    mid_time = (best["start_time"] + best["end_time"]) / 2
    return (round(best["value"], 4), seconds_to_display(int(mid_time)))


def clean_description(desc: str) -> str:
    """Strip surrounding quotes and whitespace from a description."""
    desc = desc.strip()
    # Remove leading/trailing quotes (various styles)
    if (desc.startswith('"') and desc.endswith('"')) or \
       (desc.startswith('\u201c') and desc.endswith('\u201d')):
        desc = desc[1:-1].strip()
    return desc


def determine_task_type(raw_type: str, header: str) -> str:
    """Normalize a task type string to one of: solo, prize, team, live, special."""
    raw = raw_type.lower().strip() if raw_type else ""
    header_lower = header.lower() if header else ""

    if "prize" in raw or "prize" in header_lower:
        return "prize"
    if "team" in raw or "team" in header_lower:
        return "team"
    if "live" in raw or "live" in header_lower:
        return "live"
    if "special" in raw or "special" in header_lower or "secret" in header_lower:
        return "special"
    if "solo" in raw or raw == "":
        return "solo"
    return "solo"


# ---------------------------------------------------------------------------
# 3. Parse the markdown into task objects
# ---------------------------------------------------------------------------

# Episode header patterns (various formats across seasons):
#   # EPISODE 1 - "A Fat Bald White Man"
#   ## EPISODE 2 - "Look At Me"
#   ## EPISODE 1: "Dignity Intact"
#   ## EPISODE 1 -- "The Mean Bean"
#   # EPISODE 1 -- "Flight of Fantasy" (File 001)
EPISODE_HEADER_RE = re.compile(
    r'^#{1,3}\s*EPISODE\s+(\d+)\s*[-:–—]+\s*["\u201c]([^"\u201d]+)["\u201d]',
    re.IGNORECASE,
)

# Task header patterns (handles all variations found across seasons):
# **Task 1 (Prize Task) -- ~02:00**
# ### Task 1 -- Prize Task
# **Task 2** -- ~8:47
# **Task 4 (Live)** -- ~39:43 (t=2383s)
# **Task 3 (Solo -- two-part)** ~19:11
# **Task 1 -- Prize Task** (~02:25)
TASK_HEADER_RE = re.compile(
    r'^(?:#{1,4}\s*|\*\*\s*)'             # leading ### or **
    r'Task\s+(\d+)'                        # "Task N"
    r'(?:\s*\(([^)]*?)\))?'               # optional parenthetical like (Prize Task)
    r'(?:\s*\**\s*)'                       # optional closing **
    r'(?:[-–—]+\s*)?'                      # optional separator dashes
    r'(.*)',                                # rest of line (task name, timestamp, etc.)
    re.IGNORECASE,
)

# Timestamp patterns
TIMESTAMP_TILDE_RE = re.compile(r'~\s*(\d{1,2}:\d{2}(?::\d{2})?)')
TIMESTAMP_PAREN_RE = re.compile(r'\(~?(\d{1,2}:\d{2}(?::\d{2})?)\)')
TIMESTAMP_T_RE = re.compile(r'\(t=(\d+)s?\)')  # (t=126s) format used in S20

# Field extractors -- match at line start, allowing leading list markers
TYPE_RE = re.compile(r'^[-*\s]*\*{0,2}Type:?\*{0,2}\s*(.*)', re.IGNORECASE)
DESC_RE = re.compile(r'^[-*\s]*\*{0,2}Description:?\*{0,2}\s*(.*)', re.IGNORECASE)
SUMMARY_RE = re.compile(r'^[-*\s]*\*{0,2}Summary:?\*{0,2}\s*(.*)', re.IGNORECASE)
TIMESTAMP_FIELD_RE = re.compile(r'^[-*\s]*\*{0,2}Timestamp:?\*{0,2}\s*(.*)', re.IGNORECASE)
CROWD_FAV_RE = re.compile(r'CROWD\s+FAVORITE', re.IGNORECASE)

# Sections to skip (these are summary/recap sections, not task definitions)
SKIP_SECTION_RE = re.compile(
    r'^#{1,3}\s*TOP\s+CROWD|'
    r'^#{1,3}\s*SUMMARY|'
    r'^#{1,3}\s*OVERALL|'
    r'^\*\*Total\s+tasks',
    re.IGNORECASE,
)

# Season detection patterns (in body text, not just headers)
SEASON_NUM_RE = re.compile(r'(?:TASKMASTER\s+)?SEASON\s+(\d+)', re.IGNORECASE)
SEASON_NZ_RE = re.compile(r'Taskmaster\s+NZ\s+Season\s+(\d+)', re.IGNORECASE)


def detect_season_from_line(line: str) -> str | None:
    """Try to detect a season change from this line. Returns season string or None."""
    # NZ pattern (check first -- more specific)
    m = SEASON_NZ_RE.search(line)
    if m:
        return f"nz-s{int(m.group(1)):02d}"

    # Regular season pattern in headers
    if re.match(r'^#', line):
        m = SEASON_NUM_RE.search(line)
        if m:
            return f"s{int(m.group(1)):02d}"

    # Regular season in body text (for S07 which uses a paragraph)
    # "tasks/challenges from Taskmaster Season 7"
    m = re.search(r'from\s+Taskmaster\s+Season\s+(\d+)', line, re.IGNORECASE)
    if m:
        return f"s{int(m.group(1)):02d}"

    # "TASKMASTER SEASON 20 -- COMPLETE TASK EXTRACTION"
    m = re.search(r'TASKMASTER\s+SEASON\s+(\d+)', line)
    if m:
        return f"s{int(m.group(1)):02d}"

    # S19 contestant detection (no season header exists)
    if "Fatiha El-Ghorri" in line:
        return "s19"

    return None


def extract_timestamp(line: str) -> int | None:
    """Extract timestamp in seconds from a line, trying multiple patterns."""
    # Try ~MM:SS or (~MM:SS)
    m = TIMESTAMP_TILDE_RE.search(line)
    if m:
        return ts_to_seconds(m.group(1))

    m = TIMESTAMP_PAREN_RE.search(line)
    if m:
        return ts_to_seconds(m.group(1))

    # Try (t=NNNs) format
    m = TIMESTAMP_T_RE.search(line)
    if m:
        return int(m.group(1))

    return None


def parse_markdown(filepath: str) -> list[dict]:
    """Parse the all-tasks-by-season.md file into a list of task dicts."""
    with open(filepath) as f:
        lines = f.readlines()

    tasks = []
    current_season = "s04"  # file starts with S04
    current_episode_num = None
    current_episode_title = ""
    in_skip_section = False  # True when inside a "TOP CROWD-FAVORITE" or summary section

    # State for the current task being built
    current_task = None
    in_summary = False  # for multi-line summaries

    def flush_task():
        nonlocal current_task, in_summary
        if current_task:
            # Clean up description and summary
            if current_task.get("task_description"):
                current_task["task_description"] = clean_description(
                    current_task["task_description"]
                )
            if current_task.get("task_summary"):
                current_task["task_summary"] = current_task["task_summary"].strip()
            # Normalize type
            current_task["task_type"] = determine_task_type(
                current_task.get("_raw_type", ""),
                current_task.get("_header_parens", ""),
            )
            # Remove internal fields
            current_task.pop("_raw_type", None)
            current_task.pop("_header_parens", None)
            tasks.append(current_task)
        current_task = None
        in_summary = False

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # ---- Detect season boundaries ----
        new_season = detect_season_from_line(stripped)
        if new_season:
            flush_task()
            current_season = new_season
            in_skip_section = False
            # Don't continue -- the same line might also be an episode header

        # ---- Detect skip sections (TOP CROWD-FAVORITE, summaries, etc.) ----
        if SKIP_SECTION_RE.match(stripped):
            flush_task()
            in_skip_section = True
            current_episode_num = None  # reset so tasks in recap don't get assigned
            continue

        # An episode header always exits a skip section
        ep_match = EPISODE_HEADER_RE.match(stripped)
        if ep_match:
            flush_task()
            in_skip_section = False
            current_episode_num = int(ep_match.group(1))
            current_episode_title = ep_match.group(2).strip()
            # Remove trailing content like "(File 001)" or "(Grand Final)" from title
            current_episode_title = re.sub(
                r'\s*\((?:File\s+\d+|Grand\s+Final|Series\s+Finale|GRAND\s+FINAL)\)\s*$',
                '',
                current_episode_title,
                flags=re.IGNORECASE,
            ).strip()
            in_summary = False
            continue

        # If in a skip section, ignore everything
        if in_skip_section:
            continue

        # ---- Detect task headers ----
        task_match = TASK_HEADER_RE.match(stripped)
        if task_match and current_episode_num is not None:
            flush_task()
            in_summary = False

            task_num = int(task_match.group(1))
            header_parens = task_match.group(2) or ""
            rest_of_line = task_match.group(3) or ""

            # Extract timestamp from the rest of the line
            timestamp_seconds = extract_timestamp(stripped)

            # Also check for type info in the header rest
            # e.g. "### Task 1 -- Prize Task" -> rest = "Prize Task"
            # or "**Task 4 (Team Task) -- ~22:00**" -> parens = "Team Task"
            header_type_hint = rest_of_line.strip().rstrip("*").strip()

            ep_key = f"{current_season}/{current_episode_num:03d}"
            task_id = f"{current_season}-e{current_episode_num:02d}-t{task_num:02d}"

            current_task = {
                "id": task_id,
                "season": current_season,
                "episode_num": current_episode_num,
                "episode_title": current_episode_title,
                "episode_key": ep_key,
                "task_num": task_num,
                "timestamp_seconds": timestamp_seconds,
                "timestamp_display": seconds_to_display(timestamp_seconds) if timestamp_seconds is not None else "",
                "task_description": "",
                "task_summary": "",
                "_raw_type": "",
                "_header_parens": header_parens + " " + header_type_hint,
                "is_crowd_favorite": False,
            }
            continue

        # ---- If not inside a task, skip ----
        if current_task is None:
            continue

        # ---- Parse task body lines ----

        # Horizontal rules or blank lines end summary continuation
        if stripped == "---" or stripped == "":
            in_summary = False
            continue

        # Heatmap notes / metadata lines -- stop summary, don't consume
        if stripped.startswith("**Heatmap") or stripped.startswith("- Heatmap"):
            in_summary = False
            continue

        # Timestamp field (S05 format: "- **Timestamp:** ~07:39")
        ts_field = TIMESTAMP_FIELD_RE.match(stripped)
        if ts_field:
            ts_val = extract_timestamp(ts_field.group(1))
            if ts_val is not None and current_task["timestamp_seconds"] is None:
                current_task["timestamp_seconds"] = ts_val
                current_task["timestamp_display"] = seconds_to_display(ts_val)
            in_summary = False
            continue

        # Type line
        type_match = TYPE_RE.match(stripped)
        if type_match:
            current_task["_raw_type"] = type_match.group(1).strip().rstrip(".")
            in_summary = False
            continue

        # Description line (can be multi-value for multi-part tasks)
        desc_match = DESC_RE.match(stripped)
        if desc_match:
            desc_text = desc_match.group(1).strip()
            if current_task["task_description"]:
                current_task["task_description"] += " " + desc_text
            else:
                current_task["task_description"] = desc_text
            in_summary = False
            continue

        # "- Part N:" lines for multi-part task descriptions (S19)
        if re.match(r'^-?\s*Part\s+\d+:', stripped, re.IGNORECASE):
            part_text = stripped.lstrip("- ").strip()
            if current_task["task_description"]:
                current_task["task_description"] += " " + part_text
            else:
                current_task["task_description"] = part_text
            in_summary = False
            continue

        # Summary line
        summary_match = SUMMARY_RE.match(stripped)
        if summary_match:
            current_task["task_summary"] = summary_match.group(1).strip()
            in_summary = True
            continue

        # Crowd favorite
        if CROWD_FAV_RE.search(stripped):
            current_task["is_crowd_favorite"] = True
            in_summary = False
            continue

        # Heatmap note line (within task body -- not a continuation of summary)
        if re.match(r'^[-*\s]*\*{0,2}Heatmap\s+(note|peak)', stripped, re.IGNORECASE):
            in_summary = False
            continue

        # Lines starting with ** are likely new metadata, not summary
        if stripped.startswith("**") and not in_summary:
            continue

        # Continuation of summary (non-empty line that isn't a field)
        if in_summary and stripped:
            current_task["task_summary"] += " " + stripped

    # Flush last task
    flush_task()

    return tasks


# ---------------------------------------------------------------------------
# 4. Post-processing: fix season assignments where detection order was wrong
# ---------------------------------------------------------------------------

def fix_season_assignments(tasks: list[dict], episodes: dict) -> list[dict]:
    """Fix tasks assigned to wrong season because the season boundary was
    detected after the first episode header. Use episode titles to verify."""
    # Build a reverse lookup: episode_title -> season/episode_num from episodes-index
    title_to_season = {}
    for key, ep in episodes.items():
        season = ep.get("season", key.split("/")[0])
        ep_num = ep.get("episode_num", int(key.split("/")[1]))
        # Extract the episode title from the full YouTube title
        # e.g. "Series 4, Episode 1 - 'A Fat Bald White Man.' | Full Episode | Taskmaster"
        yt_title = ep.get("title", "")
        title_to_season[key] = (season, ep_num)

    # Also build sets of episode titles per season from the markdown tasks themselves
    # to detect mismatches. The simplest fix: if a task's episode_key doesn't exist
    # in the episodes index, try other seasons.
    for task in tasks:
        ep_key = task["episode_key"]
        if ep_key in episodes:
            continue  # already matched

        # Try to find the right season by checking other seasons with the same ep number
        ep_num = task["episode_num"]
        for candidate_key in episodes:
            parts = candidate_key.split("/")
            if int(parts[1]) == ep_num:
                candidate_season = parts[0]
                if candidate_season != task["season"]:
                    # Check if reassigning would fix it
                    new_key = f"{candidate_season}/{ep_num:03d}"
                    if new_key in episodes and new_key != ep_key:
                        # Don't reassign if another task already claims this slot
                        # correctly. Just flag it for now.
                        pass

    # Hard-coded fixes for known mismatches based on the file structure:
    # S19 has no season header; its episodes come after NZ-S02.
    # S19 episode titles (from the markdown):
    s19_titles = {
        "Sometimes spit.", "An invisible jump rope.", "My presumably s***tum.",
        "Midnight picnic.", "Maybe we're the monsters.", "It's got to be obsolete.",
        "Glass half most.", "Science all your life.", "Getaway sticks.", "The clever side.",
    }
    s20_titles = {
        "9x7.", "Cows are made of milk.", "Thompson.", "Hey mate.",
        "Bats, bats, hang up.", "Is that number got curves?",
        "Drier than you think, chalk.", "Am I an idiom?",
        "A 1970s camping kettle.", "Supping from the fountain.",
    }

    for task in tasks:
        title = task["episode_title"]
        if title in s19_titles and task["season"] != "s19":
            task["season"] = "s19"
            task["episode_key"] = f"s19/{task['episode_num']:03d}"
            task["id"] = f"s19-e{task['episode_num']:02d}-t{task['task_num']:02d}"
        elif title in s20_titles and task["season"] != "s20":
            task["season"] = "s20"
            task["episode_key"] = f"s20/{task['episode_num']:03d}"
            task["id"] = f"s20-e{task['episode_num']:02d}-t{task['task_num']:02d}"

    return tasks


# ---------------------------------------------------------------------------
# 5. Join tasks with episode data and build final output
# ---------------------------------------------------------------------------

def build_index():
    episodes = load_episodes_index()
    md_path = BASE / "all-tasks-by-season.md"
    raw_tasks = parse_markdown(str(md_path))
    raw_tasks = fix_season_assignments(raw_tasks, episodes)

    output = []
    unmatched_keys = set()
    matched_keys = set()

    for task in raw_tasks:
        ep_key = task.pop("episode_key")
        task.pop("task_num", None)
        ep_data = episodes.get(ep_key)

        if ep_data is None:
            unmatched_keys.add(ep_key)
            video_id = ""
            watch_url = ""
            embed_url = ""
            heatmap_peak_value = 0.0
            heatmap_peak_time = ""
        else:
            matched_keys.add(ep_key)
            video_id = ep_data.get("video_id", "")
            ts = task.get("timestamp_seconds")

            if ts is not None:
                watch_url = f"https://youtube.com/watch?v={video_id}&t={ts}"
                embed_url = f"https://youtube.com/embed/{video_id}?start={ts}"
            else:
                watch_url = f"https://youtube.com/watch?v={video_id}"
                embed_url = f"https://youtube.com/embed/{video_id}"

            heatmap = ep_data.get("heatmap", [])
            heatmap_peak_value, heatmap_peak_time = get_heatmap_peak(heatmap)

        entry = {
            "id": task["id"],
            "season": task["season"],
            "episode_num": task["episode_num"],
            "episode_title": task["episode_title"],
            "video_id": video_id,
            "watch_url": watch_url,
            "embed_url": embed_url,
            "timestamp_seconds": task.get("timestamp_seconds"),
            "timestamp_display": task.get("timestamp_display", ""),
            "task_description": task.get("task_description", ""),
            "task_summary": task.get("task_summary", ""),
            "task_type": task.get("task_type", "solo"),
            "is_crowd_favorite": task.get("is_crowd_favorite", False),
            "heatmap_peak_value": heatmap_peak_value,
            "heatmap_peak_time": heatmap_peak_time,
        }
        output.append(entry)

    # Write output
    out_path = BASE / "tasks-index.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # ---- Report ----
    print(f"Total tasks indexed: {len(output)}")
    print(f"Unique episodes matched: {len(matched_keys)} / {len(episodes)} available")
    print(f"Episode keys with tasks but no video match: {len(unmatched_keys)}")
    if unmatched_keys:
        for k in sorted(unmatched_keys):
            count = sum(1 for t in output if f"{t['season']}/{t['episode_num']:03d}" == k)
            print(f"  UNMATCHED: {k} ({count} tasks)")

    # Season breakdown
    season_counts = {}
    for t in output:
        s = t["season"]
        season_counts[s] = season_counts.get(s, 0) + 1
    print("\nTasks per season:")
    for s in sorted(season_counts):
        print(f"  {s}: {season_counts[s]}")

    # Type breakdown
    type_counts = {}
    for t in output:
        tp = t["task_type"]
        type_counts[tp] = type_counts.get(tp, 0) + 1
    print("\nTasks by type:")
    for tp in sorted(type_counts):
        print(f"  {tp}: {type_counts[tp]}")

    crowd_favs = sum(1 for t in output if t["is_crowd_favorite"])
    print(f"\nCrowd favorites: {crowd_favs}")

    # Check for episodes in index with no tasks
    episodes_with_tasks = set()
    for t in output:
        episodes_with_tasks.add(f"{t['season']}/{t['episode_num']:03d}")
    missing_episodes = set(episodes.keys()) - episodes_with_tasks
    if missing_episodes:
        print(f"\nEpisodes in index with NO tasks parsed ({len(missing_episodes)}):")
        for k in sorted(missing_episodes):
            print(f"  {k}: {episodes[k].get('title', '?')[:60]}")

    # Sample output
    print("\n--- Sample tasks ---")
    # Pick first, a middle one, and last
    if output:
        samples = [output[0]]
        if len(output) > 2:
            samples.append(output[len(output) // 2])
        samples.append(output[-1])
        for s in samples:
            print(json.dumps(s, indent=2, ensure_ascii=False))
            print()


if __name__ == "__main__":
    build_index()
