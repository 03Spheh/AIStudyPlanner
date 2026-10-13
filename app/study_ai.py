import re


def clean_text(text):
    """
    Cleans extracted PDF text so it is easier to analyse.
    """

    if not text:
        return ""

    # Remove page markers
    text = re.sub(r"--- Page \d+ ---", " ", text)

    # Replace multiple spaces/newlines
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_into_sentences(text):
    """
    Splits text into simple sentences.
    """

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 20
    ]


def generate_summary(text, number_of_sentences=5):
    """
    Generates a simple extractive summary.

    The system selects meaningful sentences from the
    uploaded study material.
    """

    cleaned = clean_text(text)

    if not cleaned:
        return "There is not enough readable content to create a summary."

    sentences = split_into_sentences(cleaned)

    if not sentences:
        return cleaned[:1000]

    # Common academic words that indicate important content
    important_words = [
        "definition",
        "theorem",
        "principle",
        "example",
        "important",
        "therefore",
        "because",
        "means",
        "called",
        "defined",
        "formula",
        "method",
        "property",
        "concept",
        "result",
        "solution"
    ]

    scored_sentences = []

    for index, sentence in enumerate(sentences):

        score = 0

        lower_sentence = sentence.lower()

        # Give points when academic keywords appear
        for word in important_words:
            if word in lower_sentence:
                score += 2

        # Slight preference for earlier sentences
        if index < 10:
            score += 1

        # Avoid extremely long sentences
        if len(sentence) < 300:
            score += 1

        scored_sentences.append((score, index, sentence))

    # Select highest scoring sentences
    scored_sentences.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = scored_sentences[:number_of_sentences]

    # Put them back in their original order
    selected.sort(key=lambda item: item[1])

    summary = []

    for _, _, sentence in selected:
        summary.append(sentence)

    return " ".join(summary)


def extract_key_topics(text, number_of_topics=8):
    """
    Finds possible important academic topics from the text.
    """

    cleaned = clean_text(text)

    if not cleaned:
        return []

    sentences = split_into_sentences(cleaned)

    word_frequency = {}

    # Words that normally don't represent useful topics
    stop_words = {
        "the", "and", "that", "this", "with",
        "from", "are", "was", "were", "for",
        "have", "has", "been", "into", "their",
        "there", "which", "will", "would", "can",
        "could", "should", "than", "then", "they",
        "them", "these", "those", "about", "also",
        "where", "when", "what", "such", "using",
        "used", "each", "more", "some", "only",
        "not", "but", "you", "your", "our",
        "its", "his", "her", "how", "who",
        "all", "any", "one", "two", "may"
    }

    for sentence in sentences:

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z-]{3,}\b",
            sentence.lower()
        )

        for word in words:

            if word not in stop_words:

                word_frequency[word] = (
                    word_frequency.get(word, 0) + 1
                )

    # Sort by frequency
    sorted_words = sorted(
        word_frequency.items(),
        key=lambda item: item[1],
        reverse=True
    )

    topics = []

    for word, frequency in sorted_words:

        if frequency >= 2:

            topic = word.capitalize()

            if topic not in topics:
                topics.append(topic)

        if len(topics) >= number_of_topics:
            break

    return topics


def generate_questions(text, number_of_questions=5):
    """
    Generates simple practice questions from important
    sentences in the uploaded study material.
    """

    cleaned = clean_text(text)

    if not cleaned:
        return []

    sentences = split_into_sentences(cleaned)

    questions = []

    question_starters = [
        "Explain",
        "Define",
        "Describe",
        "What is",
        "Why is"
    ]

    important_words = [
        "definition",
        "theorem",
        "principle",
        "concept",
        "method",
        "property",
        "formula",
        "example",
        "sequence",
        "limit",
        "function",
        "convergence"
    ]

    for sentence in sentences:

        lower_sentence = sentence.lower()

        found_keyword = None

        for word in important_words:

            if word in lower_sentence:
                found_keyword = word
                break

        if found_keyword:

            # Create a question from the sentence
            question = (
                f"Explain the concept of "
                f"{found_keyword} discussed in the study material."
            )

            if question not in questions:
                questions.append(question)

        if len(questions) >= number_of_questions:
            break

    # If not enough questions were found,
    # create general study questions.
    if len(questions) < number_of_questions:

        general_questions = [
            "What are the main concepts discussed in this material?",
            "Explain one important concept from the study material.",
            "What definitions should a student remember?",
            "Which examples are used to explain the concepts?",
            "What important results or properties are presented?"
        ]

        for question in general_questions:

            if question not in questions:
                questions.append(question)

            if len(questions) >= number_of_questions:
                break

    return questions[:number_of_questions]