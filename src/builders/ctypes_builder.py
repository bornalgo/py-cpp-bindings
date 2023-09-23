import ctypes
from pygccxml import declarations
from typing import Union, Optional, List, Tuple, Dict, Set
from src.tools.string_tools import *

from enum import Enum

declarations_type = Union[
    declarations.declaration_t,
    declarations.type_t,
    declarations.free_calldef_t,
    declarations.enumeration_t,
    declarations.class_t,
    declarations.variable_t,
    declarations.argument_t,
    declarations.operator_t,
    declarations.destructor_t
]


class Commented(Enum):
    # Enumeration to represent commenting options
    NoComment = 0
    Inline = 1
    Outline = 2
    Mixed = 3

    @staticmethod
    def inner(commented: "Commented"):
        # Helper method to determine inner comment style
        if commented == Commented.Mixed:
            return Commented.Inline
        else:
            return commented


class Definition(Enum):
    # Enumeration to represent definition options
    Undefined = 0
    Pre = 1
    Post = 2
    Mixed = 3
    Complete = 4


ctypes_module = __import__('ctypes')

cpp_to_ctypes_mapper = {
    # Mapping of C++ types to ctypes types
    'void*': 'c_void_p',
    'bool': 'c_bool',
    'char*': 'c_char_p',
    'std::string': 'c_char_p',
    'char': 'c_char',
    'wchar_t': 'c_wchar',
    'unsigned char': 'c_ubyte',
    'short': 'c_short',
    'unsigned short': 'c_ushort',
    'int': 'c_int',
    'unsigned int': 'c_uint',
    'long': 'c_long',
    'unsigned long': 'c_ulong',
    'long long': 'c_longlong',
    'unsigned long long': 'c_ulonglong',
    'float': 'c_float',
    'double': 'c_double',
    'long double': 'c_longdouble',
    'short int': 'c_short',
    'unsigned short int': 'c_ushort',
    'short unsigned int': 'c_ushort',
    'long int': 'c_long',
    'unsigned long int': 'c_ulong',
    'long unsigned int': 'c_ulong',
    'long long int': 'c_longlong',
    'unsigned long long int': 'c_ulonglong',
    'long long unsigned int': 'c_ulonglong',
    'long unsigned long int': 'c_ulonglong',
    'int8_t': 'c_int8',
    'uint8_t': 'c_uint8',
    'int16_t': 'c_int16',
    'uint16_t': 'c_uint16',
    'int32_t': 'c_int32',
    'uint32_t': 'c_uint32',
    'int64_t': 'c_int64',
    'uint64_t': 'c_uint64',
    'intptr_t': 'c_int',
    'uintptr_t': 'c_uint',
    'int_fast8_t': 'c_int',
    'int_fast16_t': 'c_int',
    'int_fast32_t': 'c_int',
    'int_fast64_t': 'c_int64',
    'uint_fast8_t': 'c_uint',
    'uint_fast16_t': 'c_uint',
    'uint_fast32_t': 'c_uint',
    'uint_fast64_t': 'c_uint64',
    'int_least8_t': 'c_int',
    'int_least16_t': 'c_int',
    'int_least32_t': 'c_int',
    'int_least64_t': 'c_int64',
    'uint_least8_t': 'c_uint',
    'uint_least16_t': 'c_uint',
    'uint_least32_t': 'c_uint',
    'uint_least64_t': 'c_uint64',
    'intmax_t': 'c_int64',
    'uintmax_t': 'c_uint64'
}


