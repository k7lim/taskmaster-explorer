#!/usr/bin/env python3
"""Score Taskmaster tasks for party suitability."""

import json
import re
import sys

def lower_text(task):
    """Combine description and summary into searchable lowercase text."""
    return (task.get("task_description", "") + " " + task.get("task_summary", "")).lower()

def has_any(text, words):
    """Check if text contains any of the given words/phrases."""
    return any(w in text for w in words)

def score_safety(task):
    text = lower_text(task)
    ttype = task["task_type"]

    # Prize tasks: just bringing items
    if ttype == "prize":
        return 5, "prize task - just bringing items"

    # Dangerous: vehicles, heights, heavy machinery
    if has_any(text, ["vehicle", "kayak", "boat", "caravan", "car park",
                       "drive ", "driving", "motorway"]):
        return 1, "involves vehicles/transport"
    if has_any(text, ["height", "balcony", "roof", "climb", "ladder", "tree"]):
        if has_any(text, ["climb", "roof", "balcony", "ladder"]):
            return 1, "involves heights/climbing"
        return 2, "possible height concerns"
    if has_any(text, ["livestock", "horse", "animal pen"]):
        return 1, "involves animals/livestock"
    if has_any(text, ["treadmill", "machinery"]):
        return 1, "involves machinery"

    # Fire
    if has_any(text, ["fire", "flame", "candle", "lighter", "burn"]):
        return 2, "involves fire/flames"

    # Blindfold + movement
    if has_any(text, ["blindfold"]):
        if has_any(text, ["walk", "move", "navigate", "run", "step", "obstacle"]):
            return 2, "blindfolded movement"
        return 3, "blindfolded but stationary"

    # Throwing, launching
    if has_any(text, ["throw", "fling", "launch", "catapult", "hurl", "flung"]):
        return 3, "involves throwing/launching"

    # Water, messy
    if has_any(text, ["water", "splash", "wet", "pour ", "bath"]):
        if has_any(text, ["swim", "lake", "river", "pond", "pool"]):
            return 2, "involves water/swimming"
        return 3, "messy/water involved"
    if has_any(text, ["paint", "flour", "mess", "splat", "gunge", "gunk", "slime"]):
        return 3, "messy task"

    # Physical but safe
    if has_any(text, ["run ", "running", "sprint", "race ", "obstacle",
                       "physical", "carry", "heavy", "wheelie bin"]):
        return 3, "physical activity"

    # Food/eating
    if has_any(text, ["eat", "food", "cake", "biscuit", "fruit", "sandwich",
                       "cook", "bake", "melon", "banana", "coconut"]):
        return 4, "food-related task"

    # Word/drawing/guessing - safest
    if has_any(text, ["draw", "write", "word", "guess", "spell", "letter",
                       "describe", "charade", "impression", "impersonat",
                       "song", "sing", "hum", "poem", "limerick", "rhyme",
                       "memory", "remember", "identify", "recognize",
                       "trivia", "quiz", "question", "answer",
                       "act out", "perform", "recite"]):
        return 5, "mental/creative task"

    # Live tasks are generally safe studio tasks
    if ttype == "live":
        return 4, "live studio task"

    # Default
    return 4, "generally safe"

