from datetime import date, datetime


# ==========================================
# AI-BASED PERSONALIZED STUDY PLANNER
# ==========================================

print("==========================================")
print("       AI STUDY PLANNER")
print("==========================================")


# ==========================================
# MODULE INFORMATION
# ==========================================

number_of_modules = int(
    input("\nHow many modules do you have? ")
)


maximum_study_hours = float(
    input(
        "What is the maximum number of hours "
        "you want to study per day? "
    )
)


modules = []


for i in range(number_of_modules):

    print("\nModule", i + 1)

    name = input("Enter module name: ")

    credit_score = float(
        input("Enter module credit score: ")
    )

    assessment = input(
        "Enter assessment type "
        "[Test/Exam/Assignment/Project]: "
    )

    assessment_date = input(
        "Enter assessment date (YYYY-MM-DD): "
    )

    module = {
        "name": name,
        "credit_score": credit_score,
        "assessment": assessment,
        "assessment_date": assessment_date
    }

    modules.append(module)


# ==========================================
# ASSESSMENT SCORES
# ==========================================

assessment_scores = {
    "Test": 2,
    "Exam": 3,
    "Assignment": 1,
    "Project": 2
}


# ==========================================
# CURRENT DATE
# ==========================================

# Fixed date while testing.
# Later we will change this to date.today()

today = date(2026, 9, 27)


# ==========================================
# CALCULATE PRIORITY
# ==========================================

for module in modules:

    assessment_date = datetime.strptime(
        module["assessment_date"],
        "%Y-%m-%d"
    ).date()


    days_remaining = (
        assessment_date - today
    ).days


    # ======================================
    # URGENCY SCORE
    # ======================================

    if days_remaining <= 3:
        urgency_score = 5

    elif days_remaining <= 7:
        urgency_score = 4

    elif days_remaining <= 14:
        urgency_score = 3

    elif days_remaining <= 30:
        urgency_score = 2

    elif days_remaining <= 60:
        urgency_score = 1

    else:
        urgency_score = 0


    # ======================================
    # ASSESSMENT SCORE
    # ======================================

    assessment_type = (
        module["assessment"]
        .strip()
        .title()
    )


    assessment_score = assessment_scores.get(
        assessment_type,
        1
    )


    # ======================================
    # PRIORITY SCORE
    # ======================================

    priority_score = (
        module["credit_score"]
        + urgency_score
        + assessment_score
    )


    module["days_remaining"] = days_remaining

    module["urgency_score"] = urgency_score

    module["assessment_score"] = (
        assessment_score
    )

    module["priority_score"] = (
        priority_score
    )


# ==========================================
# SORT MODULES
# ==========================================

modules.sort(
    key=lambda module:
    module["priority_score"],
    reverse=True
)


# ==========================================
# DISPLAY PRIORITY
# ==========================================

print("\n")
print("==========================================")
print("           STUDY PRIORITY")
print("==========================================")


for position, module in enumerate(
    modules,
    start=1
):

    print(
        position,
        ".",
        module["name"],
        "→ Priority",
        round(
            module["priority_score"],
            2
        )
    )

    print(
        "   Credit Score:",
        module["credit_score"]
    )

    print(
        "   Assessment:",
        module["assessment"]
    )

    print(
        "   Days remaining:",
        module["days_remaining"]
    )

    print(
        "   Urgency Score:",
        module["urgency_score"]
    )

    print(
        "   Assessment Score:",
        module["assessment_score"]
    )


# ==========================================
# STUDENT AVAILABILITY
# ==========================================

print("\n")
print("==========================================")
print("        STUDENT AVAILABILITY")
print("==========================================")


print(
    "Enter the time you are normally free "
    "to study on each day."
)


print(
    "Use 24-hour format, for example 19:00."
)


print(
    "For overnight study, enter the normal "
    "times, for example 20:00 to 04:00."
)


days_of_week = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


availability = {}


