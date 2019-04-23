This is intended as a guide to get CReduce up and running on Windows.

##### Table of Contents  
[Introduction](#intro)  
[A Word on PATH and Shells](#path)  
[Preliminaries](#prelim)  
[Get a Perl Distribution](#get-perl)  
[Build Clang](#build-clang)
[Build unifdef.exe](#unifdef)  
[Get CReduce](#get-creduce)  
[Build CReduce](#build)  

[Using CReduce](#using)
* [Bring Your Own Interestingness Test](#interestingness-byo)  
* [Interestingness Test Made Easy](#interestingness)  

[A Non-Toy Example](#nontoy)

<a name="intro"/>

## Introduction
We assume that you know what CReduce is and what it does.  More information
about CReduce can be found at the [project's home page](https://embed.cs.utah.edu/creduce/).

CReduce is quite difficult to get working on Windows.  The process is not
well documented and there are many gotchas along the way.  And if you stray
from the path, things will go wrong.  This guide is intended to be a complete
verifiably reproducible sequence of steps that will allow you to get CReduce
working on your Windows machine.

<a name="path"/>

## A Word on PATH and Shells

We assume that all commands (unless explicitly stated otherwise) are run from a cmd shell.  **NOT** a git bash shell or any other kind of shell.  Please do not use git bash unless the instructions explicitly call for it.

For each tool that we build or all, instructions will be given about whether it needs to be in your PATH.  If the instructions indicate that it should be in PATH and you do not put it in PATH, you will be on your own to adjust the instructions as necessary.

<a name="prelim"/>

## Install Required Tools

Before starting, you should have the following software installed:

* [Flex](http://gnuwin32.sourceforge.net/packages/flex.htm)  
* [Ninja](https://ninja-build.org/)
* [CMake](https://cmake.org/download/)
* [Git](https://gitforwindows.org/)

Flex is a fast lexer generator used by CReduce.  Ninja is a build tool used (among
other things) to build CMake-configured projects.  CMake and Git are, well... CMake
and Git.  Download them all from the links above.

All of these packages provide binary distributions.  You do not need to build anything from
source.  In all cases it should be safe to download whatever the latest version is.

**Important:** All of these tools should be in your `PATH` environment variable.

For the remainder of the document, we will assume that your source tree is
rooted at a folder named `src`.  All shell commands with no explicit
instructions assume that are you are in `src`.


<a name="get-perl"/>

### Get a Perl Distribution

Download any Perl distribution you feel comfortable with.  [ActiveState](https://www.activestate.com/products/activeperl/downloads/)
and [Strawberry Perl](http://strawberryperl.com/) are popular choices.

**Important:** perl should be in your `PATH` environment variable.

Install the following Perl modules:

* Exporter::Lite  
* File::Which
* Getopt::Tabular
* Regexp::Common
* Term::ReadKey

```
$ cpan -i "Exporter::Lite"
// Note: The previous command will probably inform you that you need to download
// MinGW and dmake.  Accept and let it proceed.  You will only be prompted for this
// on the first package you install.
$ cpan -i "File::Which"
$ cpan -i "Getopt::Tabular"
$ cpan -i "Regexp::Common"
$ cpan -i "Term::ReadKey"
```


<a name="build-clang"/>

### Build Clang

CReduce claims to be able to work with a version of clang/LLVM installed from a
binary distribution package.  However, i was not able to make this work due to
the fact that the binary distribution does not ship with the .cmake configuration
files, and CReduce seems to require them.  So we will be building from source.

**Important**: Make sure you are in a MSVC C++ Developer Command Prompt for
these steps.  You can open one by searching for "x86 Native Tools Command
Prompt for VS 2017" or similar.  Note that when you try to run cmake, it might
find gcc on your path due to an earlier step, and then try to build clang using
gcc instead of MSVC.  You don't want this.  If this happens, delete `gcc.exe` and
`g++.exe` from `C:\Perl64\site\bin`.  If you ever try to install another package
that needs them, it will always just re-download them same as it did in the
earlier step.

**Important**: As of this writing, LLVM miscompiles with VS 2019.  Please make
sure you are using 2015 or 2017.

1. Clone LLVM: `(src) $ git clone https://github.com/llvm/llvm-project.git`.
2. Make a build directory: `(src) $ mkdir llvm-build && cd llvm-build`
3. Configure the build.
```
  (src/llvm-build) $ 
    cmake -G Ninja
      -DCMAKE_BUILD_TYPE=Release
      -DLLVM_TARGETS_TO_BUILD=X86
      -DLLVM_ENABLE_PROJECTS=clang;lld
      ..\llvm-project\llvm
```
4. Run the build and wait: `(src/llvm-build) $ ninja`

Note that, contrary to other steps, clang **does not** need to be in your `PATH`.


<a name="unifdef"/>

### Build unifdef.exe

unifdef is an optional utility that can be used by CReduce to eliminate blocks of preprocessor
logic.  If you have it, CReduce can use it.  If not, it will work anyway (but probably be
slowe and the reduction might not be as good).   Note that if you only ever reduce
pre-processed source (e.g. `cl.exe /EP foo.cpp`) then you don't need this.  Nevertheless,
we don't want to stray from the path, because that's where things start going wrong.

1. Clone the repo: `(src) $ git clone git://dotat.at/unifdef.git`
2. Open a git bash shell (Git Bash is a tool that ships with [Git for Windows](https://gitforwindows.org/))
   and cd to the directory where you cloned unifdef in step 1.
3. Run this command: `(src/unifdef) $ sh scripts/reversion.sh`.  You should see some output like this:
```
   version
     -> unifdef-2.11.25.65842ab.XX 2019-04-19 12:27:33 -0700
```
4. Open `src/unifdef/win32/unifdef.sln` in a recent version of Visual Studio.  I tested 2015
   but 2017 should work equally well.  Build the Release configuration.
   
Note: unifdef does not need to be in `PATH`.  Later we will copy it into CReduces build tree
which will allow creduce to find it.

<a name="get-creduce"/>

### Get CReduce

1. Clone creduce from its [github repo](https://github.com/csmith-project/creduce).

```(src) $ git clone https://github.com/csmith-project/creduce.git```

2. Make sure you are set up to track the `llvm-svn-compatible` branch or else you
may fail building CReduce using a newer version of Clang.

```
(src) $ cd creduce
(src/creduce) $ git checkout -b creduce origin/llvm-svn-compatible
Switched to a new branch 'creduce'
Branch 'creduce' set up to track remote branch 'llvm-svn-compatible' from 'origin'.
```

3. Make a build directory (we'll use this later):

```
(src/creduce) $ cd ..
(src) $ mkdir creduce-build
```

<a name="build"/>

## Build CReduce

Finally!  We're ready to actually build CReduce.

1. Switch to your CReduce build directory created earlier and run CMake to
   configure it.
```
  (src/creduce-build) $ 
    cmake -G Ninja 
      -DCMAKE_BUILD_TYPE=Release 
      -DLLVM_DIR=src/llvm-build
      -DCMAKE_C_COMPILER=src/llvm-build/bin/clang-cl.exe
      -DCMAKE_CXX_COMPILER=src/llvm-build/bin/clang-cl.exe
      -DCMAKE_PREFIX_PATH=src/llvm-build
      ..\creduce
```

**Important**: CMake requires absolute paths.  Replace `src` with the absolute path
of the directory.  Also, CMake requires forward slashes.  Do not use backslashes
anywhere.

2. Build creduce.  `(src/creduce-build) $ ninja`

3. Install creduce (Note: You must be in an administrator command prompt): `(src/creduce-build) $ ninja install`

**Note:** You will get thousands of warnings, but you should not get any errors.
Ignore the warnings.

4. unifdef needs to be manually copied into the place where creduce expects it to be.  

```
(src/creduce-build) $ mkdir unifdef && cd unifdef
(src/creduce-build/unifdef) $ copy src/unifdef/win32/Release/unifdef.exe
```

<a name="using"/>

## Using CReduce

It's finally time to use CReduce!  Let's look at how to actually use it.

Normally, creduce expects you to write your own interestingness test.  This is a self-contained script which has all information about how to invoke the compiler as well as what makes the result interesting directly into the script.  Then creduce will invoke your script once for each source file it wants to check the interestingness of.  There are two big reasons this can often be a bit of a burden.  

The first reason (which is not Windows specific) is that in a large majority of cases, an interestingness test boils down to "run the compiler with these flags, and the invocation was interesting if X was in the output, otherwise it's not interesting".  It's painstaking to have to write a new script every single time that copies a lot of the boilerplate, hardcodes paths, etc.  It would be nice if we could automate this.

This is compounded by the second reason (which is Windows specific).  The "script" that creduce expects is something that can be run the same way an executable can be run.  On Unixy systems this is fine, because you can write a shell script.  On Windows though this means you need to use a batch file, and I can assure you that nobody wants to do anything non-trivial in a batch file.  It's nice to be able to write our scripts in something like Python.  So on Windows, we additionally need a "wrapper" batch file that just calls a Python script, but then this script has to be hardcoded as well, so now we need 2 scripts filled with boilerplate every time we want a new interestingness test.

First we'll look at how to write an interestingness test the "standard" way, which will motivate the next topic, which provides an easy way to write interestingness tests for the most common use cases.


<a name="interestingness-byo"/>

### Bring Your Own Interestingness Test

You invoke creduce with `$ perl path/to/creduce test.bat foo.cpp`.

During the reduction process, creduce will make many temporary directories, copy the current version of the source into it, and
run your script against it.  For this reason, it's important that `foo.cpp` be relative and assumed to be located in the current
directory.  This way, whenever creduce runs your interestingness test, it will pick up the version of the source file in the current temporary directory.

Let's make this concrete by looking at an example of a toy program with something we want to reduce, and the scripts and creduce invocation needed to make this happen.

```c
C:\warning\foo.cpp
int main(int argc, char **argv) {
  return 1.0;  // This should warn about double to int conversion.
}
```

First, we write `test.py` which will invoke the compiler, check for this warning, and return 0 if the warning is present, and 1 if the warning is not present.

```python
# C:\reduce\test.py
import os
import subprocess
import sys

# IMPORTANT: Path to source file is in current working directory
args = ['cl.exe', '/W3', '/WX', 'foo.cpp']

obj = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
(stdout, stderr) = obj.communicate()

if "warning treated as error" in stdout:
    sys.exit(0)

sys.exit(1)
```

Then we need to write our batch file wrapper which calls python with this script:
```
REM C:\reduce\test.bat
python C:\reduce\test.py
```

And finally, we can invoke creduce:

```
$ perl C:\src\creduce-build\creduce\creduce test.bat foo.cpp
```

If we run this, we should see creduce printing a bunch of output like this:
```
===< pass_comments :: 0 >===
===< pass_includes :: 0 >===
===< pass_line_markers :: 0 >===
===< pass_blank :: 0 >===
(2.6 %, 373 bytes)
===< pass_clang_binsrch :: replace-function-def-with-decl >===
===< pass_clang_binsrch :: remove-unused-function >===
===< pass_lines :: 0 >===
(5.2 %, 363 bytes)
===< pass_lines :: 1 >===
```

and if we wait long enough, it will return.  So what did it do?  Let's look at the
original file now.

```
$ cat foo.cpp
int main(int argc, char **argv) ;
```

And we can see that our program is smaller.

<a name="interestingness"/>

### Simple Interestingness Test

That was a lot of work though.  We had to write 2 files, hardcode a bunch of paths,
and mess around with python subprocess module which you probably have to check the
documentation for every time you use it.  Let's see how we can make this easier.

Let's try this again.  First put the original (pre-reduced file) back where it was.

```
$ copy foo.cpp.orig foo.cpp
```

Then download [reduce.py](https://github.com/zjturner/creduce-windows/blob/master/reduce.py)
and this time run `reduce.py` instead of running creduce directly.

```
$ python reduce.py --source=foo.cpp --creduce=C:\src\creduce-build\creduce\creduce --stdout="warning treated as error" --cflags="/c /O2 /W3 /WX"
```

And we get the exact same result!  We didn't have to create any batch files, or python files, and we didn't have to worry about relative / absolute paths.  

Note that BYO interestingness tests are obviously more powerful.  They allow you to compile multiple files, have interesting tests based on the generated code or object file, link stuff together, and pretty much whatever you want.  But for the majority of cases, the simple interestingness test should suffice and greatly simplify things.

<a href="nontoy"/>

## A Non-Toy Example

Here we give an example of how CReduce can be used to find real problems by showing a non-trivial program that illustrates a compiler bug, and then using creduce to figure out how to make that compiler bug smaller.

To start with, I needed to find an ICE.  I searched the Microsoft Developer Community website and decided to use [this one](https://developercommunity.visualstudio.com/content/problem/538662/internal-compiler-error-27.html) which has something do with a `std::vector`.  The repro is here:

```c
// ice.cpp
#include <vector>
#include <cstdint>

int what();

enum class bingus_t : uint8_t {
  bungus,
  bingus,
  lumpus
};

int what() {

  struct a_struct_t {
	  bool is_small {true};
	  uint32_t delta_time {0};
	  bingus_t type {bingus_t::bungus};
	  uint32_t size {0};
	  uint32_t data_size {0};
  };
  struct another_struct_t {
	  std::vector<unsigned char> bytes {};
	  a_struct_t ans {};
  };

  std::vector<another_struct_t> tests {
	  {{0x00,0xFF,0x58,0x04,0x04,0x02,0x18,0x08},
      {true,0x00,bingus_t::lumpus,8,7}},
  };

  return 0;
}
```

But it's not immediately obvious what the problem is.  Let's see how creduce can help.

First, preprocess the file so that creduce has a single self-contained source file to work with:

```
$ cl /c /P /EP /Fiice.pp.cpp ice.cpp
```

Next, let's make sure the ICE actually happens on the pre-processed file.

```
$ cl /c ice.pp.cpp
C:\creduction>cl /Z7 /c ice.pp.cpp
Microsoft (R) C/C++ Optimizing Compiler Version 19.20.27508.1 for x64
Copyright (C) Microsoft Corporation.  All rights reserved.

ice.pp.cpp
C:\creduction\ice.pp.cpp(26) : fatal error C1001: An internal error has occurred in the compiler.
(compiler file 'd:\agent\_work\1\s\src\vctools\Compiler\Utc\src\p2\main.c', line 160)
 To work around this problem, try simplifying or changing the program near the locations listed above.
Please choose the Technical Support command on the Visual C++
 Help menu, or open the Technical Support help file for more information
  cl!InvokeCompilerPassW()+0x84fd5

C:\creduction\ice.pp.cpp(26) : fatal error C1001: An internal error has occurred in the compiler.
(compiler file 'd:\agent\_work\1\s\src\vctools\Compiler\Utc\src\Common\error.c', line 835)
 To work around this problem, try simplifying or changing the program near the locations listed above.
Please choose the Technical Support command on the Visual C++
 Help menu, or open the Technical Support help file for more information
```

Now, let's try to reduce this to the smallest possible ICE.

```
$  python reduce.py --source=ice.pp.cpp --cores=12 --creduce=C:\src\creduce-build\creduce\creduce --stdout="compiler file 'd:\agent\_work\1\s\src\vctools\Compiler\Utc\src\p2\main.c', line 160" --stderr="compiler file 'd:\agent\_work\1\s\src\vctools\Compiler\Utc\src\p2\main.c', line 160" --cflags="/c"
```

Note that the text we're checking for includes the exact faulting line in the compiler, to make sure that the source file is only interesting if it produces the *same* ICE.

After all is said and done, we get this:

```c
namespace std {
template <class a> class initializer_list {
public:
  initializer_list();
  initializer_list(a *, a *);
};
class b {
  int c;

public:
  template <class j> b(j);
};
template <class d> class e {
public:
  e(initializer_list<d>) : f(int()) {}
  ~e();
  b f;
};
struct g {};
struct h {
  e<char> bytes;
  g ans{};
};
e<h> i{{}};
} // namespace std
```

While creduce is pretty good, if you play around with this by hand, you can get it a little smaller:

```c
namespace std {
template <class a> struct initializer_list {
  initializer_list();
  initializer_list(a *, a *);
};
}

template <class d> struct e {
  e(std::initializer_list<d>);
  ~e();
  int f;
};
struct g {};
struct h {
  e<char> bytes;
  g ans{};
};
e<h> i{{}};
```

But at least now it's more apparent what the bug is, and also makes for a better repro case.