class CtypesBuilder:
    def __init__(self, decl: declarations_type, decl_string: str = None,
                 title: str = None, name: str = None, default_value: str = None,
                 is_reference: bool = False, is_type: bool = False,
                 is_function: bool = False, is_structure: bool = False, builders: Optional[dict] = None,
                 futures: Optional[set] = None, explicit: bool = False, parent: Optional["CtypesBuilder"] = None):
        """
        Initializes a CtypesBuilder instance.

        Args:
            decl: The declaration or type object.
            decl_string: A string representation of the declaration.
            title: The title of the builder.
            name: The name of the declaration.
            default_value: The default value for the declaration.
            is_reference: Indicates if the declaration is a reference.
            is_type: Indicates if the declaration represents a type.
            is_function: Indicates if the declaration is a function.
            is_structure: Indicates if the declaration is a structure.
            builders: A dictionary of builders.
            futures: A set of future declarations.
            explicit: Indicates if the declaration is explicit.
            parent: The parent CtypesBuilder instance.

        Attributes:
            # ... (other attributes)

        """
        self.parent = parent
        self.decl = decl
        self.decl_string = decl_string
        self.title = title
        self.ctype_base_string = None
        self.ctype_string = None
        self.ctype_object = None
        self.is_reference = is_reference
        self.pointer_count = 0
        self.array_pointer_count = 0
        self.explicit = explicit
        if self.decl is not None and hasattr(self.decl, 'name') and name is None:
            name = self.decl.name
        self.name = name
        self.default_value = default_value
        self.is_type = is_type
        self.is_function = is_function
        self.is_structure = is_structure
        self.is_enumeration = False
        self.is_constructor = False
        self.arguments = None
        self.argument_types = None
        self.return_type = None
        self.enumerations = None
        self.declarations = None
        if builders is None:
            builders = {}
        self.builders = builders
        if futures is None:
            futures = set()
        self.futures = futures
        self.dependency: Optional[CtypesBuilder] = None
        self.dependents: List[CtypesBuilder] = []
        self.declared = False

    def collect(self, inner_type: 'CtypesBuilder'):
        """
        Collects information from an inner CtypesBuilder instance and updates the current instance.

        Args:
            inner_type: The inner CtypesBuilder instance to collect information from.
        """
        self.ctype_base_string = inner_type.ctype_base_string
        self.ctype_string = inner_type.ctype_string
        self.ctype_object = inner_type.ctype_object
        self.is_reference = self.is_reference or inner_type.is_reference
        self.pointer_count += inner_type.pointer_count
        self.array_pointer_count += inner_type.array_pointer_count
        self.explicit = self.explicit or inner_type.explicit

    def wrap(self, outer_ctype_string: str, outer_ctype_object: ctypes, explicit: bool = False):
        """
        Wraps the current CtypesBuilder instance with an outer type.

        Args:
            outer_ctype_string: The outer ctypes type as a string.
            outer_ctype_object: The outer ctypes type as an object.
            explicit: Indicates whether the wrapping is explicit.

        Notes:
            If the outer type is a POINTER and a matching typedef exists, the type is updated accordingly.
        """
        if not explicit and outer_ctype_string == 'ctypes.POINTER' and \
                f'{remove_prefix(self.ctype_string, "ctypes.")}_p' in cpp_to_ctypes_mapper:
            self.ctype_string = f'{self.ctype_string}_p'
            self.ctype_object = getattr(ctypes_module, f'{remove_prefix(self.ctype_string, "ctypes.")}_p')
        else:
            self.ctype_string = f'{outer_ctype_string}({self.ctype_string})'
            self.ctype_object = outer_ctype_object(self.ctype_object)
        if outer_ctype_string == 'ctypes.POINTER':
            self.pointer_count += 1

    def pointer_wrap(self, explicit: bool = False):
        """
        Wraps the current CtypesBuilder instance with a POINTER type.

        Args:
            explicit: Indicates whether the wrapping is explicit.
        """
        self.wrap('ctypes.POINTER', ctypes.POINTER, explicit=explicit)

    @classmethod
    def populate(cls, decl: declarations_type, title: str = None, decl_origin: declarations_type = None,
                 builders: Optional[dict] = None, futures: Optional[set] = None, explicit: bool = False,
                 parent: Optional["CtypesBuilder"] = None):
        """
        Populate a CtypesBuilder instance based on a given declaration or type.

        Args:
            decl: The declaration or type to populate from.
            title: The title of the builder.
            decl_origin: The declaration origin.
            builders: A dictionary of builders.
            futures: A set of future declarations.
            explicit: Indicates whether the declaration is explicit.
            parent: The parent CtypesBuilder instance.

        Returns:
            CtypesBuilder: A populated CtypesBuilder instance.
        """
        if builders is None:
            builders = {}
        if futures is None:
            futures = set()

        # Handle builders by recursively populating from the inner declaration
        if isinstance(decl, declarations.typedef_t):
            innest_decl = get_innest_decl(decl)
            self = cls.populate(innest_decl, title=title, decl_origin=decl,
                                builders=builders, futures=futures, explicit=explicit, parent=parent)
            self.decl = decl
            self.is_type = True
            return self

        # Handle other declarations or types
        if decl_origin is not None and hasattr(decl_origin, 'decl_string'):
            decl_string = clean_type(decl_origin.decl_string)
        elif decl is not None and hasattr(decl, 'decl_string'):
            decl_string = clean_type(decl.decl_string)
        else:
            decl_string = None

        self = cls(decl, decl_string=decl_string, title=title, builders=builders, futures=futures,
                   explicit=explicit, parent=parent)

        if isinstance(decl, (declarations.free_function_type_t, declarations.member_function_type_t)):
            # Handle free function types
            self.ctype_string = 'ctypes.CFUNCTYPE'
            self.ctype_object = ctypes.CFUNCTYPE
            self.is_function = True
            self.return_type = CtypesBuilder.populate(decl.return_type, decl_origin=decl,
                                                      builders=builders, futures=futures, explicit=self.explicit,
                                                      parent=self)
            self.argument_types = [CtypesBuilder.populate(param, builders=builders, futures=futures,
                                                          explicit=self.explicit, parent=self)
                                   for param in decl.arguments_types]

        # Handle other declaration types (enumeration, class, constructor, free function, etc.)
        elif isinstance(decl, (declarations.enumeration_t, declarations.class_t, declarations.constructor_t,
                               declarations.free_function_t, declarations.member_function_t)):
            if isinstance(decl, declarations.enumeration_t):
                # Handle enumerations
                self.ctype_string = 'ctypes.c_int'
                self.ctype_object = ctypes.c_int
                self.enumerations = decl.values
                self.is_enumeration = True
            elif isinstance(decl, declarations.class_t):
                # Handle class declarations
                self.is_structure = True
                self.declarations = [CtypesBuilder.populate(decl, builders=builders, futures=futures,
                                                            explicit=self.explicit, parent=self)
                                     for decl in decl.declarations]
            elif isinstance(decl, (declarations.constructor_t, declarations.free_function_t,
                                   declarations.member_function_t)):
                # Handle constructors and free functions
                self.ctype_string = 'ctypes.CFUNCTYPE'
                self.ctype_object = ctypes.CFUNCTYPE
                self.is_function = True
                self.return_type = CtypesBuilder.populate(decl.return_type, decl_origin=decl, builders=builders,
                                                          futures=futures, explicit=self.explicit, parent=self)
                self.argument_types = [CtypesBuilder.populate(param, builders=builders, futures=futures,
                                                              explicit=self.explicit, parent=self)
                                       for param in decl.argument_types]
                self.arguments = [CtypesBuilder.populate(param, builders=builders, futures=futures,
                                                         explicit=self.explicit, parent=self)
                                  for param in decl.arguments]
        else:
            # Handle other declarations using custom conversion
            self = cpp_to_ctypes(decl, title=title, decl_origin=decl_origin, builders=builders,
                                 futures=futures, explicit=explicit, parent=parent)

        return self

    def copy(self, other):
        """
        Copy attributes from another CtypesBuilder instance.

        Args:
            other (CtypesBuilder): The other CtypesBuilder instance to copy attributes from.
        """
        for attr_name in vars(self):
            if not attr_name.startswith("__") and hasattr(other, attr_name):
                setattr(self, attr_name, getattr(other, attr_name))

    def get_ctype_string(self) -> str:
        """
        Get the ctypes string representation for the current CtypesBuilder instance.

        Returns:
            str: The ctypes string representation.
        """
        if self.ctype_string is not None:
            return self.ctype_string
        elif self.decl_string in self.builders and self.builders[self.decl_string].is_enumeration:
            return self.builders[self.decl_string].get_ctype_string()
        else:
            return self.get_decl_string()

    def get_ctype_string_with_pointer(self, count: int = 0):
        """
        Get the ctypes string representation with a specified number of pointers.

        Args:
            count (int): The number of pointers to add.

        Returns:
            str: The ctypes string representation with pointers.
        """
        return repeat_prefix(self.get_ctype_string(), 'ctypes.POINTER(', max(0, self.pointer_count + count))

    def get_decl_string(self) -> str:
        """
        Get the declaration string for the current CtypesBuilder instance.

        Returns:
            str: The declaration string.
        """
        if self.is_type:
            return self.decl_string
        elif self.title is not None:
            return self.title
        elif self.name is not None:
            return self.name
        else:
            return self.decl_string

    def to_string(self, commented: Commented = Commented.Mixed, postfix: str = '', prefix: str = '',
                  begin: str = None, end: str = None, definition: Definition = Definition.Undefined,
                  divider: str = '\n\n') -> str:
        """
        Generate a string representation of the CtypesBuilder object.

        Args:
            commented (Commented): The type of comment to add.
            postfix (str): The postfix for the generated code.
            prefix (str): The prefix for the generated code.
            begin (str): The custom beginning code.
            end (str): The custom ending code.
            definition (Definition): The definition type of the comment.
            divider (str): The divider between multiple generated strings.

        Returns:
            str: The string representation of the CtypesBuilder object.
        """
        self.declared = True
        if self.is_function:
            comment = self.get_comment(prefix='# Function type for ', postfix='\n', definition=definition,
                                       commented=commented)
            funcname = self.get_decl_string()
            if begin is None:
                begin = f'{funcname} = '
            else:
                definition = Definition.Complete
            if end is None:
                end = ''
            begin += self.get_ctype_string_with_pointer() + '('
            if commented != Commented.NoComment:
                sub_prefix = " " * len(begin)
                restype_postfix = ", " + postfix
                argtypes_postfix = "\n" + postfix
            else:
                sub_prefix = ""
                restype_postfix = argtypes_postfix = postfix
            restype = self.restype(prefix=sub_prefix, commented=Commented.inner(commented),
                                   postfix=restype_postfix, definition=definition)
            argtypes = self.argtypes(prefix=sub_prefix, commented=Commented.inner(commented),
                                     postfix=argtypes_postfix, definition=definition)
            if definition == Definition.Pre or (definition == Definition.Undefined and self.has_dependency()):
                if comment:
                    comment += ' (Pre-definition)'
                code = begin + 'None)'
            elif commented == Commented.NoComment:
                if definition == Definition.Post or definition == Definition.Mixed:
                    if comment:
                        comment += ' (Post-definition)'
                    if self.pointer_count > 0:
                        code = f'{funcname}.contents = {self.get_ctype_string_with_pointer(count=-1)}({restype}, ' \
                               f'{argtypes}' + (')' * self.pointer_count) + end
                    else:
                        code = f'{funcname}.restype = {restype}\n{funcname}.argtypes = [{argtypes}]'
                else:
                    code = begin + f'{restype}, ' \
                                   f'{argtypes}' + (')' * (1 + self.pointer_count)) + end
            else:
                if definition == Definition.Post or definition == Definition.Mixed:
                    if comment:
                        comment += ' (Post-definition)'
                    if self.pointer_count > 0:
                        begin_post = f'{funcname}.contents = {self.get_ctype_string_with_pointer(count=-1)}('
                        restype = indent(restype, len(begin_post) - len(begin))
                        argtypes = indent(argtypes, len(begin_post) - len(begin))
                        code = f'{funcname}.contents = {self.get_ctype_string_with_pointer(count=-1)}({restype}, ' \
                               f'{argtypes}' + (')' * self.pointer_count) + end
                    else:
                        begin_argtypes = f'{funcname}.argtypes = ['
                        argtypes = indent(argtypes, len(begin_argtypes) - len(begin))
                        if Commented.inner(commented) == Commented.Outline:
                            begin_restype = f'{funcname}.restype = ('
                            restype = indent(restype, len(begin_restype) - len(begin))
                            code = f'{begin_restype}\n{restype})' \
                                   f'{begin_argtypes}\n{argtypes}{" " * len(begin_argtypes)}]'
                        else:
                            begin_restype = f'{funcname}.restype = '
                            restype = indent(restype, len(begin_restype) - len(begin))
                            code = f'{begin_restype}{restype}' \
                                   f'{begin_argtypes}\n{argtypes}{" " * len(begin_argtypes)}]'
                else:
                    code = f'{begin}\n{restype}\n' \
                           f'{argtypes}{" " * len(begin)}' + (')' * (1 + self.pointer_count)) + end
            res = add_prefix_to_lines(f'{comment}{code}', prefix)
        elif self.is_enumeration:
            if begin is None:
                begin = ''
            if end is None:
                end = ''
            comment = self.get_comment(prefix='# Enum for ', commented=commented)
            enumerations = self.enums(prefix=' ' * 4, postfix='\n' + postfix, definition=definition)
            if definition == Definition.Pre or (definition == Definition.Undefined and self.has_dependency()):
                res = ''
            else:
                if commented == Commented.NoComment:
                    res = f'{begin}class {self.get_decl_string()}(IntEnum):\n{enumerations}{end}'
                elif commented == Commented.Inline:
                    res = add_prefix_to_lines(f'class {self.get_decl_string()}(IntEnum):    {comment}\n{enumerations}',
                                              prefix)
                else:
                    res = add_prefix_to_lines(f'{comment}\nclass {self.get_decl_string()}(IntEnum):\n{enumerations}',
                                              prefix)
        elif self.is_structure:
            if begin is None:
                begin = ''
            if end is None:
                end = ''
            comment = self.get_comment(prefix='# Structure for ', commented=commented)
            n = len('    _fields_ = [')
            decls = self.decls(prefix=' ' * n, postfix='\n' + postfix, commented=Commented.inner(commented),
                               definition=definition)

            if definition == Definition.Pre or (definition == Definition.Undefined and self.has_dependency()):
                if comment:
                    comment += ' (Pre-definition)'
                if commented == Commented.NoComment:
                    res = add_prefix_to_lines(
                        f'{begin}class {self.get_decl_string()}(ctypes.Structure):\n    pass{end}', prefix)
                elif commented == Commented.Inline:
                    res = add_prefix_to_lines(f'{begin}class {self.get_decl_string()}(ctypes.Structure):    {comment}\n'
                                              f'    pass{end}', prefix)
                else:
                    res = add_prefix_to_lines(f'{comment}\n{begin}class {self.get_decl_string()}(ctypes.Structure):\n'
                                              f'    pass{end}', prefix)
            else:
                code = f'{decls}{" " * n}'
                if definition == Definition.Post or definition == Definition.Mixed:
                    if comment:
                        comment += ' (Post-definition)'
                    begin_post = begin + self.get_decl_string() + '._fields_ = ['
                    decls = indent(decls, len(begin_post) - n)
                    code = f'{decls}{" " * len(begin_post)}'
                    if commented == Commented.NoComment:
                        res = add_prefix_to_lines(f'{begin_post}{code}]{end}', prefix)
                    else:
                        res = add_prefix_to_lines(f'{comment}\n{begin_post}{code}]{end}', prefix)
                else:
                    if commented == Commented.NoComment:
                        res = add_prefix_to_lines(
                            f'{begin}class {self.get_decl_string()}(ctypes.Structure):\n    _fields_ = ['
                            f'{code}]{end}', prefix)
                    elif commented == Commented.Inline:
                        res = add_prefix_to_lines(f'{begin}class {self.get_decl_string()}(ctypes.Structure):    '
                                                  f'{comment}\n    _fields_ = [{code}]{end}', prefix)
                    else:
                        res = add_prefix_to_lines(f'{comment}\n{begin}class {self.get_decl_string()}(ctypes.Structure):'
                                                  f'\n    _fields_ = [{code}]{end}', prefix)
        elif self.is_type:
            if begin is None:
                begin = f'{self.name} = '
            if begin is not None:
                prefix += begin
            if end is not None:
                postfix += end
            res = self.get_code_comment(comment_prefix='# Type for ', prefix=prefix, postfix=postfix,
                                        commented=commented)
            if definition == Definition.Pre or (definition == Definition.Undefined and self.has_dependency()):
                res = ''
        else:
            comment = self.get_comment(prefix='# Type for ', commented=commented)
            code, comment = self.get_code_update_comment(comment)
            if definition == Definition.Pre or (definition == Definition.Undefined and self.has_dependency()):
                res = ''
            else:
                if begin is not None:
                    prefix += begin
                if end is not None:
                    postfix += end
                if commented == Commented.NoComment:
                    res = f'{prefix}{code}{postfix}'
                elif commented == Commented.Inline:
                    res = f'{prefix}{code}{postfix}    {comment}'
                else:
                    res = add_prefix_to_lines(f'{comment}\n{code}{postfix}', prefix)
        dependents = [dependent for dependent in self.dependents
                      if dependent is not self.get_parent() or definition == Definition.Undefined]
        if dependents and self.parent is None:
            res += divider + divider.join([dependent.to_string(commented=commented, postfix=postfix, prefix=prefix,
                                                               end=end, definition=Definition.Post)
                                           for dependent in dependents])
        return res

    def get_innest_declaration_string(self) -> str:
        """
        Get the innermost declaration string from the current CtypesBuilder instance.

        Returns:
            str: The innermost declaration string.
        """
        type_str = get_innest_decl(self.decl).decl_string
        if type_str is None or not type_str:
            return ''
        type_str = re.sub(r'^::', '', type_str)
        if type_str == self.decl_string:
            return ''
        return type_str

    def get_code_update_comment(self, comment: str) -> Tuple[str, str]:
        """
        Get the code and a comment for code updates.

        Args:
            comment (str): The comment to include.

        Returns:
            Tuple[str, str]: The updated code and comment.
        """
        ctype_base_string: str = self.ctype_base_string
        if ctype_base_string is not None and ctype_base_string:
            typedef = self.builders.get(ctype_base_string)
        else:
            typedef = self.builders.get(self.get_ctype_string())
        if typedef is None or not typedef.is_enumeration or ctype_base_string in \
                [f'ctypes.{val}' for val in cpp_to_ctypes_mapper.values()]:
            code = self.get_ctype_string()
        else:
            code = self.get_ctype_string().replace(ctype_base_string, 'ctypes.c_int')
            comment = f'{comment} -> {self.get_ctype_string()}'
        if ctype_base_string in self.futures:
            if ctype_base_string in self.builders:
                self.set_dependency(self.builders[ctype_base_string])
            elif ctype_base_string in [self.get_parent().name, self.get_parent().decl_string]:
                self.set_dependency(self.get_parent())
                code = code.replace(ctype_base_string, self.get_parent().decl_string)
        return code, comment

    def get_parent(self) -> "CtypesBuilder":
        """
        Get the parent CtypesBuilder instance.

        Returns:
            CtypesBuilder: The parent CtypesBuilder instance.
        """
        if self.parent is not None:
            return self.parent.get_parent()
        else:
            return self

    def set_dependency(self, dependency: "CtypesBuilder"):
        """
        Set the dependency of the current CtypesBuilder instance.

        Args:
            dependency (CtypesBuilder): The dependency CtypesBuilder instance.
        """
        if self.parent is not None:
            self.parent.set_dependency(dependency)
            self.dependency = self.parent.dependency
        elif self.dependency is None:
            parent = self.get_parent()
            self.dependency = dependency
            self.dependency.dependents.append(parent)
        elif self.dependency is not dependency and self.dependency.typedef_index() < dependency.typedef_index():
            parent = self.get_parent()
            self.dependency.dependents.remove(parent)
            self.dependency = dependency
            self.dependency.dependents.append(parent)

    def get_dependency(self) -> Optional["CtypesBuilder"]:
        """
        Get the dependency CtypesBuilder instance.

        Returns:
            CtypesBuilder: The dependency CtypesBuilder instance.
        """
        if self.parent is not None:
            return self.parent.get_dependency()
        else:
            return self.dependency

    def has_dependency(self) -> bool:
        """
        Check if the current CtypesBuilder instance has an unresolved dependency.

        Returns:
            bool: True if there is an unresolved dependency, otherwise False.
        """
        if self.dependency is not None:
            return not self.dependency.declared or self.dependency is self
        else:
            return False

    def typedef_index(self) -> int:
        """
        Get the index of the current CtypesBuilder instance within the builders.

        Returns:
            int: The index of the CtypesBuilder instance within the builders, or -1 if not found.
        """
        for index, value in enumerate(self.builders.values()):
            if value is self:
                return index
        return -1

    def get_code_comment(self, comment_prefix: str = None, comment_postfix: str = None,
                         prefix: str = '', postfix: str = '', commented: Commented = Commented.Outline):
        """
        Get code with an optional comment for the current CtypesBuilder instance.

        Args:
            comment_prefix (str): The prefix for the comment.
            comment_postfix (str): The postfix for the comment.
            prefix (str): The prefix for the code.
            postfix (str): The postfix for the code.
            commented (Commented): The type of comment to add.

        Returns:
            str: The code with an optional comment.
        """
        comment = self.get_comment(prefix=comment_prefix, postfix=comment_postfix, commented=commented)
        code, comment = self.get_code_update_comment(comment)
        if commented == Commented.NoComment:
            return f'{prefix}{code}{postfix}'
        elif commented == Commented.Inline:
            return f'{prefix}{code}{postfix}    {comment}'
        else:
            return add_prefix_to_lines(f'{comment}\n{code}', prefix) + postfix

    def get_comment(self, prefix: str = None, postfix: str = None, definition: Definition = Definition.Undefined,
                    commented: Commented = Commented.Outline) -> str:
        """
        Get a comment for the current CtypesBuilder instance.

        Args:
            prefix (str): The prefix for the comment.
            postfix (str): The postfix for the comment.
            definition (Definition): The definition type of the comment.
            commented (Commented): The type of comment to add.

        Returns:
            str: The comment as a string.
        """
        if commented == Commented.NoComment:
            return ''
        if prefix is None:
            prefix = '# '
        if postfix is None:
            postfix = ''
        if definition == Definition.Pre and self.parent is None:
            postfix = ' (Pre-definition) ' + postfix
        elif definition == Definition.Post and self.parent is None:
            postfix = ' (Post-definition) ' + postfix
        comment_ext = self.get_innest_declaration_string()
        if comment_ext:
            return f'{prefix}{str(self.decl)}: {comment_ext}{"*" * self.pointer_count}' \
                   f'{"&" if self.is_reference else ""}{postfix}'
        else:
            return f'{prefix}{str(self.decl)}{postfix}'

    def restype(self, prefix: str = '', postfix: str = '', commented: Commented = Commented.Inline,
                definition: Definition = Definition.Undefined) -> Optional[str]:
        """
        Get the return type as a code comment.

        Args:
            prefix (str): The prefix for the comment.
            postfix (str): The postfix for the comment.
            commented (Commented): The type of comment to add.
            definition (Definition): The definition type of the comment.

        Returns:
            Optional[str]: The return type as a code comment.
        """
        if isinstance(self.return_type, CtypesBuilder):
            return self.return_type.get_code_comment(prefix=prefix, postfix=postfix, commented=commented)
        return None

    def argtypes(self, prefix: str = '', postfix: str = '', commented: Commented = Commented.Inline,
                 definition: Definition = Definition.Undefined) -> Optional[str]:
        """
        Get argument types as a code comment.

        Args:
            prefix (str): The prefix for the comment.
            postfix (str): The postfix for the comment.
            commented (Commented): The type of comment to add.
            definition (Definition): The definition type of the comment.

        Returns:
            Optional[str]: The argument types as a code comment.
        """
        if isinstance(self.argument_types, list):
            txt = ''
            for argument_type in self.argument_types:
                if isinstance(argument_type, CtypesBuilder):
                    txt += argument_type.get_code_comment(prefix=prefix, postfix=", ", commented=commented) + postfix
                else:
                    txt += f'{prefix}None{postfix}'
            return txt
        return None

    def args(self, prefix: str = '', postfix: str = '', commented: Commented = Commented.Inline,
             definition: Definition = Definition.Undefined) -> Optional[str]:
        if isinstance(self.argument_types, list):
            txt = ''
            for argument in self.arguments:
                if isinstance(argument, CtypesBuilder):
                    txt += argument.get_code_comment(prefix=prefix, postfix=", ", commented=commented) + postfix
                else:
                    txt += f'{prefix}None{postfix}'
            return txt
        return None

    def enums(self, prefix: str = '', postfix: str = '', commented: Commented = Commented.Inline,
              definition: Definition = Definition.Undefined) -> Optional[str]:
        """
        Get enumerations as a code comment.

        Args:
            prefix (str): The prefix for the comment.
            postfix (str): The postfix for the comment.
            commented (Commented): The type of comment to add.
            definition (Definition): The definition type of the comment.

        Returns:
            Optional[str]: The enumerations as a code comment.
        """
        if isinstance(self.enumerations, list):
            txt = ''
            for enumeration in self.enumerations:
                if isinstance(enumeration, tuple):
                    txt += f'{prefix}{enumeration[0]} = {enumeration[1]}{postfix}'
            return txt
        return None

    def decls(self, prefix: str = '', postfix: str = '', commented: Commented = Commented.Inline,
              definition: Definition = Definition.Undefined) -> Optional[str]:
        """
        Get declarations as a code comment.

        Args:
            prefix (str): The prefix for the comment.
            postfix (str): The postfix for the comment.
            commented (Commented): The type of comment to add.
            definition (Definition): The definition type of the comment.

        Returns:
            Optional[str]: The declarations as a code comment.
        """
        if isinstance(self.declarations, list):
            txt = f'{postfix}'
            for declaration in self.declarations:
                if isinstance(declaration, CtypesBuilder):
                    if not isinstance(declaration.decl, declarations.constructor_t) and \
                            declaration.get_ctype_string() is not None and isinstance(declaration.name, str) and \
                            declaration.name.isidentifier():
                        decl_string = declaration.to_string(commented=commented, prefix=prefix,
                                                            begin=f'("{declaration.name}", ', end='), ',
                                                            definition=definition)
                        if declaration.dependency is not None and definition == Definition.Undefined:
                            continue
                        txt += f'{decl_string}{postfix}'
            return txt
        return None


