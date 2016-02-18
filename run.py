import argparse
import os
import shutil
import subprocess
import sys

# convert windows paths to unix paths for folder depths > 1
def unixify_path(path):
    if sys.platform == 'win32' and subdirectory_path.count('\\') > 1:
        return subdirectory_path.replace('\\', '/')
    return path;

if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--repo_dir',
        type=str,
        nargs='?',
        help='Path of original repo.')
    parser.add_argument(
        '--output_dir',
        type=str,
        nargs='?',
        help='Path of final output directory.')
    parser.add_argument(
        '--subdirectory_path',
        type=str,
        nargs='?',
        help='Relative path of subdirectory path to isolate.')
    args = parser.parse_args()

    original_repo_path = args.repo_dir
    new_repo_path = args.output_dir
    subdirectory_path = args.subdirectory_path
else:
    original_repo_path = input('Original Repo Path: ')
    new_repo_path = input('New Repo Path: ')
    subdirectory_path = input(
        'Subdirectory path to isolate (relative to %s): ' %
        new_repo_path)

if not os.path.exists(new_repo_path):
    os.makedirs(new_repo_path)
else:
    print 'OUTPUT DIRECTORY ALREADY EXISTS'
    sys.exit(0)

# clone original repo to new working repo
print 'Cloning original repo...'
subprocess.call(['git',
                 'clone',
                 '--no-hardlinks',
                 original_repo_path,
                 new_repo_path])

os.chdir(new_repo_path)

unix_subdirectory_path = unixify_path(subdirectory_path)

# discard everything but our subdirectory, promote to root level
print 'Discarding unwanted changes...'
subprocess.call(['git',
                 'filter-branch',
                 '--subdirectory-filter',
                 unix_subdirectory_path,
                 'HEAD',
                 '--',
                 '--all'])
subprocess.call(['git', 'reset', '--hard'])

# cleanup
print 'Cleaning up...'
subprocess.call(['git', 'gc', '--aggressive'])
subprocess.call(['git', 'prune'])

# origin stuff
print 'Removing old origin..'
subprocess.call(['git', 'remote', 'rm', 'origin'])

# remove from original repo
print "Removing subdirectory from original repository"
os.chdir(original_repo_path)
shutil.rmtree(os.path.abspath(subdirectory_path))
subprocess.call(['git',
                 'add',
                 '-u',
                 unix_subdirectory_path])
subprocess.call(['git',
                 'commit',
                 '-m',
                 'Detatched %s into separate repository' % subdirectory_path])
