# py-cpp-bindings
## _This is a Python utility for generating seamless bindings to C++ libraries, enabling you to effortlessly interface Python with existing C++ codebases._

![Example3_h](res/imgs/example3_h.svg)
![Example3_py](res/imgs/example3_py.svg)

"py-cpp-bindings" is a handy Python utility for generating seamless bindings to C++ libraries, enabling you to effortlessly interface Python with existing C++ codebases. This versatile tool streamlines the process of creating Pythonic wrappers around C++ classes, functions, and enums, making it easier than ever to harness the capabilities of C++ libraries from within Python.

## Features

- **Automated Binding Generation:** Quickly generate Python bindings for C++ code with minimal effort.
- **Versatile Compatibility:** Works with a wide range of C++ libraries and projects.
- **Effortless Integration:** Seamlessly incorporate C++ functionality into Python applications.
- **Advanced Type Handling:** Handle complex C++ types, including pointer types and circular type definitions.
- **Flexible Configuration:** Fine-tune the binding generation process to meet your specific needs.
- **Intuitive Usage:** Enjoy a user-friendly interface for creating Pythonic wrappers.
- **Documentation and Examples:** Documentation and illustrative examples to guide you through the process.

Unlock the full potential of your C++ libraries in Python with "py-cpp-bindings." Start bridging the gap between these two powerful programming languages today!

## Prerequisites

- **Python Packages:** You must have the following Python packages installed:

  - [pygccxml](https://pygccxml.readthedocs.io/en/latest/)
  - [pyinstaller](https://www.pyinstaller.org/)

- **XML Generator:** An XML generator tool is required to extract information from your C++ codebase. In this project, we have used the following XML generator tools:

  - [castxml](https://github.com/CastXML/CastXML)
  - [castxml-patch](https://pypi.org/project/castxml-patch/)

## Build

### Windows

Execute the following command
```bat
.\buildWindows.bat
```

### Linux

Execute the following command
```sh
./buildLinux.sh
```

## Usage

### Linux
```sh
build/LINUX-x86_64/dist/py-cpp-bindings/py-cpp-bindings --filenames examples/example1.h --output example/example1.py
```

### Windows

Note that you need to change the `--include-paths` based on your OS file system.

```bat
build\Win64\dist\py-cpp-bindings\py-cpp-bindings.exe --filenames examples\example1.h --include-paths "C:\Program Files (x86)\Windows Kits\10\Include\10.0.19041.0\ucrt" "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\include" --output examples\example1.py
```

