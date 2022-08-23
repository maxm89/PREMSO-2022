# -*- coding: utf-8 -*-

"""Tests for coffe.core.cluster"""

from __future__ import absolute_import, division, print_function

import os
import time

import pytest

from coffe.core import cluster, pkgdata, thirdparty, filesys, shell
from coffe.gmx.sim import GmxCalculation


#  ==============================
#       Failure tests
#  ==============================


def test_cluster_invalid_queueing(tmpdir):
    with pytest.raises(AssertionError):
        c = cluster.ClusterJob("slkjsd",
                               pkgdata.abspath("data/batch_torque.sh"),
                               work_dir=str(tmpdir)
                               )


def test_cluster_invalid_script(tmpdir):
    with pytest.raises(AssertionError):
        c = cluster.ClusterJob("torque",
                               pkgdata.abspath("data/asdflkj.sh"),
                               work_dir=str(tmpdir)
                               )


@pytest.mark.skipif(not thirdparty.TORQUE.exists,
                    reason="requires torque")
def test_cluster_slurm_script_for_torque(tmpdir):
    with pytest.raises(cluster.ClusterError):
        c = cluster.ClusterJob("torque",
                               pkgdata.abspath("data/batch_slurm.sh"),
                               work_dir=str(tmpdir)
                               )


@pytest.mark.skipif(not thirdparty.SLURM.exists,
                    reason="requires slurm")
def test_cluster_torque_script_for_slurm(tmpdir):
    with pytest.raises(cluster.ClusterError):
        c = cluster.ClusterJob("slurm",
                               pkgdata.abspath("data/batch_torque.sh"),
                               work_dir=str(tmpdir)
                               )


#  ==============================
#       Shared tests
#  ==============================

@pytest.fixture(params=[
    (None, None), # the third item is a "hint command".
                        # If this command exists, the relevant tests will be executed.
    ("torque", "data/batch_torque.sh"),
    ("slurm", "data/batch_slurm.sh"),
])
def all_queues(request, tmpdir):
    """Run test for all queueing systems.
    Returns:  cluster instance, tmpdir
    """
    def wrapper():
        queueing, script = request.param
        if script is not None:
            script = pkgdata.abspath(script)
        if queueing == "torque" and not thirdparty.TORQUE.exists:
            pytest.skip("Torque does not work on your system".format(queueing))
        if queueing == "slurm" and not thirdparty.SLURM.exists:
            pytest.skip("Slurm does not work on your system".format(queueing))
        return queueing, script, str(tmpdir)
    return wrapper


@pytest.fixture()
def job_all_queues(all_queues):
    def wrapper(jobname=None):
        queueing, script, tmp = all_queues()
        return cluster.ClusterJob(queueing, script, jobname, tmp), tmp
    return wrapper


def test_construction(job_all_queues):
    """Construction via fixture"""
    job_all_queues()


def test_reconstruction_after_error(job_all_queues):
    c, tmp = job_all_queues()
    c.status = 1
    c.status = cluster.Status.error
    c2 = cluster.ClusterJob(c.queueing, c.batch_template, c.job_name, tmp)
    assert c2.status == cluster.Status.not_written


def test_reconstruction_active(job_all_queues):
    c, tmp = job_all_queues()
    if c.queueing is None:
        return  # in this case, the process cannot be tracked by future processes
    c += "sleep 5"
    c.submit()
    c2 = cluster.ClusterJob(c.queueing, c.batch_template, c.job_name, tmp)
    assert c2.status in [cluster.Status.queueing, cluster.Status.running]
    c2.kill()


def test_failure_readd(job_all_queues):
    c, tmp = job_all_queues()
    c += "sleep 5"
    c.submit()
    # job is now queueing or running
    with pytest.raises(cluster.ClusterError):
        c += "other"
    c.kill()


def test_failure_rewrite(job_all_queues):
    c, tmp = job_all_queues()
    c += "sleep 5"
    c.submit()
    # job is now queueing or running
    with pytest.raises(cluster.ClusterError):
        c.write_script()
    c.kill()


def test_failure_resubmit(job_all_queues):
    c, tmp = job_all_queues()
    c += "sleep 5"
    c.submit()
    # job is now queueing or running
    with pytest.raises(cluster.ClusterError):
        c.submit()
    c.kill()


def test_empty_write(job_all_queues):
    c, tmp = job_all_queues()
    script_name = c.write_script()
    assert os.path.isfile(script_name)
    with open(script_name, "r") as new:
        assert new.read() != ""


@pytest.fixture()
def touch_test(job_all_queues):
    def wrapper(job_name=None):
        c, tmp = job_all_queues(job_name)
        c += "cd {}".format(tmp)
        c += "touch test.txt"
        return c, tmp
    return wrapper


