from typing import Optional, List, Set, Iterable
import re


def repeat_prefix(input_string: str, prefix: str, count: int) -> Optional[str]:
    """
    Repeat a prefix string a specified number of times and append it to the input string.

    Args:
        input_string (str): The input string to which the prefix will be repeated and appended.
        prefix (str): The prefix string to be repeated.
        count (int): The number of times the prefix should be repeated.

    Returns:
        Optional[str]: The modified string with the repeated prefix, or None if the input string is None.
    """
    if input_string is None:
        return input_string
    else:
        output_string = input_string
        for i in range(count):
            output_string = prefix + output_string
        return output_string


def remove_prefix(input_string: str, prefix: str) -> Optional[str]:
    """
    Remove a prefix string from the beginning of the input string.

    Args:
        input_string (str): The input string from which the prefix will be removed.
        prefix (str): The prefix string to be removed.

    Returns:
        Optional[str]: The modified string with the prefix removed, or None if the input string is None.
    """
    if input_string is None:
        return input_string
    if input_string.startswith(prefix):
        return input_string[len(prefix):]
    else:
        return input_string


def remove_suffix(input_string: str, suffix: str) -> Optional[str]:
    """
    Remove a suffix string from the end of the input string.

    Args:
        input_string (str): The input string from which the suffix will be removed.
        suffix (str): The suffix string to be removed.

    Returns:
        Optional[str]: The modified string with the suffix removed, or None if the input string is None.
    """
    if input_string is None:
        return input_string
    if input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    else:
        return input_string


def add_prefix_to_lines(input_string: str, prefix: str) -> Optional[str]:
    """
    Add a prefix to each line of the input string, preserving indentation.

    Args:
        input_string (str): The input string containing multiple lines.
        prefix (str): The prefix string to be added to each line.

    Returns:
        Optional[str]: The modified string with the prefix added to each line, or None if the input string is None.
    """
    if input_string is None:
        return input_string
    lines = []
    i = 0
    skip_first = False
    for line in input_string.split('\n'):
        if line.strip().startswith('#') and i == 0:
            lines.append(extract_leading_whitespace(prefix) + line)
            skip_first = True
        elif i == 0 or (i == 1 and skip_first):
            lines.append(prefix + line)
        else:
            space = extract_leading_whitespace(prefix)
            lines.append(space + ' ' * (len(prefix) - len(space)) + line)
        i += 1
    return '\n'.join(lines)


def remove_prefix_from_lines(input_string: str, prefix: str) -> Optional[str]:
    """
    Remove a common prefix from the beginning of each line in the input string.

    Args:
        input_string (str): The input string containing multiple lines.
        prefix (str): The prefix string to be removed from each line.

    Returns:
        Optional[str]: The modified string with the prefix removed from each line, or None if the input string is None.
    """
    if input_string is None:
        return input_string
    lines = []
    for line in input_string.split('\n'):
        lines.append(remove_prefix(line, prefix))
    return '\n'.join(lines)


def indent(input_string: str, num: int) -> Optional[str]:
    """
    Indent each line of the input string by a specified number of spaces or remove indentation if num is negative.

    Args:
        input_string (str): The input string containing multiple lines.
        num (int): The number of spaces to indent each line. If negative, remove indentation.

    Returns:
        Optional[str]: The modified string with lines indented by the specified number of spaces or None if input is
         None.
    """
    if input_string is None or num == 0:
        return input_string
    lines = []
    for line in input_string.split('\n'):
        if line:
            if num > 0:
                lines.append((' ' * num) + line)
            else:
                lines.append(line[-num:])
        else:
            lines.append(line)
    return '\n'.join(lines)


def extract_leading_whitespace(input_string: str) -> Optional[str]:
    """
    Extract leading whitespace characters from the input string.

    Args:
        input_string (str): The input string from which to extract leading whitespace.

    Returns:
        Optional[str]: The extracted leading whitespace characters, or None if the input string is None.
    """
    if input_string is None:
        return None
    return input_string[:len(input_string) - len(input_string.lstrip())]


def has_whitespace(input_string: str) -> bool:
    """
    Check if the input string contains any whitespace characters.

    Args:
        input_string (str): The input string to check for whitespace.

    Returns:
        bool: True if the input string contains whitespace, False otherwise.
    """
    if input_string is None:
        return False
    return any(char.isspace() for char in input_string)


def clean_type(type_str: Optional[str]) -> Optional[str]:
    """
    Clean and normalize a C++ type string by removing unnecessary spaces, const keywords, and redundant symbols.

    Args:
        type_str (Optional[str]): The C++ type string to be cleaned.

    Returns:
        Optional[str]: The cleaned C++ type string, or None if the input is None or empty.
    """
    if type_str is None or not type_str:
        return type_str

    # Remove '::' from the beginning of the type string
    cleaned_type = re.sub(r'^::', '', type_str)

    # Remove const keyword if it's a standalone word
    cleaned_type = re.sub(r'\bconst\b\s*', '', cleaned_type)

    # Remove any spaces around '*' and '&'
    cleaned_type = re.sub(r'\s+([*&]\s*)', r'\1', cleaned_type)

    # Remove any repeated '&' characters
    cleaned_type = re.sub(r'&{2,}', ' ', cleaned_type)

    # Remove any leading and trailing white spaces
    cleaned_type = cleaned_type.strip()

    return cleaned_type


def clean_word(word: str) -> List[str]:
    """
    Cleans a word by splitting it at punctuation characters and removing empty strings.

    Args:
        word (str): The word to be cleaned.

    Returns:
        list: A list of cleaned word segments.
    """
    # Split the word at punctuation characters and keep them as separate elements
    cleaned_word = re.split(r'([^\w_])', word)
    # Remove any empty strings from the list
    cleaned_word = [c for c in cleaned_word if c]
    return cleaned_word


def get_words(file_path: str) -> Set[str]:
    """
    Extracts unique words from a text file, considering valid identifiers.

    Args:
        file_path (str): The path to the text file.

    Returns:
        set: A set containing unique words found in the file.
    """
    unique_words = set()
    with open(file_path, 'r') as file:
        for line in file:
            words = line.split()
            for word in words:
                cleaned_word = clean_word(word)
                for each_word in cleaned_word:
                    if each_word and each_word.isidentifier():
                        unique_words.add(each_word)
    return unique_words


def join_iterable(iterable: Iterable, separator: str = ', ', end_separator: str = ' and ') -> str:
    # Convert the iterable elements to strings
    iterable = map(str, iterable)

    # Convert the iterable to a list
    iterable = list(iterable)

    # If the iterable is empty, return an empty string
    if not iterable:
        return ''

    # If there's only one element, return it as a string
    if len(iterable) == 1:
        return iterable[0]

    # Initialize the result string
    result = ''

    # Iterate through the elements in the iterable
    for i, item in enumerate(iterable):
        if i == 0:
            # For the first item, just add it to the result
            result += item
        elif i == len(iterable) - 1:
            # For the last item, add the end_separator before appending it to the result
            result += end_separator + item
        else:
            # For all other items, add the separator before appending them to the result
            result += separator + item

    return result