# Taskmaster Explorer

Browse 311 tasks from six seasons of Taskmaster — UK Series 4, 5, 7, 19, 20 and NZ Series 2. Watch any task on YouTube, see which moments people replayed most, and find tasks you can steal for your own party.

**Live site:** [k7lim.github.io/taskmaster-explorer](https://k7lim.github.io/taskmaster-explorer/)

## What's here

Every task card from 56 episodes, extracted from YouTube subtitles and verified against the [Taskmaster fan wiki](https://taskmaster.fandom.com/wiki/Taskmaster). Each task links directly to its moment in the full episode on YouTube.

Each task has an engagement score from YouTube's "Most Replayed" heatmap — how heavily its segment was replayed relative to the rest of the episode.

Toggle Party Mode to filter to 255 tasks that work at house parties, rated on safety (will anyone get hurt?), equipment (do you need more than household items?), and group fun (will everyone actually enjoy this?), with notes on how to adapt each one.

## How it was built

Subtitles from all 56 episodes were fed through transcript extraction to pull out task descriptions and timestamps. YouTube's heatmap metadata provided the engagement scores. Each task was then scored for party suitability and cross-checked against the Taskmaster fan wiki. The site is a single HTML file with the data baked in.

## Files

| File | What it does |
|------|-------------|
| `index.html` | The entire site — self-contained, no build step |
| `frames/` | 311 screenshot JPEGs extracted from episodes |
| `tasks-index-scored.json` | Structured data for all 311 tasks |
| `all-tasks-by-season.md` | Human-readable task listing |
| `build-index.py` | Joins task extractions with video metadata |
| `score-party.py` | Keyword-based party scoring (superseded by llm-rescore.py) |
| `llm-rescore.py` | Party scoring with per-task judgment calls |
| `extract-frames.sh` | Downloads 1 frame per task from YouTube |
| `add-wiki-links.py` | Adds wiki URLs for each task and series |

## Seasons covered

| Season | Episodes | Tasks | Contestants |
|--------|----------|-------|-------------|
| UK Series 4 | 8 | 48 | Hugh Dennis, Joe Lycett, Lolly Adefope, Mel Giedroyc, Noel Fielding |
| UK Series 5 | 8 | 49 | Aisling Bea, Bob Mortimer, Mark Watson, Nish Kumar, Sally Phillips |
| UK Series 7 | 10 | 58 | James Acaster, Jessica Knappett, Kerry Godliman, Phil Wang, Rhod Gilbert |
| NZ Series 2 | 10 | 56 | David Correos, Guy Montgomery, Laura Daniel, Matt Heath, Ursula Carlson |
| UK Series 19 | 10 | 51 | Fatiha El-Ghorri, Jason Mantzoukas, Mathew Baynton, Rosie Ramsey, Stevie Martin |
| UK Series 20 | 10 | 49 | Ania Magliano, Maisie Adam, Phil Ellis, Reece Shearsmith, Sanjeev Bhaskar |

These are the seasons currently available as full episodes on the [official Taskmaster YouTube channel](https://www.youtube.com/Taskmaster).

## Credits

Task data sourced from the [official Taskmaster YouTube channel](https://www.youtube.com/Taskmaster). Task descriptions verified against [taskmaster.fandom.com](https://taskmaster.fandom.com/). Taskmaster is owned by Avalon Television.

Built with [Claude Code](https://claude.ai/code).
