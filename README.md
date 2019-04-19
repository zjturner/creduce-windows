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
* [Simple Interestingness Test](#interestingness)  

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

**Important**: Make sure you are set up to track the `llvm-svn-compatible` branch
or else you may fail building CReduce using a newer version of Clang.

2. Make a build directory (we'll use this later): `(src) $ mkdir creduce-build`


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

1. Clone LLVM: `(src) $ git clone https://github.com/llvm/llvm-project.git`.
2. Make a build directory: `(src) $ mkdir llvm-build && cd llvm-build`
3. Configure the build:
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

<a name="interestingness-byo"/>

### Bring Your Own Interestingness Test

<a name="interestingness"/>

### Simple Interestingness Test
