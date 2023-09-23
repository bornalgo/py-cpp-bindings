import ctypes
from enum import IntEnum

# Enum for Color [enumeration]
class Color(IntEnum):
    RED = 0
    GREEN = 1
    BLUE = 2


# Function type for int add(int a, int b) [free function]
add = ctypes.CFUNCTYPE(
                       ctypes.c_int,     # int add(int a, int b) [free function]: int (*)( int,int )
                       ctypes.c_int,     # int
                       ctypes.c_int,     # int
                       )

# Function type for double multiply(double x, double y) [free function]
multiply = ctypes.CFUNCTYPE(
                            ctypes.c_double,     # double multiply(double x, double y) [free function]: double (*)( double,double )
                            ctypes.c_double,     # double
                            ctypes.c_double,     # double
                            )

# Function type for std::string greet(std::string const & name) [free function]: std::string (*)( ::std::string const & )
greet = ctypes.CFUNCTYPE(
                         ctypes.c_char_p,     # std::string greet(std::string const & name) [free function]: std::string (*)( ::std::string const & )
                         ctypes.c_char_p,     # std::string const &: std::basic_string<char>&
                         )

# Structure for Rectangle [class]
class Rectangle(ctypes.Structure):
    _fields_ = [
                # Function type for double Rectangle::area() const [member function]: double ( ::Rectangle::* )(  )const
                ("area", ctypes.CFUNCTYPE(
                                          ctypes.c_double,     # double Rectangle::area() const [member function]: double ( ::Rectangle::* )(  )const
                                          )), 
                # Function type for double Rectangle::perimeter() const [member function]: double ( ::Rectangle::* )(  )const
                ("perimeter", ctypes.CFUNCTYPE(
                                               ctypes.c_double,     # double Rectangle::perimeter() const [member function]: double ( ::Rectangle::* )(  )const
                                               )), 
                ("width_", ctypes.c_double),     # Type for Rectangle::width_ [variable]
                ("height_", ctypes.c_double),     # Type for Rectangle::height_ [variable]
                ]
