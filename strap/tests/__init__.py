from contextlib import contextmanager
from path import path
import os
import logging

logger = logging.getLogger(__name__)

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


def teardown():
    venv = path(os.environ['VIRTUAL_ENV'])
    cleaned = len([bb.rmtree() for bb in venv.dirs('build-bundle*')])
    logger.info('%s build-bundles cleaned', cleaned)