def get_innest_decl(decl: declarations_type) -> declarations_type:
    """
    Recursively retrieve the innermost declaration from a given declaration.

    Args:
        decl (declarations_type): The input declaration.

    Returns:
        declarations_type: The innermost declaration found.
    """
    if hasattr(decl, 'decl_type'):
        return get_innest_decl(decl.decl_type)
    elif hasattr(decl, 'base'):
        return get_innest_decl(decl.base)
    elif hasattr(decl, 'declaration'):
        return get_innest_decl(decl.declaration)
    else:
        return decl


def get_decl_string(decl: declarations_type) -> Optional[str]:
    """
    Get the declaration string from a given declaration.

    Args:
        decl (declarations_type): The input declaration.

    Returns:
        Optional[str]: The declaration string, or None if not available.
    """
    if decl is None:
        return None
    elif getattr(decl, 'decl_string'):
        return decl.decl_string
    else:
        return None


def cpp_to_ctypes(
    decl: Union[declarations.declaration_t, declarations.type_t],
    title: str = None,
    decl_origin: Union[declarations.declaration_t, declarations.type_t] = None,
    builders: Optional[dict] = None,
    futures: Optional[set] = None,
    explicit: bool = False,
    parent: Optional["CtypesBuilder"] = None
) -> "CtypesBuilder":
    """
    Convert a C++ declaration to a CtypesBuilder instance.

    Args:
        decl (Union[declarations.declaration_t, declarations.type_t]): The C++ declaration to convert.
        title (str): Optional title for the conversion.
        decl_origin (Union[declarations.declaration_t, declarations.type_t]): The original declaration.
        builders (Optional[dict]): A dictionary of builders.
        futures (Optional[set]): A set of future declarations.
        explicit (bool): Whether to generate explicit ctypes definitions.
        parent (Optional["CtypesBuilder"]): The parent CtypesBuilder instance, if applicable.

    Returns:
        CtypesBuilder: A CtypesBuilder instance representing the converted declaration.
    """
    if builders is None:
        builders = {}
    if futures is None:
        futures = set()
    if title is not None and title in builders:
        return builders[title]
    if decl_origin is None:
        decl_origin = decl
    type_name = None
    is_reference = False
    pointer_count = 0
    default_value = None
    is_pointer = False
    name = None
    if hasattr(decl, 'decl_type'):
        type_name = 'decl_type'
    elif hasattr(decl, 'return_type'):
        type_name = 'return_type'
    if type_name is not None:
        decl = getattr(decl, type_name)
    decl_string = clean_type(get_decl_string(decl))
    if isinstance(decl, declarations.reference_t):
        is_reference = True
        decl = decl.base
    while isinstance(decl, declarations.pointer_t):
        pointer_count += 1
        decl = decl.base
    if hasattr(decl_origin, 'name'):
        name = decl_origin.name
    if hasattr(decl_origin, 'default_value'):
        default_value = decl_origin.default_value
    decl_str = get_decl_string(decl)
    if isinstance(decl, declarations.typedef_t) or isinstance(decl, declarations.free_function_type_t) or \
            isinstance(decl, declarations.enumeration_t) or \
            isinstance(decl, declarations.class_t) or isinstance(decl, declarations.constructor_t) or \
            isinstance(decl, declarations.free_function_t):
        res = CtypesBuilder.populate(decl, title=title, decl_origin=decl_origin, builders=builders,
                                     futures=futures, explicit=explicit, parent=parent)
        res.is_reference = is_reference
        if name is not None:
            res.name = name
        if default_value is not None:
            res.default_value = default_value
        res.pointer_count = pointer_count
    else:
        innest_decl = get_innest_decl(decl)
        is_type = True if isinstance(innest_decl, declarations.typedef_t) else False
        is_function = True if (isinstance(innest_decl, declarations.free_function_t) or
                               isinstance(innest_decl, declarations.free_function_type_t)) else False
        is_structure = True if isinstance(innest_decl, declarations.class_t) else False
        if pointer_count > 0:
            pointer_count -= 1
            is_pointer = True
        decl_str_cleaned = clean_type(decl_str)
        if isinstance(decl, declarations.array_t):
            decl_str_cleaned = clean_type(decl.base.decl_string)
            size = decl.size
        else:
            size = 0
        if has_whitespace(decl_str_cleaned) and re.sub(r'&\*', '', decl_str_cleaned) not in cpp_to_ctypes_mapper:
            decl_str_cleaned = clean_type(decl_string)
        res = cpp_str_to_ctypes(decl_str_cleaned, title, is_cleaned=True, explicit=explicit, name=name,
                                default_value=default_value, is_pointer=is_pointer, is_type=is_type,
                                is_function=is_function, is_structure=is_structure,
                                size=size, is_reference=is_reference,
                                decl=decl_origin, builders=builders, futures=futures, parent=parent)

        for i in range(pointer_count):
            res.pointer_wrap(explicit=explicit)
    res.decl_string = decl_string

    return res


