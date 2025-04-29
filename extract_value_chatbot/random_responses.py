import random

# A set of 5 varied Persian templates for loan-response summaries.
TEMPLATES_SUMMARY = [
    # Template 1
    (
        "بسیار خب، طبق اطلاعات شما:\n"
        "{summary}"
    ),
    # Template 2
    (
        "مروری بر مقادیر دریافتی شما:\n"
        "{summary}"
    ),
    # Template 3
    (
        "خوب، این مقادیر برای شما استخراج شدند:\n"
        "{summary}"
    ),
    # Template 4
    (
        "طبق درخواست شما، این نتایج به دست آمد:\n"
        "{summary}"
    ),
    # Template 5
    (
        "این هم خلاصه‌ای از مقادیر مدنظر شما:\n"
        "{summary}"
    ),
]


def random_response_summary(summary: str) -> str:
    """
    Selects and returns one random phrasing for the given summary.
    """
    template = random.choice(TEMPLATES_SUMMARY)
    return template.format(summary=summary)
