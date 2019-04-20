import argparse
import os
import shlex
import subprocess
import sys
import tempfile

def _which(command):
    """which(command) - Look up the given command in PATH environment variable"""

    paths = os.environ.get('PATH', '')

    # Check for absolute match first.
    if os.path.isabs(command) and os.path.isfile(command):
        return os.path.normcase(os.path.normpath(command))

    # Would be nice if Python had a lib function for this.
    if not paths:
        paths = os.defpath

    base, extension = os.path.splitext(command)

    # If the filename already has an extension, don't bother with PATHEXT
    if extension:
        command = base
        pathext = [extension]
    else:
        # Get suffixes to search.
        # On Cygwin, 'PATHEXT' may exist but it should not be used.
        if os.pathsep == ';':
            pathext = os.environ.get('PATHEXT', '').split(';') + ['']
        else:
            pathext = ['']

    # Search the paths...
    for path in paths.split(os.pathsep):
        for ext in pathext:
            p = os.path.join(path, command + ext)
            if os.path.exists(p) and not os.path.isdir(p):
                return os.path.normcase(os.path.normpath(p))

    return None

parser = argparse.ArgumentParser(description='Reduce a file.')
parser.add_argument('--script', help='An interestingness test written in python')
parser.add_argument('--source', help='source file being reduced')
parser.add_argument('--stdout', help='Mark test run as interesting if stdout contains this text')
parser.add_argument('--stderr', help='Mark test run as interesting if stderr contains this text')
parser.add_argument('--compiler', help='Path to compiler.  If not specified, cl.exe will be located in PATH')
parser.add_argument('--cflags', help='flags to pass to compiler.')
parser.add_argument('--cores', help='Number of cores to use.  (By default all available cores will be used)')
parser.add_argument('--creduce', help='Path to creduce perl script.  If not specified, PATH will be searched')
parser.add_argument('--now', action='store_true', help='Run this as an interestingness test instead of a wrapper')

args = parser.parse_args()

def _generate_test_script():
    global args
    # If the user specified a custom interestingness test script, use that.
    # Otherwise, call back into this script with argument values updated to
    # indicate things we may have calculated while sanitizing args.
    if args.script:
        arglist = [args.script]
    else:
        arglist = [os.path.realpath(__file__)]
        arglist.append('--source=%s' % args.source)
        arglist.append('--compiler=%s' % args.compiler)
        if args.stdout:
            arglist.append('--stdout=%s' % args.stdout)
        if args.stderr:
            arglist.append('--stderr=%s' % args.stderr)
        if args.cflags:
            arglist.append('--cflags=%s' % args.cflags)
        arglist.append('--now')

    return ' '.join(['"' + x + '"' for x in arglist])

def _generate_test_wrapper():
    batfd, batpath = tempfile.mkstemp(suffix='.bat', text=True)
    test_args = _generate_test_script()
    command = '"%s" %s' % (sys.executable, test_args)
    os.write(batfd, command)

    os.close(batfd)
    return batpath

def _run_interestingness_test():
    global args
    cflags = shlex.split(args.cflags, posix=False)
    compiler_invocation = [args.compiler] + cflags + [args.source]

    obj = subprocess.Popen(compiler_invocation, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    (stdout, stderr) = obj.communicate()
    # If user specified stdout and it matches, it's interesting
    if args.stdout:
        if args.stdout in stdout:
            return 0
    # If user specified stderr and it matches, it's interesting
    if args.stderr:
        if args.stderr in stderr:
            return 0
    # Nothing matches, not interesting
    return 1

if not args.compiler:
    args.compiler = _which('cl.exe')

if not args.compiler:
    print('Cannot find a working compiler.  Either pass --compiler or make sure cl.exe is in PATH')
    sys.exit(1)

if not os.path.exists(args.source):
    print('Source file "%s" does not exist.' % args.source)
    sys.exit(1)

if args.now:
    exit_code = _run_interestingness_test()
    sys.exit(exit_code)

if not args.creduce:
    args.creduce = _which('creduce')

if not args.creduce:
    print('Cannot find creduce.  Either pass --creduce or make sure it is in PATH')
    sys.exit(1)

if not args.cores:
    import multiprocessing
    args.cores = multiprocessing.cpu_count()

test_wrapper = _generate_test_wrapper()

creduce_args = ['perl', args.creduce, '--n', args.cores, test_wrapper, args.source]

result = subprocess.call(creduce_args, universal_newlines=True)
