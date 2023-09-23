import ctypes
from enum import IntEnum

# Function type for int subtract(int x, int y) [free function]
subtract = ctypes.CFUNCTYPE(
                            ctypes.c_int,     # int subtract(int x, int y) [free function]: int (*)( int,int )
                            ctypes.c_int,     # int
                            ctypes.c_int,     # int
                            )

# Function type for float divide(float a, float b) [free function]
divide = ctypes.CFUNCTYPE(
                          ctypes.c_float,     # float divide(float a, float b) [free function]: float (*)( float,float )
                          ctypes.c_float,     # float
                          ctypes.c_float,     # float
                          )

# Enum for Fruit [enumeration]
class Fruit(IntEnum):
    APPLE = 0
    BANANA = 1
    ORANGE = 2


# Structure for Animal [class]
class Animal(ctypes.Structure):
    _fields_ = [
                # Function type for void Animal::printInfo() [member function]
                ("printInfo", ctypes.CFUNCTYPE(
                                               None,     # void Animal::printInfo() [member function]: void ( ::Animal::* )(  )
                                               )), 
                ("name", ctypes.c_char_p),     # Type for Animal::name [variable]: std::basic_string<char>
                ("age", ctypes.c_int),     # Type for Animal::age [variable]
                ]