def score_equipment(task):
    text = lower_text(task)
    ttype = task["task_type"]

    # Prize tasks: bring your own stuff
    if ttype == "prize":
        return 5, "contestants bring items"

    # Impractical equipment
    if has_any(text, ["coconut bobsled", "caravan", "treadmill", "kayak",
                       "seesaw", "wheelie bin", "zipline", "trampoline",
                       "golf cart"]):
        return 1, "requires impractical equipment"
    if has_any(text, ["large outdoor", "field", "garden", "car park"]):
        return 2, "requires outdoor space"

    # Significant prep / building
    if has_any(text, ["build", "construct", "extension", "structure"]):
        if has_any(text, ["tower", "stack"]):
            return 3, "building with simple items"
        return 2, "requires building/construction"
    if has_any(text, ["special equipment", "machine", "robot"]):
        return 2, "requires special equipment"

    # Costumes
    if has_any(text, ["costume", "disguise", "dress up", "outfit", "clothing",
                       "boiler suit", "smock", "hairdressing"]):
        return 3, "needs costumes/clothing"

    # Moderate shopping
    if has_any(text, ["specific prop", "mannequin", "dummy", "wig"]):
        return 3, "needs specific props"

    # Balloons, eggs, simple supplies
    if has_any(text, ["balloon", "egg", "cup", "can ", "cans ", "tin ",
                       "rubber duck", "toilet roll", "toothbrush",
                       "spaghetti", "marshmallow", "straw"]):
        return 4, "simple supplies needed"

    # Paper, pens, drawing
    if has_any(text, ["draw", "write", "paper", "pen ", "pencil", "card"]):
        return 5, "just paper and pens"
    if has_any(text, ["word", "guess", "say ", "speak", "talk", "voice",
                       "sing", "hum", "noise", "sound", "impression",
                       "describe", "question", "answer", "memory"]):
        return 5, "no equipment needed"

    # Food tasks - need food items
    if has_any(text, ["eat", "food", "cake", "biscuit", "fruit", "sandwich",
                       "cook", "bake", "melon", "banana"]):
        return 4, "needs food items"

    # Paint
    if has_any(text, ["paint"]):
        return 3, "needs paint supplies"

    # Live tasks usually have simple props provided
    if ttype == "live":
        return 4, "simple live task props"

    # Default
    return 3, "some supplies needed"

def score_group_fun(task):
    text = lower_text(task)
    ttype = task["task_type"]

    # Live tasks - designed for audience
    if ttype == "live":
        return 5, "live studio task - built for groups"

    # Prize tasks
    if ttype == "prize":
        return 4, "everyone brings something"

    # Team tasks
    if ttype == "team":
        return 4, "team format works for parties"

    # Filming required
    if has_any(text, ["film", "video", "footage", "record", "camera",
                       "photograph", "photo "]):
        if has_any(text, ["film", "video", "footage", "record"]):
            return 2, "requires filming"
        return 3, "involves photos"

    # Long duration
    if has_any(text, ["hour", "day ", "days", "week", "month", "year",
                       "five month", "tomorrow"]):
        return 1, "takes too long for a party"
    # Check for long minutes
    mins_match = re.search(r'(\d+)\s*minute', text)
    if mins_match and int(mins_match.group(1)) > 20:
        return 2, "takes too long (>20 min)"

    # Requires outdoor/large space
    if has_any(text, ["outside", "outdoor", "garden", "field", "car park",
                       "lake", "river", "furthest from"]):
        return 2, "needs outdoor space"

    # Requires isolation / going somewhere
    if has_any(text, ["alone", "isolation", "private", "secret location",
                       "leave the house"]):
        return 2, "requires isolation/solo"

    # Word games, bluffing, guessing - party gold
    if has_any(text, ["guess", "bluff", "charade", "impression", "impersonat",
                       "act out", "mime", "word game"]):
        return 5, "guessing/bluffing game"
    if has_any(text, ["say a word", "say a ", "letter word", "spell",
                       "rhyme", "song", "sing", "hum", "noise", "sound"]):
        return 5, "word/sound game"

    # Drawing/creative with spectator value
    if has_any(text, ["draw", "paint", "sculpt", "make a face",
                       "portrait", "picture"]):
        return 4, "creative with spectator value"

    # Performance
    if has_any(text, ["perform", "present", "speech", "poem", "limerick",
                       "soap opera", "trailer", "dramatic"]):
        return 4, "performance task"

    # General solo tasks
    return 3, "adaptable to group format"


def generate_party_notes(task, safety, equip, gfun):
    """Generate a brief adaptation note."""
    text = lower_text(task)
    ttype = task["task_type"]
    score = safety[0] * equip[0] * gfun[0]

    if score >= 48:
        # Good party task - how to adapt
        if ttype == "live":
            return "Ready to go - already a live group task"
        if ttype == "prize":
            return "Everyone brings an item, group votes on winner"
        if ttype == "team":
            return "Split into teams and compete"
        if has_any(text, ["draw", "paint", "write"]):
            return "Give everyone paper/pens, compare results"
        if has_any(text, ["guess", "bluff", "word"]):
            return "Play as a group round-robin style"
        if has_any(text, ["sing", "hum", "noise", "sound", "impression"]):
            return "Take turns performing, group judges"
        if has_any(text, ["eat", "food", "cake", "fruit"]):
            return "Set up food challenge station, everyone competes"
        return "Run simultaneously, group votes on winner"
    else:
        # Not great - why
        reasons = []
        if safety[0] <= 2:
            reasons.append(f"safety concern: {safety[1]}")
        if equip[0] <= 2:
            reasons.append(f"equipment issue: {equip[1]}")
        if gfun[0] <= 2:
            reasons.append(f"fun issue: {gfun[1]}")
        if reasons:
            return "Not ideal - " + "; ".join(reasons)
        return "Needs significant adaptation for party format"