for day in days_of_week:

    print("\n" + day)


    available = input(
        "Are you available to study? [Yes/No]: "
    ).strip().lower()


    if available == "yes":

        start_time = input(
            "From what time are you free? [HH:MM]: "
        )


        end_time = input(
            "Until what time are you free? [HH:MM]: "
        )


        start = datetime.strptime(
            start_time,
            "%H:%M"
        )


        end = datetime.strptime(
            end_time,
            "%H:%M"
        )


        start_minutes = (
            start.hour * 60
            + start.minute
        )


        end_minutes = (
            end.hour * 60
            + end.minute
        )


        # ==================================
        # NORMAL TIME
        # ==================================

        if end_minutes > start_minutes:

            available_minutes = (
                end_minutes
                - start_minutes
            )

            overnight = False


        # ==================================
        # OVERNIGHT TIME
        # ==================================

        elif end_minutes < start_minutes:

            available_minutes = (
                1440
                - start_minutes
                + end_minutes
            )

            overnight = True


        # ==================================
        # INVALID / SAME TIME
        # ==================================

        else:

            available_minutes = 0

            overnight = False


        availability[day] = {

            "start": start_time,

            "end": end_time,

            "start_minutes": start_minutes,

            "end_minutes": end_minutes,

            "minutes": available_minutes,

            "overnight": overnight

        }


    else:

        availability[day] = {

            "start": None,

            "end": None,

            "start_minutes": None,

            "end_minutes": None,

            "minutes": 0,

            "overnight": False

        }


# ==========================================
# DISPLAY AVAILABILITY
# ==========================================

print("\n")
print("==========================================")
print("        YOUR AVAILABILITY")
print("==========================================")


total_available_minutes = 0


for day in days_of_week:

    day_info = availability[day]


    if day_info["minutes"] > 0:

        hours = (
            day_info["minutes"]
            / 60
        )


        if day_info["overnight"]:

            print(
                day,
                "→",
                day_info["start"],
                "-",
                day_info["end"],
                "(overnight,",
                round(hours, 2),
                "hours)"
            )


        else:

            print(
                day,
                "→",
                day_info["start"],
                "-",
                day_info["end"],
                "(",
                round(hours, 2),
                "hours)"
            )


        total_available_minutes += (
            day_info["minutes"]
        )


    else:

        print(
            day,
            "→ Not available"
        )


# ==========================================
# TOTAL AVAILABLE TIME
# ==========================================

print("\n")


print(
    "Total weekly available time:",
    round(
        total_available_minutes / 60,
        2
    ),
    "hours"
)


print(
    "Maximum study time per day:",
    maximum_study_hours,
    "hours"
)


# ==========================================
# CALCULATE PRIORITY PERCENTAGE
# ==========================================

total_priority = sum(
    module["priority_score"]
    for module in modules
)


for module in modules:

    module["priority_percentage"] = (
        module["priority_score"]
        / total_priority
    )


# ==========================================
# CREATE STUDY WINDOWS
# ==========================================

study_windows = {}


for day in days_of_week:

    study_windows[day] = []


for index, day in enumerate(days_of_week):

    day_info = availability[day]


    if day_info["minutes"] <= 0:
        continue


    start_minutes = (
        day_info["start_minutes"]
    )


    end_minutes = (
        day_info["end_minutes"]
    )


    # ======================================
    # NORMAL AVAILABILITY
    # ======================================

    if not day_info["overnight"]:

        study_windows[day].append(
            (
                start_minutes,
                end_minutes
            )
        )


    # ======================================
    # OVERNIGHT AVAILABILITY
    # ======================================

    else:

        study_windows[day].append(
            (
                start_minutes,
                1440
            )
        )


        next_day_index = (
            index + 1
        ) % len(days_of_week)


        next_day = days_of_week[
            next_day_index
        ]


        study_windows[next_day].insert(
            0,
            (
                0,
                end_minutes
            )
        )


# ==========================================
# STUDY SESSION SETTINGS
# ==========================================

STUDY_BLOCK_MINUTES = 50

BREAK_MINUTES = 15


# ==========================================
# GENERATE STUDY SLOTS
# ==========================================

print("\n")
print("==========================================")
print("       GENERATING STUDY TIMETABLE")
print("==========================================")


study_slots = []


maximum_daily_minutes = (
    maximum_study_hours * 60
)


