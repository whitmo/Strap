import subprocess
import os


class Process(object):
    """
    A slight refactoring of virtualenv.call_subprocess
    """
    def __init__(self, cmd, logger, show_stdout=True,
                 filter_stdout=None, cwd=None,
                 raise_on_returncode=True, extra_env=None,
                 remove_from_env=None, return_output=False):
        if isinstance(cmd, basestring):
            cmd = [str(x) for x in cmd.split()]
        self.cmd = cmd
        self.logger = logger
        self.show_stdout = show_stdout
        self.stdout = None
        if not show_stdout:
            self.stdout = subprocess.PIPE
        self.filter_stdout=filter_stdout
        self.cwd=cwd
        self.raise_on_returncode=raise_on_returncode
        self.env = self.prep_env(extra_env, remove_from_env)
        self._proc = None
        self.command_desc = self.make_command_desc()
        self.return_output = return_output

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
                self._proc = subprocess.Popen(
                    self.cmd, stderr=subprocess.STDOUT, stdin=None, stdout=self.stdout,
                    cwd=self.cwd, env=self.env)
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

    def yield_output(self):
        stdout = self.proc.stdout
        while 1:
            if not stdout:
                raise StopIteration()
            line = stdout.readline()
            if not line:
                break
            line = line.rstrip()
            yield line
            if self.filter_stdout:
                level = self.filter_stdout(line)
                if isinstance(level, tuple):
                    level, line = level
                self.logger.log(level, line)
## @@ todo            
##                 if not self.logger.stdout_level_matches(level):
##                     logger.show_progress()
            else:
                self.logger.info(line)

    def run(self):
        """
        It's what you do right?
        """
        all_output = []
        self.logger.debug("Running command %s", self.command_desc)
        if self.show_stdout is not None:
            all_output = [x for x in self.yield_output()]
        else:
            self.proc.communicate()
        self.proc.wait()
        if self.proc.returncode:
            if self.raise_on_returncode:
                if all_output:
                    self.logger.notify('Complete output from command %s:', self.command_desc)
                    self.logger.notify('\n'.join(all_output) + '\n----------------------------------------')
                raise OSError("Command %s failed with error code %s"
                              %(self.command_desc, self.proc.returncode))
            else:
                self.logger.warn("Command %s had error code %s", self.command_desc, self.proc.returncode)
        if self.return_output:
            return "".join(all_output)
        return self.proc.returncode
