# -*- coding: utf-8 -*-

"""Coffe's working directory class has been designed to
facilitate calling simulation programs and shell commands.
It makes sure that all output is logged properly so that
errors in subprograms can be traced. It also allows
saving and loading instances, which provides the basis for
the :mod:`~coffe.core.cluster` module.

The :class:`~CoffeWorkDir` can be used either as a context manager (python's :code:`with` statement)
or as a base class, e.g., for simulation classes. When used as a context manager, exceptions that are
raised in the :code:`with` block are automatically logged. When used as a base class, logging of exceptions
can be turned on via the :func:`~log_exceptions` decorator.


Examples:
    Example 1 - Usage as a Context Manager::

        def run_some_external_program(work_dir, filename):
            with CoffeWorkDir(work_dir, "run_some_external_program", locals()) as cwd:
                filename = cwd.abspath(filename)
                cmd = "some_program " + filename
                cwd.call_cmd(cmd)
                with open (cwd.last_outfile()) as f:
                 # ... parse output etc ...
                cwd.logger.info("print some info")

    Example 2 - Usage as a Base Class::

        class SimulationClass(CoffeWorkDir):

             @log_exceptions    # This decorator enables automatic logging of exceptions.
             def __init__(work_dir, input_file, **kwargs):
                 super(SimulationClass,self).__init__(work_dir, "SimulationClass", locals())
                 self.logger.info("Setup simulation class")
                 self.my_input_file = self.abspath(input_file)

             @log_exceptions
             def __call__():
                 self.call_cmd("simulation_command " + self.my_input_file)

        ############################################
        # Code ran on head node or local machine
        ############################################

        # Setup Simulation
        obj = SimulationClass(".", "input.dat")
        obj.save()
        filename = obj.dumpfilename()

        ############################################
        # Code ran on compute node
        ############################################

        obj = CoffeWorkDir.load(filename)
        obj()   # run simulation

        # Note: to run from the command line and not from
        # a python program, see 'coffe run_class -h'

"""

from __future__ import absolute_import, division, print_function


import functools
import logging
import os
import glob

from coffe.core import compat, shell, saver, graffiti
from coffe.core.filesys import make_abspath, stderr_filename, stdout_filename


def get_global_log_level():
    return logging.getLogger().getEffectiveLevel()


def set_global_log_level(level):
    logging.getLogger().setLevel(level=level)


def prepare_coffe_work_dir(work_dir):
    """Create work_dir, hidden .coffe subdirectory and logger instance.
    Calling this function multiple times for the same work_dir is valid
    and will not change the outcome.

    Args:
        work_dir (str): a directory path. If the directory does not exist, it is created by this function.

    Returns:
        A tuple with three items:
            - work_dir (str):  Absolute path of working directory.
            - coffe_dir (str): Hidden coffe subdirectory (work_dir/.coffe).
            - logger (:obj:`logging.Logger`): A logger that writes to work_dir/.coffe/log.txt.

    Raises:
        Assertion Error: if the working directory is not a path
        OSError: if the directory is not writable
    """
    # create work_dir
    _work_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(work_dir)))
    if not os.path.isdir(_work_dir):
        if not os.path.isdir(os.path.realpath(os.path.join(_work_dir, os.pardir))):
            raise OSError("Working directory {} could not be created. "
                          "Parent directory does not exist.".format(_work_dir))
        else:
            try:
                os.mkdir(_work_dir)
            except OSError:
                raise OSError("Working directory {} could not be created. "
                              "Make sure you have writing permissions.".format(_work_dir))
    assert os.path.isdir(_work_dir)

    # create .coffe subdirectory
    coffe_dir = make_abspath(".coffe", _work_dir, check_exists=False)
    coffe_just_created = False
    if not os.path.isdir(coffe_dir):
        try:
            os.mkdir(coffe_dir)
            coffe_just_created = True
        except OSError:
            raise OSError("Coffe directory {} could not be created. "
                          "Make sure you have writing permissions.".format(coffe_dir))
    assert os.path.isdir(coffe_dir)

    # create logger instance
    logger = logging.getLogger('{}'.format(_work_dir))
    if coffe_just_created or (not len(logger.handlers)):  # avoid redundant handlers
        logger.setLevel(logging.DEBUG)
        # File logging
        log_file = os.path.join(coffe_dir,"log.txt")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = graffiti.ColorFormatter('%(asctime)s - %(levelname)s - %(message)s',
                                                 use_color=False)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(get_global_log_level())
        console_formatter = graffiti.ColorFormatter('%(message)s', use_color=True)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return _work_dir, coffe_dir, logger


