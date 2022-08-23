# -*- coding: utf-8 -*-

"""A python module for submitting bash scripts to the cluster.

Note:
    Modifying this module requires care, because the CI can not directly test
    slurm and torque commands. Make sure to run py.test on slurm and torque
    clusters to make sure everything works as expected.
"""

from __future__ import absolute_import, division, print_function

import os
import random
import subprocess
import re
import multiprocessing
import time


from coffe.core import saver, decorators, filesys, thirdparty, cmdchain, coffedir, shell


class ClusterError(Exception):
    """
    A custom error class for cluster submission
    """
    pass


class ClusterJobAlreadyCompletedError(ClusterError):
    pass


class ClusterJobAlreadyQueueingError(ClusterError):
    pass


SUBMIT_COMMAND = {"slurm": "sbatch", "torque": "qsub", None: "bash"}
STATUS_COMMAND = {"slurm": "squeue", "torque": "qstat", None: ""}
DELETE_COMMAND = {"slurm": "scancel", "torque": "qdel", None: None}
JOBNAME_OPTION = {"slurm": " --job-name", "torque": " -N",
                  None: " jobname"} # the blanks are important
OPTION_DELIMIT = {"slurm": "=", "torque": " ", None: ": "}
OPTION_PREFIX = {"slurm": "#SBATCH", "torque": "#PBS", None: "#"}


class Status(type):
    """
    Status of a cluster job.
    """
    not_written = "not_written"  #: Script has not been written, yet.
    not_submitted = "not_submitted"  #: Script written, not submitted.
    queueing = "queueing"  #: Job has been submitted and is in the queue.
    running = "running"  #: Job is currently running on the cluster.
    completed = "completed"  #: Job has terminated successfully.
    error = "error"  #: Job terminated, but did not complete.

    @classmethod
    def is_written(cls, status):
        return not status == cls.not_written

    @classmethod
    def is_submitted(cls, status):
        return status not in [cls.not_written, cls.not_submitted]

    @classmethod
    def read(cls, file):
        """Read from file.

        Returns:
            A pair (status, job_id)

             - str: status
             - int: job_id (None if not yet queueing)
        """
        assert os.path.isfile(file)
        with open(file,"r") as f:
            content = f.read().strip().split()
            if len(content) == 1:
                status = content[0]
                assert status in [cls.not_written, cls.not_submitted]
                return status, None
            elif len(content) == 2:
                status, job_id = content
                job_id = int(job_id)
                assert status in [cls.queueing, cls.running,
                                  cls.completed, cls.error]
                return status, job_id
            else:
                raise ClusterError("Status file had bad format")

    @classmethod
    def write(cls, file, status, job_id=None):
        """Write to file."""
        if status == Status.queueing:
            assert job_id is not None
            with open(file, "w") as f:
                f.write("{} {}".format(status, int(job_id)))
        elif status in [Status.running,
                        Status.completed,
                        Status.error]:
            assert job_id is None
            previous, job_id = cls.read(file)
            with open(file, "w") as f:
                f.write("{} {}".format(status, job_id))
        else:
            assert status in [Status.not_written, Status.not_submitted]
            assert job_id is None
            with open(file, "w") as f:
                f.write("{}".format(status))


