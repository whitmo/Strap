from contextlib import contextmanager
from fabric.api import local
import argparse
import os
import virtualenv
import zipfile


def main(args):
    """
    bundle name
    -e extra text to resolve
    -r requirements file
    """
    #venv = os.environ('VIRTUAL_ENV')
    local('pip bundle -r %s %s' %(reqfile, bundle_name))
    with zipfile.ZipFile(bundle_name, 'a') as bundle:
        bundle.writestr(virtualenv.create_bootstrap_script("print 'woooooooot'"), '__main__.py')
        

@contextmanager
def pushd(dir):
    '''A context manager (Python 2.5+ only) for stepping into a 
    directory and automatically coming back to the previous one. 
    The original directory is returned. Usage is like this::
    
        from __future__ import with_statement
        # the above line is only needed for Python 2.5
        
        from paver.easy import *
        
        @task
        def my_task():
            with pushd('new/directory') as old_dir:
                ...do stuff...
    '''
    old_dir = os.getcwd()
    os.chdir(dir)
    try:
        yield old_dir
    finally:
        os.chdir(old_dir)
