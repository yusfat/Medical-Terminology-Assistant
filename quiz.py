#!/usr/bin/env python3
"""
Medical Terminology Assistant
Data lives in terms.csv | Logic lives here
"""

import csv
import random
import os
import json
from datetime import datetime, timedelta

DATA_FILE = "progress.json"
RECENT_FILE = "recent.json"
TERMS_FILE = "terms.csv"

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def load_terms():
    terms = []
    try:
        with open(TERMS_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                terms.append({
                    "type": row["type"].strip().lower(),
                    "term": row["term"].strip(),
                    "meaning": row["meaning"].strip(),
                    "category": row.get("category", "General").strip()
                })
    except FileNotFoundError:
        print("ERROR: terms.csv not found!")
        exit()
    return terms

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename) as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def is_correct(user_answer, correct_meaning):
    user = user_answer.strip().lower()
    correct = correct_meaning.lower()
    if len(user) < 3:
        return False
    if user == correct or correct.startswith(user) or user in correct:
        return True
    words = [w for w in correct.replace(",", " ").replace("/", " ").split() if len(w) > 3]
    matches = sum(1 for w in words if w in user)
    return matches >= 1 and len(user) >= 4

def get_questions(all_terms, num):
    recent = load_json(RECENT_FILE, [])
    available = [t for t in all_terms if t["term"] not in recent]
    if len(available) < num:
        available = all_terms[:]
    questions = random.sample(available, min(num, len(available)))
    new_recent = [q["term"] for q in questions] + recent
    save_json(RECENT_FILE, new_recent[:70])
    return questions

def show_menu():
    print("\n=== Medical Terminology Assistant ===")
    print("1. Review by type (prefix/root/suffix/full)")
    print("2. Mixed Quiz")
    print("3. Random Full Terms (min 5)")
    print("4. Review Wrong Answers")
    print("5. Spaced Repetition")
    print("6. Reverse Practice (meaning → term)")
    print("7. Grouped Similar Meanings")
    print("8. Comprehension Passage")
    print("9. Build Full Term example")
    print("10. English / Medical Overlap")
    print("0. Exit")
    return input("\nChoose: ").strip()

def review_by_type(terms):
    clear()
    print("1. prefix  2. root  3. suffix  4. full")
    choice = input("Choose type: ").strip()
    mapping = {"1": "prefix", "2": "root", "3": "suffix", "4": "full"}
    selected = mapping.get(choice)
    if not selected:
        print("Invalid choice")
        input("Press Enter...")
        return
    filtered = [t for t in terms if t["type"] == selected]
    print(f"\n--- {selected.upper()} ({len(filtered)} items) ---")
    for t in filtered:
        print(f"{t['term']:32} → {t['meaning']}")
    input("\nPress Enter...")

def mixed_quiz(terms):
    clear()
    try:
        num = int(input("How many questions? (8-25): ") or "12")
        num = max(5, min(num, 30))
    except:
        num = 12

    questions = get_questions(terms, num)
    progress = load_json(DATA_FILE, {"wrong": [], "next_review": {}})
    score = 0
    wrongs = []

    for i, q in enumerate(questions, 1):
        print(f"\n{i}. [{q['type']}] What does '{q['term']}' mean?")
        ans = input("Answer: ").strip()
        if is_correct(ans, q["meaning"]):
            print("✓ Correct")
            score += 1
        else:
            print(f"✗ {q['meaning']}")
            wrongs.append(q)

    for item in wrongs:
        if not any(w["term"] == item["term"] for w in progress["wrong"]):
            progress["wrong"].append(item)
            progress["next_review"][item["term"]] = (datetime.now() + timedelta(hours=6)).isoformat()

    save_json(DATA_FILE, progress)
    print(f"\nScore: {score}/{len(questions)}")
    input("Press Enter...")

def random_full_terms(terms):
    clear()
    fulls = [t for t in terms if t["type"] == "full"]
    if not fulls:
        print("No full terms in CSV.")
        input("Press Enter...")
        return
    print("--- Random Full Terms (minimum 5) ---")
    count = 0
    while True:
        batch = random.sample(fulls, min(5, len(fulls)))
        for t in batch:
            count += 1
            print(f"\n{count}. {t['term']}")
            input("Think of the meaning → Press Enter")
            print(f"   Meaning: {t['meaning']}")
        if input("\nWant 5 more? (y/n): ").strip().lower() != "y":
            break
    input("Press Enter...")

def review_wrong():
    clear()
    progress = load_json(DATA_FILE, {"wrong": [], "next_review": {}})
    wrongs = progress.get("wrong", [])
    if not wrongs:
        print("No wrong answers yet.")
        input("Press Enter...")
        return
    print(f"--- Wrong Answers ({len(wrongs)}) ---")
    for i, item in enumerate(wrongs, 1):
        print(f"{i}. [{item['type']}] {item['term']} → {item['meaning']}")
    print("\na = Clear all | Enter = Back")
    if input("Choice: ").strip().lower() == "a":
        progress["wrong"] = []
        progress["next_review"] = {}
        save_json(DATA_FILE, progress)
        print("Cleared.")
    input("Press Enter...")