class ClusterJob(coffedir.CoffeWorkDir):
    """A class for submitting jobs to a cluster.
    Supports torque and slurm queues.

    The queueing argument can also be :code:`None`.
    In this case the job is run locally - detached
    from the main process, so that the main process will continue running.
    Exceptions in ClusterJob processes are not passed to the main thread.
    Instead, they are indicated by :code:`ClusterJob.status == Status.error`.

    :class:`~ClusterJob` instances are not reusable. Once a job
    has completed successfully it is not possible to run a job with the same
    name in the same working directory.

    Status and job_id determination is based on a jobname.status file in the
    local .coffe directory.
    This makes the status check more expensive but
    supports checks spanning multiple python processes (e.g.
    when a process has terminated or is forked from the main process).

    Concretely, when you create an instance of :class:`~ClusterJob`,
    the job can be identified as completed upon construction
    (if a previous job with the same name and working directory
    has completed successfully). This will prevent jobs that are likely
    to overwrite all data from running.
    The same is True for jobs that are currently queueing or running.
    If the previous job has a pre-submission or error status, the
    present job is set up as a fresh, clean instance with status
    :attr:`~Status.not_written`.
    """

    @coffedir.log_exceptions
    @decorators.args_from_configfile
    def __init__(self, queueing=None, batch_template=None,
                 job_name=None, work_dir=None):
        """
        Args:
            queueing (str): Specifies the queueing system
                (default=None, "torque", or "slurm")
            batch_template(str): A template batch script,
                containing header, module loads, ....
                Commands are appended to this script.
            work_dir(str): The coffe working directory.

        Raises:
            ClusterError: If batch template script does not suit the queueing system.
        """
        if work_dir is None:
            work_dir="."

        super(ClusterJob, self).__init__(work_dir, "ClusterJob", locals())
        
        self.script_name = None
        
        if job_name is None:
            self._job_name = self.work_dir[-10:].replace(os.sep,"-")
        else:
            self._job_name = job_name
        self.queueing = queueing
        self.commands = []
        if batch_template is not None:
            self.batch_template = filesys.make_abspath(batch_template, work_dir)
        else:
            self.batch_template = None

        # check input
        if queueing is not None:
            assert queueing in ["slurm", "torque"], \
                "queuing must be None, 'slurm', or 'torque'"
            assert batch_template is not None, \
                "queueing='slurm', or 'torque' requires a batch_script"

        if queueing == "slurm":
            thirdparty.SLURM.require()
            is_slurm = False
            with open(self.batch_template, "r") as f:
                for line in f:
                    if line.strip().startswith("#PBS"):
                        raise ClusterError("You are not allowed to submit "
                                           "a torque script to a slurm queue.")
                    if line.strip().startswith("#SBATCH"):
                        is_slurm = True
            if not is_slurm:
                raise ClusterError(
                    "Your batch script will not work for slurm "
                    "queueing systems. No #SBATCH found in batch script.")
        if queueing == "torque":
            thirdparty.TORQUE.require()
            is_torque = False
            with open(self.batch_template, "r") as f:
                for line in f:
                    if line.strip().startswith("#SBATCH"):
                        raise ClusterError(
                            "You are not allowed to submit a "
                            "slurm script to a torque queue.")
                    if line.strip().startswith("#PBS"):
                        is_torque = True
            if not is_torque:
                raise ClusterError(
                    "Your batch script will not work for torque "
                    "queueing systems. No #PBS found in batch script.")
        self._local_process = None

        # determine status
        s = self.status
        if s == Status.not_written:
            return
        elif s in [Status.running,
                   Status.queueing,
                   Status.completed]:
            self.logger.debug("Resuming cluster job. Status was {}".format(s))
        elif s in [Status.not_submitted,
                   Status.error]:
            # reset status
            self.logger.debug("Resetting cluster job. Status was {}".format(s))
            self.status = Status.not_written
            

    @property
    def job_name(self):
        """str: The name of the job (read-only)."""
        return self._job_name

    @property
    def status_file(self):
        """str: Path of the status file (read-only)."""
        return os.path.join(self.coffe_dir, "{}.status".format(self.job_name))

    @property
    def status(self):
        """
        str: The status, as read from the status file.

        When setting the status, you can either pass
        a string (the Status) or an integer (interpreted as
        the job id, setting the status to :attr:`~Status.queueing` automatically).
        """
        if not os.path.isfile(self.status_file):
            return Status.not_written
        else:
            read_status, job_id = Status.read(self.status_file)
        # check for inconsistencies
        # ---- not in queue, but status in queue ----
        if not self._is_active(job_id):
            if read_status == Status.queueing:
                Status.write(self.status_file, Status.error)
                return Status.error
                #raise ClusterError("Job {} crashed -- disappeared from "
                #                   "queue without having run. "
                #c                  "Work_dir: {}".format(job_id, self.work_dir))
            if read_status == Status.running:
                Status.write(self.status_file, Status.error)
                return Status.error
                #raise ClusterError("Job {} crashed -- started but did not"
                #                   "complete. "
                #                   "Work_dir: {}".format(job_id, self.work_dir))
        return read_status

    @status.setter
    def status(self, value):
        if isinstance(value, str):
            Status.write(self.status_file, value)
        else:
            value = int(value)
            Status.write(self.status_file, Status.queueing, value)

    @property
    def job_id(self):
        """int: The job id, as read from the status file.
        Returns :code:`None` if the job has not been submitted, yet."""
        if not os.path.isfile(self.status_file):
            return None
        else:
            read_status, job_id = Status.read(self.status_file)
        return job_id

    @property
    def script(self):
        """str: The name of the batch script."""
        
        # Create the name of the bash script that is created on the first call
        # and re-use it
        if not self.script_name:
            self.script_name = filesys.batch_filename(self.coffe_dir, self.job_name)
            
        return self.script_name

    @property
    def is_written(self):
        """bool: Whether the batch script has been written."""
        return Status.is_written(self.status)

    @property
    def is_submitted(self):
        """bool: Whether the batch script has been submitted."""
        return Status.is_submitted(self.status)

    @property
    def local_process(self):
        """instance of :class:`~multiprocessing.Process`,
        only defined if queueing is :code:`None`
        """
        assert self.queueing is None
        return self._local_process

    @coffedir.log_exceptions
    def write_script(self):
        """Write the submission script.

        Returns:
            str: Path of the submission script.

        Raises:
            ClusterError: If script is already written.
        """
        if self.is_written:
            raise ClusterError("ClusterJobs are not reusable. "
                               "Script is already written.")
        jobname_option = "{}{}{}{}\n".format(OPTION_PREFIX[self.queueing],
                                             JOBNAME_OPTION[self.queueing],
                                             OPTION_DELIMIT[self.queueing],
                                             self.job_name
                                             )
        commands = ["## COMMANDS: ##" + os.linesep*2,
                    "err=0",
                    "trap 'err=1' ERR",
                    "cd {}".format(self.work_dir),
                    "coffe core update-cluster-status {} {};".format(
                                            Status.running, self.status_file),
                    ""
                   ] + self.commands + ["", "",
                                        'if [ "$err" -eq 0 ]; then',
                                        "coffe core update-cluster-status {} {};".format(
                                            Status.completed, self.status_file),
                                        'fi',
                                        "test $err = 0"
                                        ]
        with open(self.script, "w") as batch:
            # copy template and replace jobname
            is_jobname_written = False
            if self.batch_template is not None:
                with open(self.batch_template, "r") as template:
                    for line in template:
                        if ((self.job_name is not None) and
                                (JOBNAME_OPTION[self.queueing] in line) and
                                (OPTION_PREFIX[self.queueing] in line)):
                            batch.write(jobname_option)
                            is_jobname_written = True
                            continue
                        batch.write(line)
            if not is_jobname_written:
                batch.write(jobname_option)
            # write commands
            if self.commands:
                for line in commands:
                    batch.write(line + os.linesep)
        self.status = Status.not_submitted
        return self.script

    @coffedir.log_exceptions
    def __add__(self, command):
        """Add a command to the cluster job.

        Args:
            command (str): Either a string (command line command)
                or an instance of a callable class.

        Raises:
            ClusterError: If script is already written or if added command is
                neither a string nor an instance of a callable class.
        """
        if self.is_written:
            raise ClusterError("ClusterJobs are not reusable. "
                               "Script is already written.")
        if isinstance(command, str):    # ==== add string ====
            self.commands += [command]
        elif callable(command):         # ==== add callable instance ====
            instance = command
            assert cmdchain.has_empty_call(instance)
            # replace white spaces by -
            filename = "-".join(repr(instance).split()
                                ).replace("<","").replace(">","")
            filename = os.path.join(self.coffe_dir, filename)
            saver.save(instance, filename)
            self.commands += ["coffe run-class {}".format(filename)]

        else:
            raise ClusterError(
                "Cannot add {} to cluster (is neither string "
                "nor instance of callable class)".format(command))
        return self

    def clear(self):
        """Clear the command list"""
        self.commands = []

    @coffedir.log_exceptions
    def submit(self):
        """Submit the job to the queueing system.

        Returns:
            int: job_id

        Raises:
            ClusterJobAlreadyQueueingError: If job is already in queue.
            ClusterJobAlreadyCompletedError: If job is already completed.
            ClusterError: If the submission command failed.
        """
        self.logger.info("Submit job (jobname: {})".format(self.job_name))
        if self.status == Status.completed:
            raise ClusterJobAlreadyCompletedError(
                "Job is already completed. Aborting to prevent loss of data.")
        elif self.status == Status.queueing:
            raise ClusterJobAlreadyQueueingError(
                "Job is already queueing. Aborting to prevent race conditions.")
        elif self.status == Status.not_written:
            self.write_script()

        # prepare submit command
        sub_cmd = "{} {}".format(SUBMIT_COMMAND[self.queueing], self.script)
        self.logger.info("submit command: {}".format(sub_cmd))
        if self.queueing is None:  # ==== local execution ====
            random_id = random.randint(1, 1000000)
            self.status = random_id
            # setting status to int means (status = queueing, job_id = int)
            self._local_process = multiprocessing.Process(
                target=self.call_cmd, args=(sub_cmd,))
            self.local_process.start()
        else:                      # ==== cluster execution ====
            try:
                self.call_cmd(sub_cmd)
            except shell.ShellError:
                with open(self.last_outfile) as f:
                    cmdline = f.read()
                raise ClusterError("Submission failed: {}".format(cmdline))

            with open(self.last_outfile) as f:
                cmdline = f.read()
            # extract jobid
            id = [int(s) for s in re.split(
                r' |\.', cmdline.strip()) if s.isdigit()]
            assert len(id) == 1
            self.status = id[0]
            # setting status to int means (status = queueing, job_id = int)
        self.logger.info("Job ID: {}".format(self.job_id))
        return self.job_id

    @coffedir.log_exceptions
    def kill(self):
        """
        Kill the job.

        Raises:
            ShellError: If the kill command failed.
        """
        if self.status not in [Status.running, Status.queueing]:
            return

        if self.queueing is None:
            self.local_process.terminate()
            time.sleep(0.5)  # give some time to terminate
        else:
            cmd = "{} {}".format(DELETE_COMMAND[self.queueing], self.job_id)
            self.call_cmd(cmd)
        self.status = Status.error

    def _is_active(self, job_id):
        """Check if job is active.

        Args:
            job_id(int): The job id. Needs to be passed to avoid cyclic calling.

        Returns:
            bool: Whether the job is listed, when calling "qstat" or "squeue".
        """
        if self.queueing is None:
            try:
                return self.local_process.is_alive()
            except:
                return False
        else:
            # call and pipe to grep
            cmd = STATUS_COMMAND[self.queueing]
            p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            cmdline = p.communicate()[0]
            grep = subprocess.Popen(("grep {}".format(job_id)).split(),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE)
            cmdline = grep.communicate(cmdline)[0]
            # Sometimes, squeue fails for some reason: in this case return
            # True to prevent the script from crashing
            if p.returncode != 0:
                return True
            if cmdline.strip():  # non-empty string
                return True
            else:
                return False


