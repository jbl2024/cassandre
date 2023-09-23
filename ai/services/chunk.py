import re


def split_markdown(markdown_text):
    """
    Splits a given Markdown text into paragraphs with titles.

    Parameters:
    - markdown_text (str): The Markdown text to be split.

    Returns:
    - paragraphs_with_titles (List[str]): A list of paragraphs with their corresponding titles.
    """
    # Split content into lines
    lines = markdown_text.splitlines()

    # Initial empty titles stack and current paragraph buffer
    titles = []
    current_paragraph = []
    paragraphs_with_titles = []

    for line in lines:
        # Remove leading and trailing spaces
        stripped_line = line.strip()

        # Match title/header
        title_match = re.match(r"^(#+)\s+(.+)", stripped_line)
        if title_match:
            depth = len(title_match.group(1))
            title = title_match.group(2)

            # If there's content in current_paragraph, save it before processing this header
            if current_paragraph:
                full_title = " > ".join(titles)
                paragraph_content = "\n".join(current_paragraph).strip()
                if paragraph_content:  # Make sure it's not just whitespace
                    paragraphs_with_titles.append(
                        "{}\n{}".format(full_title, paragraph_content)
                    )
                current_paragraph = []

            # Update the titles
            titles = titles[: depth - 1]
            titles.append(title)

        else:
            # Add to current paragraph, even if it's a whitespace line
            current_paragraph.append(line.strip())

    # Handle any remaining paragraph after processing all lines
    if current_paragraph:
        full_title = " > ".join(titles)
        paragraph_content = "\n".join(current_paragraph).strip()
        if paragraph_content:  # Make sure it's not just whitespace
            paragraphs_with_titles.append(f"{full_title}\n{paragraph_content}")

    return paragraphs_with_titles
