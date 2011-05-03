from path import path
import os
import subprocess

#<CONSTANTS># module constants are inserted here
bundle_path = None
#</CONSTANTS>#

def sh(command):
    """
    execute a command 
    """
    return subprocess.call(command.split())

def extend_parser(optparse_parser):
    """
    You can add or remove options from the parser here.
    """
    print "parser"


def adjust_options(options, args):
##         You can change options here, or change the args (if you accept
##         different kinds of arguments, be sure you modify ``args`` so it is
##         only ``[DEST_DIR]``).
    print "options"
    pass

    
def after_install(options, home_dir):
##         After everything is installed, this function is called.  This
##         is probably the function you are most likely to use.  An
##         example would be::
    
##             def after_install(options, home_dir):
##                 subprocess.call([join(home_dir, 'bin', 'easy_install'),
##                                  'MyPackage'])
##                 subprocess.call([join(home_dir, 'bin', 'my-package-script'),
##                                  'setup', home_dir])
    
##         This example immediately installs a package, and runs a setup
##         script from that package.
    print __file__
    print "after_install"