class ClusterJobGenerator(object):
    """A generator for cluster jobs."""

    @decorators.args_from_configfile
    def __init__(self, queueing=None, batch_template=None, root_dir="."):
        """
        Args:
            queueing (str): The queuing system.
                Can be "torque", "slurm" or :code:`None`.
            batch_template (str): The template file for the submission script
                (should contain header and modules). If :attr:`queueing` is None,
                batch_template can be None, too.
            root_dir (str): The path from which the relative paths
                in this class are interpreted.
        """
        assert queueing in SUBMIT_COMMAND
        self.queueing = queueing
        if batch_template is not None:
            self.batch_template = filesys.make_abspath(batch_template, root_dir)
        else:
            self.batch_template = None
        self.root_dir = os.path.abspath(root_dir)

    def generate_job(self, work_dir, job_name=None):
        """Generate a cluster job.

        Args:
            work_dir(str): The working directory for the job.
            job_name(str): The job name.

        Returns:
            Instance of :class:`~ClusterJob`

        """
        return ClusterJob(self.queueing, self.batch_template, job_name=job_name,
                          work_dir=os.path.join(self.root_dir, work_dir))


def delayed_submission(cluster_job, await_true, interval=2):
    """Delay the submission of a job until :code:`await_true()` returns True.

    Args:
        cluster_job (:class:`~ClusterJob`): The job.
        await_true (:obj:`function`): A function that returns a boolean.
        interval (int): Interval (in seconds) to call the function await_true.

    Returns:
        int: Job id.
    """
    while not await_true():
        time.sleep(interval)
    return cluster_job.submit()


def async_delayed_submission(cluster_job, await_true, interval=2):
    """Delay the submission of a job until :code:`await_true()` returns True,
    run in a background process, allowing the main thread to continue.

    Args:
        cluster_job (:class:`~ClusterJob`): The job.
        await_true (:obj:`function`): A function that returns a boolean.
        interval (int): Interval (in seconds) to call the function await_true.

    Returns:
        :class:`multiprocessing.Process`: The forked thread.
    """
    p = multiprocessing.Process(
        target=delayed_submission,
        args=(cluster_job, await_true),
        kwargs={"interval":interval}
    )
    p.start()
    return p
