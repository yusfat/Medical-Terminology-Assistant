# Medical Terminology Assistant 🩺

A simple but effective open-source tool that helps medical, nursing, and healthcare students learn medical prefixes, roots, suffixes, and full terms through active recall, spaced repetition, and reverse practice.

## The Problem

Medical students are expected to memorize thousands of terms.  
Traditional flashcard apps like Anki are powerful but often have a steep learning curve.  
This project offers a lightweight, beginner-friendly alternative that works both in the terminal and on the web.

## Features

- Mixed quizzes (prefixes, roots, suffixes, and full terms)
- Reverse practice (meaning → term)
- Spaced repetition system
- Wrong-answer tracking
- Grouped learning by category
- Comprehension passages
- Clean separation of data and code (`terms.csv` + `quiz.py`)
- Easy content management — just edit the CSV file to add new terms

## Why This Project?

Medical terminology is largely built from Greek and Latin word parts.  
By mastering the common building blocks, students can decode hundreds of terms instead of memorizing them one by one.

## Quick Start

### Option 1: CLI Version (Terminal / Termux)

```bash
git clone https://github.com/yusfat/Medical-Terminology-Assistant.git
cd Medical-Terminology-Assistant
python quiz.py


