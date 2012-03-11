"""
@@ api needs refactoring
- move init calls to run
- clean up input options
"""
import logging
import os
import subprocess
import sys


logger = logging.getLogger(__name__)


class Process(object):
    """
    A slight refactoring of virtualenv.call_subprocess
    """
    def __init__(self, cmd, logger=logger, stdout=True, stderr=None, shell=False, stdin=None,
                 filter_stdout=None, cwd=None,
                 raise_on_returncode=True, extra_env=None,
                 remove_from_env=None, return_output=False):
        if isinstance(cmd, basestring):
            cmd = [str(x) for x in cmd.split()]
        self.cmd = cmd
        self.logger = logger
        self.stdout = stdout
        if stdout is True:
            self.stdout = sys.stdout
        if not stdout:
            self.stdout = subprocess.PIPE
        if stdout is False:
            self.stdout = open('/dev/null')
            
        self.stderr = stderr
        self.stdin = stdin is True and sys.stdin or stdin 

        self.filter_stdout = filter_stdout
        self.cwd=cwd
        self.raise_on_returncode=raise_on_returncode
        self.env = self.prep_env(extra_env, remove_from_env)
        self._proc = None
        self.command_desc = self.make_command_desc()
        self.return_output = return_output
        self.shell = shell

    def prep_env(self, extra_env=None, remove_from_env=None):
        env = None
        if extra_env or remove_from_env:
            env = os.environ.copy()
            if extra_env:
                env.update(extra_env)
            if remove_from_env:
                for varname in remove_from_env:
                    env.pop(varname, None)
        return env

    @property
    def proc(self):
        if self._proc is None:
            try:
                stdin = self.stdin
                if isinstance(self.stdin, file):
                    stdin = self.stdin.fileno()  
                stdout = self.stdout
                stderr = subprocess.PIPE
                if isinstance(self.stdout, file):
                    stdout = self.stdout.fileno()
                if self.return_output:
                    stdout = subprocess.PIPE
                    stdin = subprocess.PIPE
                    stderr = subprocess.PIPE
                self._proc = subprocess.Popen(self.cmd, stderr=stderr,
                                              stdin=stdin, stdout=stdout,
                                              cwd=self.cwd, env=self.env, shell=self.shell)
            except Exception, e:
                self.logger.fatal("Error %s while executing command %s" % (e, self.command_desc))
                raise
        return self._proc

    def make_command_desc(self):
        cmd_parts = []
        for part in self.cmd:
            if len(part) > 40:
                part = part[:30]+"..."+part[-5:]
            if ' ' in part or '\n' in part or '"' in part or "'" in part:
                part = '"%s"' % part.replace('"', '\\"')
            cmd_parts.append(part)
        return ' '.join(cmd_parts)

    def filter_logging(self, line):
        level = self.filter_stdout(line)
        if isinstance(level, tuple):
            level, line = level
        self.logger.log(level, line)

    def yield_output(self):
        stdout = self.proc.stdout
        stderr = self.proc.stderr
        if not stdout or stderr:
            raise StopIteration()
        while 1:
            for stream in stderr, stdout,:
                if not stream:
                    continue
                line = next(stream)
                line = line.rstrip()
                if line is not None:
                    if self.filter_stdout:
                        self.filter_logging(line)
                    else:
                        self.logger.info(line)                        
                    yield line

    long_format = "%s\n----------------------------------------"

    def run(self, capture=False, quiet=False):
        """
        Run the subprocess based on state established on
        initialization.
        """
        all_output = []
        self.logger.debug("Running command %s", self.command_desc)
        if not self.stdout is None:
            all_output = [x for x in self.yield_output()]
        else:
            self.proc.communicate()
        self.proc.wait()
        if self.proc.returncode:
            if self.raise_on_returncode:
                if all_output:
                    self.logger.notify('All output from command %s:', self.command_desc)
                    self.logger.notify(self.long_format % '\n'.join(all_output))
                error = OSError("Command %s failed with error code %s"
                              %(self.command_desc, self.proc.returncode))
                error.retcode = self.proc.returncode
                raise error
            else:
                self.logger.warn("Command %s had error code %s", self.command_desc, self.proc.returncode)
        if self.return_output:
            return "".join(all_output)
        return self.proc.returncode
