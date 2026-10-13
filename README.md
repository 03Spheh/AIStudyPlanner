# AI-Based Personalized Study Planner

Capstone project, Sol Plaatje University (Computer Science & Information Technology).
Author: Sphelele Gift Ngxongo (202425077)

A Flask + SQLite web application that builds a weekly study timetable from a
student's modules, assessment dates and free time, and analyses uploaded PDF
study materials (summary, key topics, practice questions).

## Set-up
1. Install Python 3.10+ (and Node.js only if you want to run the scheduler tests).
2. `pip install -r requirements.txt`
3. From this folder run: `python -m app.web`
4. Open http://127.0.0.1:5000, register, then log in.

## Tests
- Application tests: `python tests/test_app.py` (20 checks, uses a temporary database)
- Scheduler tests: `node tests/test_scheduler.js` (10 checks)

## Notes
- The timetable scheduler is rule-based, not a trained machine-learning model.
- Do not commit real student data, private course materials or the database file.