def test_reconstruct_completed(touch_test):
    c, tmp = touch_test()
    # artificial completion
    with open(c.status_file, "w") as f:
        f.write("completed 1")
    c2 = cluster.ClusterJob(c.queueing, c.batch_template, c.job_name, c.work_dir)
    assert c2.status == cluster.Status.completed


def test_add_string_cmd(touch_test):
    c, _ = touch_test()
    script= c.write_script()
    with open(script, "r") as f:
        assert "touch test.txt" in f.read()
    assert c.commands


def test_jobname(touch_test):
    c, _ = touch_test("my_job")
    script= c.write_script()
    job_line = filesys.grep_line(script, cluster.JOBNAME_OPTION[c.queueing])
    assert "my_job" in job_line


def test_add_failure(touch_test):
    c, _ = touch_test()
    c.write_script()
    with pytest.raises(cluster.ClusterError):
        c += " "


def test_write_twice_failure(touch_test):
    c, _ = touch_test()
    c.write_script()
    with pytest.raises(cluster.ClusterError):
        c.write_script()


def test_clear(touch_test):
    c, _ = touch_test()
    c.clear()
    assert not c.commands


def test_submit(touch_test):
    c, tmp = touch_test()
    jobid = c.submit()
    assert isinstance(jobid, int) and jobid > 0
    assert c.status in [cluster.Status.queueing,
                        cluster.Status.running,
                        cluster.Status.completed]
    if c.status == cluster.Status.completed:
        assert os.path.isfile(os.path.join(tmp, "test.txt"))


def test_submit_failure(touch_test):
    c, tmp = touch_test()
    c += "aslkhg"
    if c.queueing is None:
        c.submit()
        c.local_process.join()
        assert c.status == cluster.Status.error


def test_kill(job_all_queues):
    c, tmp = job_all_queues()
    c += "sleep 10"
    c.submit()
    c.kill()
    assert c.status == cluster.Status.error


def test_status(job_all_queues):
    c, tmp = job_all_queues()
    assert c.status == "not_written"
    c += "sleep 2"
    c.write_script()
    assert c.status == "not_submitted"
    c.submit()
    assert c.status in [cluster.Status.queueing,
                        cluster.Status.running]
    c.kill()
    assert c.status in [cluster.Status.completed, cluster.Status.error]


def test_local_job_async(tmpdir):
    testfile = os.path.join(str(tmpdir), "test.txt")
    initfile = os.path.join(str(tmpdir), "initiate.txt")
    c = cluster.ClusterJob(None, None, "noname", work_dir=str(tmpdir))
    c += ("while ! [ -e {} ]; do sleep 0.1; " 
          "done; touch {};".format(initfile, testfile))
    c.submit()
    assert not os.path.exists(testfile)
    time.sleep(0.2)
    assert not os.path.exists(testfile)
    shell.touch(initfile)
    c.local_process.join()
    assert os.path.exists(testfile)

# === Tests with simulation classes (only local) ===


@pytest.fixture
def make_gmxsim(tmpdir):
    def mksim():
        s = pkgdata.abspath("../gmx/data/test_structure.pdb")
        t = pkgdata.abspath("../gmx/data/test_topology.top")
        mdp = pkgdata.abspath("../gmx/data/test_mdp.mdp")
        wd = os.path.join(str(tmpdir), "test_sim")
        return GmxCalculation(s, t, mdp, wd)
    return mksim


@pytest.mark.skipif(not thirdparty.GROMACS.exists,
                    reason="requires gmx")
def test_add_callable_class(make_gmxsim):
    sim = make_gmxsim()
    c = cluster.ClusterJob(work_dir=sim.work_dir)
    c += sim
    assert len(c.commands) == 1


@pytest.mark.skipif(not thirdparty.GROMACS.exists,
                    reason="requires gmx")
def test_submit_callable_class(make_gmxsim):
    sim = make_gmxsim()
    c = cluster.ClusterJob(work_dir=sim.work_dir)
    c += sim
    c.submit()
    c.local_process.join()
    assert os.path.isfile(os.path.join(sim.work_dir, "confout.gro"))


# === Test generator ===


def test_job_generator(all_queues):
    queueing, script, tmp = all_queues()
    gen = cluster.ClusterJobGenerator(queueing, script, tmp)
    job = gen.generate_job(tmp, "job_name")
    assert job.job_name == "job_name"
    assert job.work_dir == tmp


# === Test delayed submission ===

def test_async_delayed_submission(tmpdir):
    testfile = os.path.join(str(tmpdir), "test.txt")
    initfile = os.path.join(str(tmpdir), "initiate.txt")
    c = cluster.ClusterJob(None, None, "noname", work_dir=str(tmpdir))
    c += "touch {}".format(testfile)
    await_true = lambda: os.path.exists(initfile)
    p = cluster.async_delayed_submission(c, await_true, interval=0.1)
    assert not os.path.exists(testfile)
    time.sleep(0.5)
    assert not os.path.exists(testfile)
    shell.touch(initfile)
    p.join()
    assert os.path.exists(testfile)
