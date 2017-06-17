#!/usr/bin/env python

import getopt, os, shutil, sys


def usage():
    print 'Requires --source_dir and --target_dir arguments'


def main(argv):
    """
    Given a source and a target directory, this script returns directories
    that are present in target dir but not in source dir.
    """
    try:
        opts, args = getopt.getopt(argv, "s:t:e:",
                                   ["source_dir=", "target_dir=",
                                    'exclude='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    args = {}
    for opt, arg in opts:                
        if opt in ("-s", "--source_dir"):
            args['source_dir'] = arg
        elif opt in ("-t", "--target_dir"):
            args['target_dir'] = arg
        elif opt in ("-e", "--exclude"):
            args['exclude'] = arg

    if 'source_dir' not in args or 'target_dir' not in args:
        usage()
        sys.exit(2)
    
    source_dir = args.get('source_dir', '').rstrip('/')
    target_dir = args.get('target_dir', '').rstrip('/')
    exclude = args.get('exclude', '')

    if not os.path.isdir(source_dir):
        print "source_dir doesn't exist or is not a directory"
    if not os.path.isdir(target_dir):
        print "target_dir doesn't exist or is not a directory"
    
    # Get all folders in source and target dir
    dirs_in_source = set([os.path.relpath(f[0], source_dir) 
                            for f in os.walk(source_dir)])
    dirs_in_target = set([os.path.relpath(f[0], target_dir) 
                                for f in os.walk(target_dir)])
    dirs_to_remove = dirs_in_target.difference(dirs_in_source)

    # Exclude directory
    if exclude:
        excluded_dirs = exclude.split(',')
        # Filter out all excluded directories
        for exclude in excluded_dirs:
            exclude_dir = '%s/' % exclude
            dirs_to_remove = [directory for directory in dirs_to_remove
                              if exclude_dir not in directory]
        dirs_to_remove = [directory for directory in dirs_to_remove
                          if os.path.basename(directory) not in excluded_dirs]

    dir_prefix = target_dir + '/'
    dirs_to_remove = [dir_prefix + directory for directory in dirs_to_remove]
    for directory in dirs_to_remove:
        print directory


if __name__ == "__main__":
    main(sys.argv[1:])