def score_tasks(tasks):
    for task in tasks:
        safety = score_safety(task)
        equip = score_equipment(task)
        gfun = score_group_fun(task)

        party_score = safety[0] * equip[0] * gfun[0]
        party_adaptable = party_score >= 48

        task["safety"] = safety[0]
        task["safety_note"] = safety[1]
        task["equipment"] = equip[0]
        task["equipment_note"] = equip[1]
        task["group_fun"] = gfun[0]
        task["group_fun_note"] = gfun[1]
        task["party_score"] = party_score
        task["party_adaptable"] = party_adaptable
        task["party_notes"] = generate_party_notes(task, safety, equip, gfun)

    return tasks


def print_summary(tasks):
    # Sort by party_score, with crowd favorites boosted
    def sort_key(t):
        boost = 10 if t["is_crowd_favorite"] else 0
        return t["party_score"] + boost

    ranked = sorted(tasks, key=sort_key, reverse=True)

    print("=" * 80)
    print("TASKMASTER PARTY SUITABILITY SCORES")
    print("=" * 80)

    # Top 30
    print("\n--- TOP 30 PARTY TASKS ---")
    print(f"{'#':>3} {'Score':>5} {'S':>2} {'E':>2} {'G':>2} {'Fav':>4} {'Type':<6} {'ID':<14} Description")
    print("-" * 120)
    for i, t in enumerate(ranked[:30], 1):
        fav = " *" if t["is_crowd_favorite"] else ""
        desc = t["task_description"][:70]
        print(f"{i:>3} {t['party_score']:>5} {t['safety']:>2} {t['equipment']:>2} {t['group_fun']:>2} {fav:>4} {t['task_type']:<6} {t['id']:<14} {desc}")

    # Counts
    adaptable = sum(1 for t in tasks if t["party_adaptable"])
    total = len(tasks)
    print(f"\n--- SUMMARY ---")
    print(f"Total tasks: {total}")
    print(f"Party-adaptable (score >= 48): {adaptable} ({100*adaptable/total:.0f}%)")
    print(f"Not suitable: {total - adaptable} ({100*(total-adaptable)/total:.0f}%)")

    # Score distribution
    print(f"\n--- SCORE DISTRIBUTION ---")
    brackets = [
        ("100-125 (excellent)", 100, 126),
        ("64-99  (great)", 64, 100),
        ("48-63  (good)", 48, 64),
        ("27-47  (marginal)", 27, 48),
        ("1-26   (poor)", 1, 27),
    ]
    for label, lo, hi in brackets:
        count = sum(1 for t in tasks if lo <= t["party_score"] < hi)
        bar = "#" * count
        print(f"  {label:>25}: {count:>3}  {bar}")

    # By dimension
    for dim in ["safety", "equipment", "group_fun"]:
        print(f"\n  {dim} distribution:")
        for score in range(5, 0, -1):
            count = sum(1 for t in tasks if t[dim] == score)
            bar = "#" * (count // 2)
            print(f"    {score}: {count:>3}  {bar}")

    # Crowd favorites that are party-adaptable
    fav_adaptable = [t for t in tasks if t["is_crowd_favorite"] and t["party_adaptable"]]
    print(f"\n--- CROWD FAVORITES THAT WORK AT PARTIES: {len(fav_adaptable)} ---")
    for t in sorted(fav_adaptable, key=lambda x: x["party_score"], reverse=True)[:15]:
        desc = t["task_description"][:65]
        print(f"  [{t['party_score']:>3}] {t['id']:<14} {desc}")


def main():
    with open("tasks-index.json") as f:
        tasks = json.load(f)

    print(f"Loaded {len(tasks)} tasks")

    tasks = score_tasks(tasks)

    with open("tasks-index-scored.json", "w") as f:
        json.dump(tasks, f, indent=2)
    print(f"Wrote tasks-index-scored.json")

    print_summary(tasks)


if __name__ == "__main__":
    main()