def cpp_str_to_ctypes(
        decl_str: str,
        title: str = None,
        name: str = None,
        default_value: str = None,
        is_cleaned: bool = False,
        is_pointer: bool = False,
        is_reference: bool = False,
        is_type: bool = False,
        is_function: bool = True,
        is_structure: bool = False,
        size: int = 0,
        decl: Union[declarations.declaration_t, declarations.type_t] = None,
        builders: Optional[Dict[str, CtypesBuilder]] = None,
        futures: Optional[Set[str]] = None,
        explicit: bool = False,
        parent: Optional["CtypesBuilder"] = None
) -> CtypesBuilder:
    """
    Convert a C++ declaration string to a CtypesBuilder instance.

    Args:
        decl_str (str): The C++ declaration string to convert.
        title (str): Optional title for the conversion.
        name (str): The name associated with the declaration.
        default_value (str): The default value associated with the declaration.
        is_cleaned (bool): Whether the input string is already cleaned.
        is_pointer (bool): Whether the declaration represents a pointer.
        is_reference (bool): Whether the declaration represents a reference.
        is_type (bool): Whether the declaration represents a typedef.
        is_function (bool): Whether the declaration represents a function.
        is_structure (bool): Whether the declaration represents a structure.
        size (int): The size of the declaration (for arrays).
        decl (Union[declarations.declaration_t, declarations.type_t]): The original declaration.
        builders (Optional[Dict[str, CtypesBuilder]]): A dictionary of builders.
        futures (Optional[Set[str]]): A set of future declarations.
        explicit (bool): Whether to generate explicit ctypes definitions.
        parent (Optional["CtypesBuilder"]): The parent CtypesBuilder instance, if applicable.

    Returns:
        CtypesBuilder: A CtypesBuilder instance representing the converted declaration.
    """
    if builders is None:
        builders = {}
    if futures is None:
        futures = set()
    if title is not None and title in builders:
        return builders[title]

    # Clean the declaration string if necessary
    decl_str_cleaned = decl_str
    if not is_cleaned:
        decl_str_cleaned = clean_type(decl_str)
    if decl_str_cleaned is not None and decl_str_cleaned:
        # Attempt to map the C++ type to a ctypes type
        ctypes_type = cpp_to_ctypes_mapper.get(decl_str_cleaned, '')
    else:
        ctypes_type = None

    # Create a new CtypesBuilder instance
    res = CtypesBuilder(decl, decl_str_cleaned, title, explicit=explicit, name=name,
                        default_value=default_value, is_reference=is_reference, builders=builders,
                        futures=futures, parent=parent)

    if ctypes_type is None:
        res.ctype_base_string = 'None'
        res.ctype_string = 'None'
        res.ctype_object = None
        return res
    elif ctypes_type:
        res.ctype_base_string = f'ctypes.{ctypes_type}'
        if is_pointer:
            if not explicit and hasattr(ctypes_module, ctypes_type + '_p') and size == 0:
                res.ctype_string = f'ctypes.{ctypes_type}_p'
                res.ctype_object = getattr(ctypes_module, ctypes_type + '_p')
            elif size > 0:
                res.ctype_string = f'ctypes.POINTER(ctypes.{ctypes_type} * {size})'
                res.ctype_object = ctypes.POINTER(getattr(ctypes_module, ctypes_type) * size)
            else:
                res.ctype_string = f'ctypes.POINTER(ctypes.{ctypes_type})'
                res.ctype_object = ctypes.POINTER(getattr(ctypes_module, ctypes_type))
            res.pointer_count = 1
        else:
            if size > 0:
                res.ctype_string = f'ctypes.{ctypes_type} * {size}'
                res.ctype_object = getattr(ctypes_module, ctypes_type) * size
            else:
                res.ctype_string = f'ctypes.{ctypes_type}'
                res.ctype_object = getattr(ctypes_module, ctypes_type)
            if decl_str_cleaned == 'void*':
                res.pointer_count = 1
    elif decl_str_cleaned == 'void':
        res.ctype_base_string = 'None'
        if is_pointer:
            if size > 0:
                res.ctype_string = 'ctypes.c_void_p * {size}'
                res.ctype_object = ctypes.c_void_p * size
                res.array_pointer_count = 1
            else:
                res.ctype_string = 'ctypes.c_void_p'
                res.ctype_object = ctypes.c_void_p
                res.pointer_count = 1
        else:
            res.ctype_string = 'None'
            res.ctype_object = None
    elif decl_str_cleaned in builders:
        res.ctype_base_string = decl_str_cleaned
        if is_pointer:
            if size > 0:
                res.ctype_string = f'ctypes.POINTER({decl_str_cleaned}) * {size}'
                if builders[decl_str_cleaned].ctype_object is None:
                    res.ctype_object = ctypes.c_void_p * size
                else:
                    res.ctype_object = ctypes.POINTER(builders[decl_str_cleaned].ctype_object) * size
            else:
                res.ctype_string = f'ctypes.POINTER({decl_str_cleaned})'
                if builders[decl_str_cleaned].ctype_object is None and is_pointer:
                    res.ctype_object = ctypes.c_void_p
                else:
                    res.ctype_object = ctypes.POINTER(builders[decl_str_cleaned].ctype_object)
        else:
            if size > 0:
                res.ctype_string = f'{decl_str_cleaned} * {size}'
                if builders[decl_str_cleaned].ctype_object is None:
                    res.ctype_object = None
                else:
                    res.ctype_object = builders[decl_str_cleaned].ctype_object * size
            else:
                res.ctype_string = decl_str_cleaned
                res.ctype_object = builders[decl_str_cleaned].ctype_object
    else:
        pointer_count = 1 if is_pointer else 0
        if decl_str_cleaned.endswith('&'):
            decl_str_cleaned = decl_str_cleaned[:-1]
            res.is_reference = True
        while decl_str_cleaned.endswith('*'):
            decl_str_cleaned = decl_str_cleaned[:-1]
            pointer_count += 1
        res.ctype_base_string = decl_str_cleaned
        if pointer_count == 0:
            if is_structure or is_function:
                futures.add(decl_str_cleaned)
                if size > 0:
                    res.ctype_string = f'{decl_str_cleaned} * {size}'
                else:
                    res.ctype_string = decl_str_cleaned
        elif is_pointer and pointer_count == 1:
            if size > 0:
                if is_structure:
                    futures.add(decl_str_cleaned)
                    res.ctype_string = f'ctypes.POINTER({decl_str_cleaned}) * {size}'
                    res.ctype_object = ctypes.c_void_p * size
                else:
                    res.ctype_string = f'ctypes.c_void_p * {size}'
                    res.ctype_object = ctypes.c_void_p * size
                res.array_pointer_count = 1
            else:
                if is_structure:
                    futures.add(decl_str_cleaned)
                    res.ctype_string = f'ctypes.POINTER({decl_str_cleaned})'
                    res.ctype_object = ctypes.c_void_p
                else:
                    res.ctype_string = 'ctypes.c_void_p'
                    res.ctype_object = ctypes.c_void_p
                res.pointer_count = 1
        else:
            if (not explicit or decl_str_cleaned not in cpp_to_ctypes_mapper) and pointer_count > 0:
                pointer_count -= 1
                is_pointer = True
            else:
                is_pointer = False
            res.collect(cpp_str_to_ctypes(decl_str_cleaned, is_cleaned=True, explicit=explicit, is_pointer=is_pointer,
                                          name=name, default_value=default_value, is_reference=is_reference,
                                          is_type=is_type, is_function=is_function, is_structure=is_structure,
                                          builders=builders, futures=futures, parent=parent))
            for i in range(pointer_count):
                res.pointer_wrap(explicit=explicit)
            if size > 0:
                res.array_pointer_count = pointer_count
                res.pointer_count = 0
                res.ctype_string = f'{res.ctype_string} * size'
                if res.ctype_object is not None:
                    res.ctype_object = res.ctype_object * size
    return res

