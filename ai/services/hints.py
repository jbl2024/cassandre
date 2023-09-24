from collections import defaultdict


def parse_hints(hints):
    """
    Parse the hints field.

    Args:
        hints (str): The hints field content.

    Returns:
        dict: A dictionary mapping page numbers to their corresponding hints.
    """
    page_mappings = defaultdict(list)  # Use a defaultdict for storing multiple hints

    if not hints:
        return page_mappings

    hints_list = hints.replace('\n', ';').split(";")

    for hint in hints_list:
        hint = hint.strip()

        if ":" not in hint:
            continue

        if "toutes pages" in hint:
            _, hint_text = hint.split(":")
            page_mappings["all"].append(hint_text.strip())
        elif "pages" in hint:
            page_range, hint_text = hint.split(":")
            start, end = [int(x) for x in page_range.replace("pages", "").split("à")]
            for page in range(start, end + 1):
                page_mappings[page].append(hint_text.strip())
        else:  # For the format "page x : hint"
            page_range, hint_text = hint.split(":")
            page = int(page_range.replace("page", "").strip())
            page_mappings[page].append(hint_text.strip())

    return page_mappings
