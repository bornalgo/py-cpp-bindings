import os
import argparse
from pygccxml import utils, declarations, parser
from collections import OrderedDict
from typing import List
import warnings
from src.builders.ctypes_builder import CtypesBuilder
from src.tools.string_tools import *


def main(filenames: List[str], output: str,
         generator_path: str = None, generator_name: str = None, include_paths: List[str] = None,
         source_files: List[str] = None):
    """
    Parse C++ header files, extract declarations, and generate Python ctypes code.

    Args:
        filenames (List[str]): List of C++ header file paths to parse.
        output (str): Output Python file path for generated ctypes code.
        generator_path (str, optional): Path to the XML generator executable. Defaults to None.
        generator_name (str, optional): Name of the XML generator. Defaults to None.
        include_paths (List[str], optional): List of additional include paths for parsing. Defaults to None.
        source_files (List[str], optional): List of source file paths to consider during parsing. Defaults to None.

    Raises:
        Exception: Raised when no valid files are provided or all provided files do not exist.
        UserWarning: Raised when some provided files do not exist.

    Returns:
        None
    """
    # Find out the C++ parser
    generator_path_utils, generator_name_utils = utils.find_xml_generator()

    # Set generator_path and generator_name if not provided
    if generator_path is None:
        generator_path = generator_path_utils
    if generator_name is None:
        generator_name = generator_name_utils

    # Configure the XML generator
    xml_generator_config = parser.xml_generator_configuration_t(
        xml_generator_path=generator_path,
        xml_generator=generator_name,
        include_paths=include_paths if include_paths else [])

    filepaths = []
    invalid_filenames = []

    if not filenames:
        raise Exception('No files are provided')

    # Validate and store valid file paths
    for filename in filenames:
        if os.path.exists(filename):
            filepaths.append(os.path.abspath(filename))
        else:
            invalid_filenames.append(filename)

    if not filepaths:
        n = len(filenames)
        if n > 1:
            raise Exception('None of the provided files (%s) exist' % join_iterable(filenames))
        else:
            raise Exception('The provided file (%s) does not exist' % filenames[0])
    elif invalid_filenames:
        n = len(invalid_filenames)
        warnings.warn('The following file%s (%s) do%s not exist and have been disregarded' % ('s' if n > 1 else '',
                                                                                              join_iterable(
                                                                                                  invalid_filenames),
                                                                                              '' if n > 1 else 'es'))


    # Parse C++ declarations from the provided files
    decls = parser.parse(filepaths, xml_generator_config)

    builders = OrderedDict()
    futures = set()

    if source_files is None:
        source_files = set(filepaths)
    else:
        source_files = set(map(lambda x: os.path.abspath(x), source_files)).union(set(filepaths))
    header_words = set()

    # Extract words from source files for future reference
    for source_file in source_files:
        header_words = header_words.union(get_words(source_file))

    # Extract and process C++ declarations
    for decl in decls[0].declarations:
        if decl.name in header_words:
            if isinstance(decl, (declarations.typedef_t, declarations.free_function_type_t,
                                 declarations.enumeration_t, declarations.class_t, declarations.constructor_t,
                                 declarations.free_function_t)):
                builders[decl.name] = CtypesBuilder.populate(decl, title=decl.name, builders=builders, futures=futures)

    # Write Python ctypes code to the output file
    with open(output, 'w') as f:
        f.write('import ctypes\n%s' % ('from enum import IntEnum\n'
                if any([builder.is_enumeration for builder in builders.values()]) else ''))

        for builder in builders.values():
            f.write('\n')
            f.write(builder.to_string())
            f.write('\n')


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Parse C++ header files and generate Python ctypes code.",
                                     add_help=True)

    # Define command-line arguments corresponding to main() parameters with hyphens
    argparser.add_argument("-f", "--filenames", nargs="+", required=True, help="List of C++ header file paths to parse")
    argparser.add_argument("-o", "--output", required=True, help="Output Python file path for generated ctypes code")
    argparser.add_argument("-p", "--generator-path", help="Path to the XML generator executable")
    argparser.add_argument("-n", "--generator-name", help="Name of the XML generator")
    argparser.add_argument("-i", "--include-paths", nargs="+", help="List of additional include paths for parsing")
    argparser.add_argument("-s", "--source-files", nargs="+",
                           help="List of source file paths to consider during parsing")

    args = argparser.parse_args()

    # Call the main function with arguments from the command line
    main(args.filenames, args.output, args.generator_path, args.generator_name, args.include_paths, args.source_files)