def log_exceptions(func):
    """
    A decorator for methods to write exceptions to self.logger before they are invoked.

    Args:
        func: A method of a class that has a property 'logger'.

    Returns:
        A modified method that writes exceptions to a logger.
    """
    # get arguments of function to allow decorators after this decorator
    arg = compat.get_function_args(func)
    assert len(arg) > 0 and arg[0] == "self", \
        "log_exceptions is designed for methods, not functions," \
        "but you tried it on {} in module {}".format(func.__name__, func.__module__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        assert len(args) > 0,  \
            "log_exceptions is designed for methods, not functions," \
            "but you tried it on function {} in module {}".format(func.__name__, func.__module__)
        self = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.exception(e)
            raise e
    wrapper.__wrapped__ = func  # required for python 2
    return wrapper


class CoffeWorkDir(object):
    """Coffe working directory.
    This class provides the following features:
        -   A hidden subdirectory :attr:`~coffe_dir` that can be used to store temporary
            files and output from shell commands.
        -   A :attr:`~logger` that writes detailed debug-level information to .coffe/log.txt,
            while putting clean output to the console.
        -   A method :meth:`~call_cmd` that executes shell commands
            (by default locally in the working directory) and stores the output.
        -   Methods to :meth:`~save` and :meth:`~load` instances.
            When simulation classes are defined as subclasses of :class:`~CoffeWorkDir`,
            simulations can be set up on the head node of a cluster and then run on a compute node
            through coffe's :mod:`~coffe.core.cluster` module.

    (See examples of usage in module description: :mod:`~coffe.core.coffedir`.)
    """

    def __init__(self, work_dir, log_name=None, log_variable_dict=None):
        """The constructor creates the working directory, hidden subdirectory .coffe, and a logger that
        writes to .coffe/log.txt.
        If the paths already exist, they are used as they are and output is appended to ./coffe/log.txt.

        Args:
            work_dir (str): The working directory
            log_name (str, optional):   A name for this instance that is written to the log file.
                                        Usually the name
            log_variable_dict (:obj:`dict`, optional): A dictionary of variables that were passed to the
                                                        constructor of a subclass or a function.
        """
        self._work_dir, _, self._logger = prepare_coffe_work_dir(work_dir)
        self.logger.debug("CoffeWorkDir: {}".format(self._work_dir))
        if log_name:
            self.logger.debug("... running {}".format(log_name))
        if log_variable_dict:
            self.logger.debug("... with variables {}".format(log_variable_dict))
        self._last_errfile, self._last_outfile = None, None

    @property
    def work_dir(self):
        """str: absolute path of the working directory"""
        return self._work_dir

    @property
    def coffe_dir(self):
        """str: absolute path of work_dir/.coffe"""
        return os.path.join(self.work_dir, ".coffe")

    @property
    def logger(self):
        """:obj:`logging.Logger` instance that writes to work_dir/.coffe/log.txt and to the console"""
        return self._logger

    @property
    def logfile(self):
        """str: The logfile to which the logger instance writes output."""
        return os.path.join(self.coffe_dir, "log.txt")

    def abspath(self, path, check_exists=True):
        """Absolute path.

        Args:
            path (str): A relative path wrt. this working directory.
            check_exists (bool): If true, check if path exists.

        Returns:
            str: An absolute path.

        Raises:
            AssertionError: If check_exists==True and path does not exist.
        """
        return make_abspath(path, self.work_dir, check_exists=check_exists)

    def relpath(self, path):
        """Path relative to this working directory.

        Args:
            path (str): An absolute path.

        Returns:
            str: A relative path.
        """
        return os.path.relpath(path, self.work_dir)

    @log_exceptions
    def call_cmd(self, cmd, **kwargs):
        """Call a command in this working directory. By default, the stdout and stderr are redirected to
        files in the .coffe subdirectory.
        You can access the stdout and stderr via and :attr:`~last_outfile` :attr:`~last_errfile`,
        respectively.

        Args:
            cmd (str): A shell command.
            **kwargs: Can be any of the arguments in :func:`~coffe.core.shell.call_cmd`.
                      Options specified via kwargs overwrite the standard stdout, stderr and work_dir.
        """
        defaults = {"work_dir": self.work_dir,
                    "stdout_file": self._stdout_file(cmd),
                    "stderr_file": self._stderr_file(cmd),
                    }
        self._last_outfile, self._last_errfile = defaults["stdout_file"], defaults["stderr_file"]
        defaults.update(kwargs)
        shell.call_cmd(cmd, **defaults)

    @property
    def last_errfile(self):
        """str: Name of the stderr file that was used by the last command run via :meth:`~call_cmd`.
        """
        return self._last_errfile

    @property
    def last_outfile(self):
        """str: Name of the stdout file that was used by the last command run via :meth:`~call_cmd`.
        """
        return self._last_outfile

    def _stderr_file(self, cmd):
        """Default name for a file storing the stderr of a command run in this working directory.
        Note that the filename contains the time of invocation.

        Args:
            cmd (str): A shell command

        Returns:
            str: an absolute filename

        """
        return stderr_filename(self.coffe_dir, ("_".join(cmd.strip().replace(os.path.sep, "").split()))[:10])

    def _stdout_file(self, cmd):
        """Default name for a file storing the stdout of a command run in this working directory.
        Note that the filename contains the time of invocation.

        Args:
            cmd (str): A shell command

        Returns:
            str: an absolute filename

        """
        return stdout_filename(self.coffe_dir, ("_".join(cmd.strip().replace(os.path.sep, "").split()))[:10])

    def __enter__(self):
        """ Enter the with statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Exit the with statement and log errors.
        """
        if exc_type is not None:
            self.logger.error(exc_val)
            return False

    def save(self):
        """Saves this instance to a file.
        """
        saver.save(self, os.path.join(self.coffe_dir, self.dumpfilename))

    @staticmethod
    def load(path):
        """Load a workdir object from a file.
        This function automatically detects if the workdir was moved.
        If a move is detected, an automatic replacement of paths is attempted.
        If the candidate path for replacement does not exist, the path is not replaced.

        Args:
            path (str): The work_dir/.coffe/...obj file to which the object has been saved.
                        If there is only one such obj file, you can also specify the work_dir itself as path


        Returns:
            :obj:`~CoffeWorkDir`: A coffe workdir (or subclass) instance.

        Raises:
            IOError: If no unique .obj file is not found in the path.
            AssertionError: If .obj file does not exist or does not store a WorkDir object.
        """
        if os.path.isdir(path) and os.path.isabs(path):
            cofd = os.path.join(path, ".coffe")
            objs = glob.glob(os.path.join(cofd, "*.obj"))
            if len(objs) == 0:
                raise IOError("Could not load object. No .obj file in {}".format(cofd))
            elif len(objs) > 1:
                raise IOError("Could not load object. {}...obj is not unique."
                              "Specify the object directly: CoffeWorkDir.load(....obj)".format(cofd)
                              )
            else:
                assert len(objs) ==1
                path = os.path.abspath(objs[0])
        assert os.path.isfile(path)
        inst = saver.load(path)
        new_wd = os.path.abspath(os.path.dirname(os.path.dirname(path)))
        old_wd = inst.work_dir
        # replace path names to support the situation that the dump file was moved
        for k in inst.__dict__:
            try:
                relpath = os.path.relpath(inst.__dict__[k], old_wd)
                candidate = os.path.abspath(os.path.join(new_wd, relpath))
                if os.path.exists(candidate):
                    inst.__dict__[k] = candidate
                    print("rep", k, candidate)
            except:
                pass
        assert isinstance(inst, CoffeWorkDir)
        return inst

    def __setstate__(self, state):
        """Makes sure that logger is not loaded from file.
        The problem here is that the logging module operates on singletons, which is
        why classes that have a logger instance can not be pickled.

        By overriding the setstate and getstate methods, classes that inherit from
        the present class can be pickled. Note that they are implicitly assumed to
        possess a work_dir and a logger.

        Args:
            state: see documentation of pickle module.

        Returns:
            None
        """
        assert '_work_dir' in state
        _, _, state['_logger'] = prepare_coffe_work_dir(state['_work_dir'])
        self.__dict__.update(state)

    def __getstate__(self):
        """Makes sure that logger is not saved to file (see documentation of :meth:`~__getstate__`)

        Returns:
            :obj:`dict`: state of this object as dictionary (see documentation of pickle module)
        """
        state = dict(self.__dict__)
        assert '_work_dir' in state
        del state['_logger']
        return state

    @property
    def dumpfilename(self):
        """str: The absolute path of the file that is used to store this object.
        """
        return os.path.join(
            self.coffe_dir,
            self.__class__.__name__ + ".obj"
            #"-".join(repr(self).split()).replace("<", "").replace(">", "").replace(os.path.sep, "").replace(" ","")
        )

    def prnt(self, *args, **kwargs):
        """Wraps self.logger.info, but acts like a print function.
        To see output from print on the console.
        Output from all levels is written to the :attr:`~logfile`.
        Args:
            *args:
            indent:
            sep:

        Returns:

        """
        indent = kwargs.get("indent", 0)
        sep = kwargs.get("sep", ' ')
        styleargs = (a for a in args if isinstance(a, graffiti.ANSIStyle))
        otherargs = (str(a) for a in args if not isinstance(a, graffiti.ANSIStyle))
        msg = graffiti.apply_indent(sep.join(otherargs), indent)
        self.logger.info(msg, *styleargs)