for day in days_of_week:

    daily_study_minutes = 0


    for window in study_windows[day]:

        start_minutes = window[0]

        end_minutes = window[1]


        current_minutes = (
            start_minutes
        )


        while (
            current_minutes
            + STUDY_BLOCK_MINUTES
            <= end_minutes
        ):

            if (
                daily_study_minutes
                + STUDY_BLOCK_MINUTES
                > maximum_daily_minutes
            ):

                break


            session_start = (
                current_minutes
            )


            session_end = (
                current_minutes
                + STUDY_BLOCK_MINUTES
            )


            study_slots.append(
                {
                    "day": day,

                    "start": session_start,

                    "end": session_end
                }
            )


            daily_study_minutes += (
                STUDY_BLOCK_MINUTES
            )


            current_minutes = (
                session_end
                + BREAK_MINUTES
            )


        if (
            daily_study_minutes
            >= maximum_daily_minutes
        ):

            break


# ==========================================
# CHECK FOR STUDY SLOTS
# ==========================================

if len(study_slots) == 0:

    print("\n")

    print(
        "No study sessions could be created."
    )

    print(
        "Please check your availability "
        "and maximum study hours."
    )

    exit()


# ==========================================
# CALCULATE MODULE SESSION TARGETS
# ==========================================

total_study_slots = len(
    study_slots
)


for module in modules:

    exact_sessions = (
        total_study_slots
        * module["priority_percentage"]
    )


    module["exact_sessions"] = (
        exact_sessions
    )


    module["target_sessions"] = int(
        exact_sessions
    )


    module["session_remainder"] = (
        exact_sessions
        - module["target_sessions"]
    )


# ==========================================
# DISTRIBUTE REMAINING SESSIONS
# ==========================================

assigned_sessions = sum(
    module["target_sessions"]
    for module in modules
)


remaining_sessions = (
    total_study_slots
    - assigned_sessions
)


while remaining_sessions > 0:

    module_to_receive = max(
        modules,
        key=lambda module:
        module["session_remainder"]
    )


    module_to_receive[
        "target_sessions"
    ] += 1


    module_to_receive[
        "session_remainder"
    ] = 0


    remaining_sessions -= 1


# ==========================================
# REMAINING SESSIONS
# ==========================================

remaining_by_module = {}


for module in modules:

    remaining_by_module[
        module["name"]
    ] = module["target_sessions"]


# ==========================================
# ASSIGN MODULES TO STUDY SLOTS
# ==========================================

last_module = None


for slot in study_slots:

    available_modules = [

        module

        for module in modules

        if remaining_by_module[
            module["name"]
        ] > 0

    ]


    different_modules = [

        module

        for module in available_modules

        if module["name"]
        != last_module

    ]


    if len(different_modules) > 0:

        available_modules = (
            different_modules
        )


    selected_module = max(

        available_modules,

        key=lambda module:
        remaining_by_module[
            module["name"]
        ]

    )


    slot["module"] = (
        selected_module["name"]
    )


    remaining_by_module[
        selected_module["name"]
    ] -= 1


    last_module = (
        selected_module["name"]
    )


# ==========================================
# FORMAT TIME
# ==========================================

def format_time(total_minutes):

    total_minutes = (
        total_minutes % 1440
    )


    hours = (
        total_minutes // 60
    )


    minutes = (
        total_minutes % 60
    )


    return (
        f"{hours:02d}:{minutes:02d}"
    )


# ==========================================
# DISPLAY PERSONALIZED TIMETABLE
# ==========================================

print("\n")
print("==========================================")
print("          PERSONALIZED TIMETABLE")
print("==========================================")


current_day = None


for index, slot in enumerate(
    study_slots
):

    day = slot["day"]


    if day != current_day:

        print("\n")

        print(
            "------------------------------------------"
        )

        print(day)

        print(
            "------------------------------------------"
        )

        current_day = day


    print(

        format_time(slot["start"]),

        "-",

        format_time(slot["end"]),

        "→",

        slot["module"]

    )


    if index + 1 < len(study_slots):

        next_slot = study_slots[
            index + 1
        ]


        if (

            next_slot["day"] == day

            and next_slot["start"]
            == slot["end"]
            + BREAK_MINUTES

        ):

            print(
                "            BREAK →",
                BREAK_MINUTES,
                "minutes"
            )


# ==========================================
# STUDY SESSION SUMMARY
# ==========================================

print("\n")
print("==========================================")
print("        STUDY SESSION SUMMARY")
print("==========================================")


