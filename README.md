This is intended as a guide to get CReduce up and running on Windows.

##### Table of Contents  
[Introduction](#intro)  
[Setting up the Build Environment](#setup)
* [Get CReduce](#get-creduce)  
* [Get a Perl Distribution](#get-perl)  
* [Get Other Required Tools](#get-other-tools)  
* [Build unifdef.exe](#unifdef)  
* [Build Clang](#build-clang)

[Build CReduce](#build)  
[Copy unifdef.exe](#copy-unifdef)

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

<a name="setup"/>

## Setting up the Build Environment

For the remainder of the document, we will assume that your source tree is
rooted at a folder named `src`.  All shell commands with no explicit
instructions assume that are you are in `src`.

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


<a name="get-perl"/>

### Get a Perl Distribution

Download any Perl distribution you feel comfortable with.  [ActiveState](https://www.activestate.com/products/activeperl/downloads/)
and [Strawberry Perl](http://strawberryperl.com/) are popular choices.

**Important:** The rest of the document assumes Perl is in your `PATH` environment
variable.  If you decide not to do this, it is up to you to recognize where and how
to modify the remaining steps in the document.

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

<a name="get-other-tools"/>

### Get Other Required Tools

Flex is a fast lexer generator used by CReduce.  Ninja is a build tool used (among
other things) to build CMake-configured projects.  CMake and Git are, well... CMake
and Git.  Download them all from their respective homepages:

* [Flex](http://gnuwin32.sourceforge.net/packages/flex.htm)  
* [Ninja](https://ninja-build.org/)
* [CMake](https://cmake.org/download/)
* [Git](https://gitforwindows.org/)

All of these packages provide binary distributions.  You do not need to build anything from
source.  In all cases it should be safe to download whatever the latest version is.

**Important:** The rest of the document assumes that all of these tools are in your `PATH`
environment variable.  If you decide not to do this, it is up to you to recognize where and
how to modify the remaining steps in the document.


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
```

**Important**: CMake requires absolute paths.  Replace `src` with the absolute path
of the directory.  Also, CMake requires forward slashes.  Do not use backslashes
anywhere.

2. Build and install creduce.  `(src/creduce-build) $ ninja && ninja install`

**Note:** You will get thousands of warnings, but you should not get any errors.
Ignore the warnings.

<a name="copy-unifdef"/>

## Copy unifdef.exe

unifdef needs to be manually copied into the place where creduce expects it to be.  

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

Here, `path/to/creduce` must be the path where CReduce *is installed* (e.g. when you ran `ninja install`), and not the build output directory.  Additionally, `foo.cpp` must be an absolute path.  `test.bat` is then free to invoke a python script (which must also be an absolute path), and that python script must also be hardcoded to build the same absolute path that was specified in the initial `creduce` invocation.  If that sounds like a lot of absolute paths, it is!  

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

# IMPORTANT: Path to source file is absolute
args = ['cl.exe', '/W3', '/WX', 'C:/warning/foo.cpp']

obj = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
(stdout, stderr) = obj.communicate()

if "warning treated as error" in stdout:
    sys.exit(0)

sys.exit(1)
```

Then we need to write our batch file wrapper which calls python with this script:
```
REM C:\reduce\test.bat
REM IMPORTANT: path to python script is absolute.
python C:\reduce\test.py
```

And finally, we can invoke creduce:

```
$ ECHO Important: path to batch file and source file below are absolute.
$ perl C:\src\creduce-build\creduce\creduce C:\reduce\test.bat C:\warning\foo.cpp
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
and re-run creduce, this time run `reduce.py` instead of running creduce directly.

```
$ python reduce.py --source=foo.cpp --creduce=C:\src\creduce-build\creduce\creduce --stdout="warning treated as error" --cflags="/c /O2 /W3 /WX"
```

And we get the exact same result!  We didn't have to create any batch files, or python files, and we didn't have to worry about relative / absolute paths.  

Note that BYO interestingness tests are obviously more powerful.  They allow you to compile multiple files, have interesting tests based on the generated code or object file, link stuff together, and pretty much whatever you want.  But for the majority of cases, the simple interestingness test should suffice and greatly simplify things.

<a href="nontoy"/>

## A Non-Toy Example

Here we give an example of how CReduce can be used to find real problems by showing a non-trivial program that illustrates a compiler bug, and then using creduce to figure out exactly what that compiler bug is.

TODO: Fill this out.
