# Autobentifier Tool

This is the home of the bento-autobentifier, a tool for automatically partitioning existing binaries into bento-boxes while minimizing the overhead of box switching.

**!! Note: This project is an expirement with no promise of support. Use at your own risk. !!**

## What are Bento-boxes?

Bento-boxes are independently-linked, memory-isolated pieces of code that are designed to work together. You can think of them as a light-weight alternative to processes for microcontrollers.

For more information on this idea, see the [bento-linker](https://github.com/arm-software/bento-linker).

This tool is an experiment in taking an existing binary, and generating those code boundaries automatically. Effectively allowing you to augment an existing program with Bento-box's memory isolation runtimes without additional programmer intervention.

## Python Requirements
`pip install -r requirements.txt`

Separately install Networkx-METIS: https://github.com/networkx/networkx-metis/
If you are building on MacOS there is a workaround to install via conda. `conda install -c conda-forge networkx-metis`

## Retdec Build and Installation

This section describes a local build and installation of RetDec. Instructions for Docker are given in the next section.

### Requirements

#### Linux

* A C++ compiler and standard C++ library supporting C++17 (e.g. GCC >= 7)
* [CMake](https://cmake.org/) (version >= 3.6)
* [Git](https://git-scm.com/)
* [Perl](https://www.perl.org/)
* [Python](https://www.python.org/) (version >= 3.4)
* [autotools](https://en.wikipedia.org/wiki/GNU_Build_System) ([autoconf](https://www.gnu.org/software/autoconf/autoconf.html), [automake](https://www.gnu.org/software/automake/), and [libtool](https://www.gnu.org/software/libtool/))
* [pkg-config](https://www.freedesktop.org/wiki/Software/pkg-config/)
* [m4](https://www.gnu.org/software/m4/m4.html)
* [zlib](http://zlib.net/)
* Optional: [Doxygen](http://www.stack.nl/~dimitri/doxygen/) and [Graphviz](http://www.graphviz.org/) for generating API documentation

On Debian-based distributions (e.g. Ubuntu), the required packages can be installed with `apt-get`:

```sh
sudo apt-get install build-essential cmake git perl python3 autoconf automake libtool pkg-config m4 zlib1g-dev upx doxygen graphviz
```

On RPM-based distributions (e.g. Fedora), the required packages can be installed with `dnf`:

```sh
sudo dnf install gcc gcc-c++ cmake make git perl python3 autoconf automake libtool pkg-config m4 zlib-devel upx doxygen graphviz
```

On Arch Linux, the required packages can be installed with `pacman`:

```sh
sudo pacman --needed -S base-devel cmake git perl python3 autoconf automake libtool pkg-config m4 zlib upx doxygen graphviz
```

#### Windows

* Microsoft Visual C++ (version >= Visual Studio 2017 version 15.7)
* [CMake](https://cmake.org/) (version >= 3.6)
* [Git](https://git-scm.com/)
* [Active Perl](https://www.activestate.com/activeperl). It needs to be the first Perl in `PATH`, or it has to be provided to CMake using `CMAKE_PROGRAM_PATH` variable, e.g. `-DCMAKE_PROGRAM_PATH=/c/perl/bin`. Does NOT work with Strawberry Perl or MSYS2 Perl (you would have to install a pre-built version of OpenSSL, see below).
* [Python](https://www.python.org/) (version >= 3.4)
* Optional: [Doxygen](http://ftp.stack.nl/pub/users/dimitri/doxygen-1.8.13-setup.exe) and [Graphviz](https://graphviz.gitlab.io/_pages/Download/windows/graphviz-2.38.msi) for generating API documentation

#### macOS

Packages should be preferably installed via [Homebrew](https://brew.sh).

* macOS >= 10.14
* Full Xcode installation ([including command-line tools](https://github.com/frida/frida/issues/338#issuecomment-426777849), see [#425](https://github.com/avast/retdec/issues/425) and [#433](https://github.com/avast/retdec/issues/433))
* [CMake](https://cmake.org/) (version >= 3.6)
* [Git](https://git-scm.com/)
* [Perl](https://www.perl.org/)
* [Python](https://www.python.org/) (version >= 3.4)
* [autotools](https://en.wikipedia.org/wiki/GNU_Build_System) ([autoconf](https://www.gnu.org/software/autoconf/autoconf.html), [automake](https://www.gnu.org/software/automake/), and [libtool](https://www.gnu.org/software/libtool/))
* Optional: [Doxygen](http://www.stack.nl/~dimitri/doxygen/) and [Graphviz](http://www.graphviz.org/) for generating API documentation

### Process
We opt to install retdec locally and pass this to PYTHONPATH later

* Clone the repository as a submodule:
  * `git submodule init`
  * `git submodule update`
* Linux:
  * `mkdir build && cd build`
  * `cmake ../external/retdec -DCMAKE_INSTALL_PREFIX=../bin`
  * `make -jN` (`N` is the number of processes to use for parallel build, typically number of cores + 1 gives fastest compilation time)
  * `make install`
* Windows:
  * Open a command prompt (e.g. `cmd.exe`)
  * `mkdir build && cd build`
  * `cmake ../external/retdec -DCMAKE_INSTALL_PREFIX=../bin -G<generator>`
  * `cmake --build . --config Release -- -m`
  * `cmake --build . --config Release --target install`
  * Alternatively, you can open `retdec.sln` generated by `cmake` in Visual Studio IDE
* macOS:
  * `mkdir build && cd build`
  * `cmake ../external/retdec -DCMAKE_INSTALL_PREFIX=../bin`
  * `make -jN` (`N` is the number of processes to use for parallel build, typically number of cores + 1 gives fastest compilation time)
  * `make install`