for module in modules:

    print(

        module["name"],

        "→",

        module["target_sessions"],

        "study sessions"

    )


print("\n")


print(
    "Total study sessions:",
    total_study_slots
)


print(
    "Each study session:",
    STUDY_BLOCK_MINUTES,
    "minutes"
)


print(
    "Break between sessions:",
    BREAK_MINUTES,
    "minutes"
)


# ==========================================
# TODAY'S STUDY SESSION
# ==========================================

print("\n")
print("==========================================")
print("        TODAY'S STUDY SESSION")
print("==========================================")


today_name = today.strftime("%A")


print(
    "Today is:",
    today_name
)


today_sessions = [

    slot

    for slot in study_slots

    if slot["day"] == today_name

]


if len(today_sessions) == 0:

    print("\n")

    print(
        "You have no scheduled study "
        "sessions for today."
    )


else:

    print("\n")

    print(
        "Your scheduled study sessions "
        "for today:"
    )

    print("\n")


    for slot in today_sessions:

        print(

            format_time(slot["start"]),

            "-",

            format_time(slot["end"]),

            "→",

            slot["module"]

        )


    # ======================================
    # SELECT NEXT STUDY SESSION
    # ======================================

    next_session = today_sessions[0]


    print("\n")

    print(
        "------------------------------------------"
    )

    print(
        "        NEXT STUDY SESSION"
    )

    print(
        "------------------------------------------"
    )


    print(

        "Module:",

        next_session["module"]

    )


    print(

        "Time:",

        format_time(
            next_session["start"]
        ),

        "-",

        format_time(
            next_session["end"]
        )

    )


    print("\n")


    print(
        "The timetable has automatically "
        "selected your study module."
    )


    print(
        "You do not need to choose what "
        "to study."
    )


    # ======================================
    # PREPARE STUDY MATERIAL
    # ======================================

    print("\n")


    prepare_material = input(

        "Would you like to prepare "
        "your study material? [Yes/No]: "

    ).strip().lower()


    if prepare_material == "yes":

        print("\n")
        print("==========================================")
        print("       STUDY MATERIAL INPUT")
        print("==========================================")


        print(
            "Scheduled module:",
            next_session["module"]
        )


        print("\n")


        # ==================================
        # MODULE SCOPE
        # ==================================

        print(
            "Enter the scope/topics for this module."
        )


        print(
            "Type each topic on a new line."
        )


        print(
            "Type DONE when you have finished."
        )


        scope_topics = []


        while True:

            topic = input(
                "Topic: "
            ).strip()


            if topic.upper() == "DONE":

                break


            if topic != "":

                scope_topics.append(topic)


        # ==================================
        # STUDENT NOTES
        # ==================================

        print("\n")


        print(
            "Now enter your lecture notes."
        )


        print(
            "You can type several lines."
        )


        print(
            "Type DONE when you have finished."
        )


        notes_lines = []


        while True:

            note = input(
                "Notes: "
            ).strip()


            if note.upper() == "DONE":

                break


            if note != "":

                notes_lines.append(note)


        notes = "\n".join(
            notes_lines
        )


        # ==================================
        # PAST PAPER
        # ==================================

        print("\n")


        past_paper_choice = input(

            "Do you have a past paper? "
            "[Yes/No]: "

        ).strip().lower()


        past_paper_questions = []


        if past_paper_choice == "yes":

            print("\n")


            print(
                "Enter the past-paper questions."
            )


            print(
                "Type each question on a new line."
            )


            print(
                "Type DONE when finished."
            )


            while True:

                question = input(
                    "Question: "
                ).strip()


                if question.upper() == "DONE":

                    break


                if question != "":

                    past_paper_questions.append(
                        question
                    )


        # ==================================
        # DISPLAY INPUT SUMMARY
        # ==================================

        print("\n")


        print(
            "=========================================="
        )


        print(
            "       STUDY MATERIAL PREPARATION"
        )


        print(
            "=========================================="
        )


        print(
            "Module:",
            next_session["module"]
        )


        print("\n")


        print(
            "Topics provided:",
            len(scope_topics)
        )


        for number, topic in enumerate(
            scope_topics,
            start=1
        ):

            print(
                number,
                ".",
                topic
            )


        print("\n")


        print(
            "Notes provided:",
            len(notes_lines),
            "lines"
        )


        if len(past_paper_questions) > 0:

            print(
                "Past-paper questions provided:",
                len(past_paper_questions)
            )

        else:

            print(
                "Past-paper questions provided: 0"
            )


        # ==================================
        # PREPARE BASIC STUDY MATERIAL
        # ==================================

        print("\n")


        print(
            "=========================================="
        )


        print(
            "       GENERATED STUDY MATERIAL"
        )


        print(
            "=========================================="
        )


        print("\n")


        print(
            "MODULE:",
            next_session["module"]
        )


        print("\n")


        print(
            "STUDY TOPICS"
        )


        print(
            "------------------------------------------"
        )


        for number, topic in enumerate(
            scope_topics,
            start=1
        ):

            print("\n")


            print(
                "TOPIC",
                number,
                ":",
                topic
            )


            print(
                "Key focus:"
            )


            print(
                "Review the definition, important "
                "concepts, examples and applications "
                "of this topic."
            )


            print(
                "Study tip:"
            )


            print(
                "Use your lecture notes first, then "
                "test your understanding using "
                "practice questions."
            )


        # ==================================
        # NOTES SUMMARY
        # ==================================

        print("\n")


        print(
            "LECTURE NOTES"
        )


        print(
            "------------------------------------------"
        )


        if notes != "":

            for note in notes_lines:

                print(
                    "•",
                    note
                )

        else:

            print(
                "No lecture notes were provided."
            )


        # ==================================
        # PRACTICE QUESTIONS
        # ==================================

        print("\n")


        print(
            "PRACTICE QUESTIONS"
        )


        print(
            "------------------------------------------"
        )


        for number, topic in enumerate(
            scope_topics,
            start=1
        ):

            print(
                number,
                ". Explain",
                topic,
                "in your own words."
            )


            print(
                number,
                ". Give one example of",
                topic + "."
            )


        # ==================================
        # PAST PAPER CONNECTION
        # ==================================

        if len(past_paper_questions) > 0:

            print("\n")


            print(
                "PAST PAPER CONNECTION"
            )


            print(
                "------------------------------------------"
            )


            print(
                "The following past-paper questions "
                "should be reviewed against the "
                "scope topics:"
            )


            for number, question in enumerate(
                past_paper_questions,
                start=1
            ):

                print(
                    number,
                    ".",
                    question
                )


        # ==================================
        # STUDENT CONFIRMATION
        # ==================================

        print("\n")


        print(
            "=========================================="
        )


        print(
            "        STUDENT CONFIRMATION"
        )


        print(
            "=========================================="
        )


        print(
            "The study material has been prepared "
            "for your scheduled module."
        )


        confirmation = input(

            "Are you ready to start studying? "
            "[Yes/No]: "

        ).strip().lower()


        if confirmation == "yes":

            print("\n")


            print(
                "=========================================="
            )


            print(
                "          STUDY SESSION STARTED"
            )


            print(
                "=========================================="
            )


            print(
                "Module:",
                next_session["module"]
            )


            print(
                "Study time:",
                format_time(
                    next_session["start"]
                ),
                "-",
                format_time(
                    next_session["end"]
                )
            )


            print("\n")


            print(
                "Focus on the topics in your scope."
            )


            print(
                "Use your notes to understand "
                "the concepts."
            )


            print(
                "Use the practice questions to "
                "test yourself."
            )


        else:

            print("\n")


            print(
                "Study session has not started."
            )


            print(
                "Your timetable remains unchanged."
            )


    else:

        print("\n")


        print(
            "No problem."
        )


        print(
            "Your study session remains scheduled."
        )


# ==========================================
# FINAL SYSTEM MESSAGE
# ==========================================

print("\n")
print("==========================================")
print("       PLANNING INFORMATION READY")
print("==========================================")


print(
    "The personalized timetable has "
    "been generated successfully."
)


print(
    "Today's scheduled study module has "
    "been identified automatically."
)


print(
    "The system does not ask the student "
    "to choose the module."
)


print(
    "The system can now collect scope, "
    "notes and optional past-paper questions."
)


print(
    "The next development stage will improve "
    "the AI generation and question matching."
)


print("\n")
print("==========================================")
print("              END OF PLAN")
print("==========================================")