def spaced_repetition():
    clear()
    try:
        hours = int(input("Interval in hours (default 6): ") or "6")
        hours = max(1, min(hours, 72))
    except:
        hours = 6

    progress = load_json(DATA_FILE, {"wrong": [], "next_review": {}})
    now = datetime.now()
    due = []
    for w in progress["wrong"]:
        next_time = progress["next_review"].get(w["term"])
        if next_time:
            try:
                if datetime.fromisoformat(next_time) <= now:
                    due.append(w)
            except:
                due.append(w)

    if not due:
        print("Nothing due right now.")
        input("Press Enter...")
        return

    print(f"{len(due)} items due\n")
    random.shuffle(due)
    for item in due:
        print(f"[{item['type']}] What does '{item['term']}' mean?")
        ans = input("Answer: ").strip()
        if is_correct(ans, item["meaning"]):
            print("✓ Remembered")
            progress["wrong"] = [w for w in progress["wrong"] if w["term"] != item["term"]]
            progress["next_review"][item["term"]] = (now + timedelta(hours=hours*2)).isoformat()
        else:
            print(f"✗ {item['meaning']}")
            progress["next_review"][item["term"]] = (now + timedelta(hours=hours)).isoformat()
    save_json(DATA_FILE, progress)
    input("\nFinished. Press Enter...")

def reverse_practice(terms):
    clear()
    fulls = [t for t in terms if t["type"] == "full"]
    if len(fulls) < 5:
        print("Not enough full terms.")
        return
    items = random.sample(fulls, min(8, len(fulls)))
    score = 0
    for t in items:
        print(f"\nMeaning: {t['meaning']}")
        ans = input("Medical term? ").strip().lower()
        if t["term"].lower() in ans or ans in t["term"].lower():
            print("✓ Correct")
            score += 1
        else:
            print(f"✗ {t['term']}")
    print(f"\nScore: {score}/{len(items)}")
    input("Press Enter...")

def grouped_meanings(terms):
    clear()
    print("--- Grouped by Category ---")
    categories = {}
    for t in terms:
        cat = t["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t)

    for cat, items in categories.items():
        print(f"\n{cat}:")
        for item in items[:8]:  # show limited to avoid too much text
            print(f"  • {item['term']} → {item['meaning']}")
        if len(items) > 8:
            print(f"  ... and {len(items)-8} more")
    input("\nPress Enter...")

def comprehension_passage(terms):
    clear()
    passages = [
        "The patient was admitted with tachycardia and dyspnea. The cardiologist ordered an electrocardiogram and noted mild cardiomegaly.",
        "Histology results confirmed inflammation. The dermatologist diagnosed dermatitis and recommended treatment.",
        "After the appendectomy the patient developed a small hemorrhage. Hematology was consulted regarding possible anemia.",
        "The neurologist examined the patient for signs of neuropathy after episodes of apnea were reported."
    ]
    passage = random.choice(passages)
    print("--- Comprehension Passage ---\n")
    print(passage)
    print("\nTry to identify the medical terms and their meanings.")
    input("\nPress Enter to see matched terms...")
    found = []
    for t in terms:
        if t["term"].lower() in passage.lower() and t["type"] == "full":
            found.append(f"{t['term']} → {t['meaning']}")
    if found:
        print("\nKey terms found:")
        for f in found:
            print(" •", f)
    else:
        print("\nNo exact full terms matched this time.")
    input("\nPress Enter...")

def build_full_term_example(terms):
    clear()
    prefixes = [t for t in terms if t["type"] == "prefix"]
    roots = [t for t in terms if t["type"] == "root"]
    suffixes = [t for t in terms if t["type"] == "suffix"]
    if not (prefixes and roots and suffixes):
        print("Not enough data in CSV.")
        return
    pre = random.choice(prefixes)
    root = random.choice(roots)
    suf = random.choice(suffixes)
    print("--- Build a Full Term ---")
    print(f"\nPrefix : {pre['term']} ({pre['meaning']})")
    print(f"Root   : {root['term']} ({root['meaning']})")
    print(f"Suffix : {suf['term']} ({suf['meaning']})")
    print("\nTry combining them in your mind.")
    input("\nPress Enter...")

def english_overlap():
    clear()
    print("--- English / Medical Overlap ---")
    print("hyper-     → hyperactive, hypersensitive, hypertension")
    print("hypo-      → hypodermic, hypothermia, hypotension")
    print("pre-       → preview, prehistoric, prenatal")
    print("post-      → postpone, postwar, postnatal")
    print("sub-       → subway, submarine, subcutaneous")
    print("inter-     → international, intercostal")
    print("micro-     → microscope, microbiology")
    print("macro-     → macroscopic, macroeconomics")
    print("-ology     → biology, psychology, cardiology")
    print("-itis      → arthritis, dermatitis (mostly medical)")
    print("-phobia    → claustrophobia, arachnophobia")
    print("\nSame word parts appear in both everyday English and medicine.")
    input("\nPress Enter...")

def main():
    terms = load_terms()
    print(f"Loaded {len(terms)} terms from terms.csv")
    while True:
        choice = show_menu()
        if choice == "1":
            review_by_type(terms)
        elif choice == "2":
            mixed_quiz(terms)
        elif choice == "3":
            random_full_terms(terms)
        elif choice == "4":
            review_wrong()
        elif choice == "5":
            spaced_repetition()
        elif choice == "6":
            reverse_practice(terms)
        elif choice == "7":
            grouped_meanings(terms)
        elif choice == "8":
            comprehension_passage(terms)
        elif choice == "9":
            build_full_term_example(terms)
        elif choice == "10":
            english_overlap()
        elif choice == "0":
            print("Keep practising!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()


