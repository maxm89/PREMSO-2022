# -*- coding: utf-8 -*-

"""Utility and helper functions for Gromacs"""

from __future__ import absolute_import, division, print_function

from coffe.core.globconf import CONFIG
from coffe.core import filesys, coffedir, shell
import os
import numpy as np
import pandas as pd
import shutil
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit


def read_xvg(xvg):
    """Read xvg file and return a numpy array."""
    assert os.path.isfile(xvg)
    return np.loadtxt(xvg, comments=["#", "@"])


def gmx_calc_energy(work_dir=".", terms=["Potential"], out="energy.xvg"):
    with coffedir.CoffeWorkDir(work_dir, "gmx_calc_energy", locals()) as cwd:
        stdin = os.linesep.join(terms) + os.linesep
        cmd = "{} energy -o {}".format(CONFIG.gmx, out)
        cwd.call_cmd(cmd, stdin_string=stdin)
        return read_xvg(os.path.join(cwd.work_dir, out))


def get_density_xvg(traj, topol, terms="0", first_frame=0, last_frame=0,
                    dens="mass", out="density.xvg", work_dir="."):
    """Creates a density profile xvg for the system

    Args:
        traj: (.trr, .xtc, .gro) trajectory file of the system
        topol: (.tpr) binary topology-File
        terms:
        first_frame: (optional, ps) first time frame to read from trajectory
        last_frame: (optional, ps) last time frame to read from trajectory
        dens:
        out: (optional, string) output name for the density diagram
        work_dir: optional) working directory

    Returns:
        returns the the density profile xvg
    """

    with coffedir.CoffeWorkDir(work_dir, "Creating a density xvg-file",
                               locals()) as cwd:
        assert traj[-3:] == "trr" or traj[-3:] == "xtc" or traj[
                                                           -3:] == "gro", "Check Trajectory Input."
        assert topol[-3:] == "tpr", "Check Topology Input"
        assert dens == "mass" or dens == "number" or dens == "charge", "Check Density Type Input!"
        cmd = "gmx density -f {} -s {} -o {} -dens {}".format(traj, topol, out,
                                                              dens)
        if first_frame != 0:
            cmd += " -b {}".format(first_frame)
        if last_frame != 0:
            cmd += " -e {}".format(last_frame)
        stdin = os.linesep.join(terms) + os.linesep
        cwd.call_cmd(cmd, stdin_string=stdin)
        density = cwd.abspath(out, check_exists=False)
        return density


def split_density(density, split_marker=0):
    """Reads the density.xvg file or the data array and splits it in its centre of mass. If split_marker is not zero, the strucure gets cut
    at the split marker (in %) and then splits the structure in its centre of mass.
    Arguments:
        density:                        -- (.xvg or np.array) density plot or numpy array which is being analyzed
        split_marker (in %):            -- (optional) indicates where the structure is split and moved
    Returns:                            two np.array containing the left and right side of the centre of mass
       """

    if isinstance(density, str):
        data = read_xvg(density)
    else:
        data = density
    if split_marker == 0:
        multi = np.multiply(data[:, 0], data[:, 1])
        summed = sum(multi)
        x_split = summed / sum(data[:, 1])
        delta_x = abs(np.subtract(data[:, 0], x_split))
        i = np.argmin(delta_x)
        data_l = data[:i, :]
        data_r = data[i:, :]

    else:
        assert split_marker > 0 and split_marker < 100
        frac = split_marker / 100
        i = np.int(np.floor(len(data[:, 0]) * frac))
        x_i = data[i, 0]
        data_l = data[:i, :]
        data_l[:, 0] += (data[-1, 0] - x_i)
        data_r = data[i:, :]
        data_r[:, 0] -= x_i
        data = np.vstack((data_r, data_l))
        multi = np.multiply(data[:, 0], data[:, 1])
        x_split = sum(multi) / sum(data[:, 1])
        delta_x = abs(np.subtract(data[:, 0], x_split))
        i = np.argmin(delta_x)
        data_l = data[:i, :]
        data_r = data[i:, :]
    return data_l, data_r, np.float(x_split / data_r[0, -1] * 100)


def gmx_density_fit(density_xvg, dens="mass", show_plot=True, work_dir="."):
    """Creates a density diagram for the system
    Edits the input structure
    Arguments:
        density_xvg:                    -- (.xvg) density plot which is being analyzed
        work_dir:                       -- (optional) working directory
    Returns:                            returns liquid and vapor densities as well as the interface width
       """
    with coffedir.CoffeWorkDir(work_dir, "Creating a curve fit",
                               locals()) as cwd:
        def func_l(z, rho_1, rho_2, z_0, D):
            return (rho_1 - rho_2) / 2 * np.tanh((z - z_0) / D) + (
                rho_1 + rho_2) / 2

        def func_r(z, rho_1, rho_2, z_0, D):
            return -(rho_1 - rho_2) / 2 * np.tanh((z - z_0) / D) + (
                rho_1 + rho_2) / 2

        unit = "[m/kg3]"
        if dens == "number":
            unit = "[1/nm3]"
        elif dens == "charge":
            unit = "[e/nm3]"

        def fitting(data_l, data_r):
            popt_l, pcov_l = curve_fit(func_l, data_l[:, 0], data_l[:, 1])
            popt_r, pcov_r = curve_fit(func_r, data_r[:, 0], data_r[:, 1],
                                       bounds=(
                                           [popt_l[0] * 0.7, popt_l[1] * 0.7,
                                            data_l[0, 0], 0],
                                           [popt_l[0] * 1.3, popt_l[1] * 1.3,
                                            data_r[-1, 0], np.inf]))
            return popt_l, pcov_l, popt_r, pcov_r

        try:
            data_l, data_r, split_out = split_density(density_xvg)
            popt_l, pcov_l, popt_r, pcov_r = fitting(data_l, data_r)

        except shell.ShellError:
            data_l, data_r, split_out = split_density(density_xvg, 33)
            popt_l, pcov_l, popt_r, pcov_r = fitting(data_l, data_r)

        if abs(popt_l[0] - popt_r[0]) >= 0.3 * popt_l[0] or abs(
            (popt_l[1] - popt_r[1]) >= 0.3 * popt_l[1]) or abs(
            popt_l[2] - popt_r[2]) < 0.1 * popt_l[2] or (
            popt_l[1] + popt_r[1]) / 2 > (popt_l[0] + popt_r[0]) / 2:
            data_l, data_r, split_out = split_density(density_xvg, 33)
            popt_l, pcov_l, popt_r, pcov_r = fitting(data_l, data_r)

        if popt_l[2] > popt_r[2]:
            data_l, data_r, split_out = split_density(
                np.vstack((data_l, data_r)), (popt_l[2] + popt_r[2]) / 2)
            popt_l, pcov_l, popt_r, pcov_r = fitting(data_l, data_r)

        z_mid = (popt_r[2] + popt_l[2]) / 2
        z_max = data_r[-1, 0]
        split_pos = (z_mid / z_max) * 100

        if 100 > split_pos > 50:
            data_l, data_r, split_out = split_density(
                np.vstack((data_l, data_r)), split_pos - 50)
            popt_l, pcov_l, popt_r, pcov_r = fitting(data_l, data_r)

        elif 0 < split_pos < 50:
            data_l, data_r, split_out = split_density(
                np.vstack((data_l, data_r)), split_pos + 50)
            popt_l, pcov_l, popt_r, pcov_r = fitting(data_l, data_r)

        plt.clf()
        plt.xlabel('z [nm]')
        plt.ylabel('Density {}'.format(unit))
        plt.plot(data_l[:, 0], data_l[:, 1], 'b-', label='left side')
        plt.plot(data_l[:, 0], func_l(data_l[:, 0], *popt_l), 'r-',
                 label='fit_l: rho_1=%5.3f, rho_2=%5.3f, z_0=%5.3f, D=%5.3f' % tuple(
                     popt_l))
        plt.plot(data_r[:, 0], data_r[:, 1], 'b-', label='right side')
        plt.plot(data_r[:, 0], func_r(data_r[:, 0], *popt_r), 'r-',
                 label='fit_r: rho_1=%5.3f, rho_2=%5.3f, z_0=%5.3f, D=%5.3f' % tuple(
                     popt_r))
        plt.legend()
        if show_plot == True:
            plt.show()
        else:
            plt.savefig("{}/density_fit.png".format(work_dir))

        rho_l = (popt_l[0] + popt_r[0]) / 2
        rho_v = (popt_l[1] + popt_r[1]) / 2
        D = (popt_l[3] + popt_r[3]) / 2
        z_l = popt_l[2]
        z_r = popt_r[2]
        if rho_l < rho_v:
            print(
                "Warning: Edge Density > Middle Density. Make sure that the denser phase is near the center of the box!")
        return rho_l, rho_v, D, z_l, z_r, np.vstack(
            (data_l, data_r)), popt_l, popt_r, split_out


def get_densities(traj, topol, n_substances=1, first_frame=0, last_frame=0,
                  dens="mass", show_plot=True, out="density.xvg", work_dir="."):
    """ creates a density fit for two phase systems from gromacs files
    Arguments:
        traj:                           -- (.trr, .xtc, .gro) trajectory file of the system
        topol:                          -- (.tpr) binary topology-File
        first_frame:                    -- (optional, ps) first time frame to read from trajectory
        last_frame:                     -- (optional, ps) last time frame to read from trajectory
        out:                            -- (optional, string) output name for the density diagram
        work_dir:                       -- (optional) working directory
    Returns:                            returns liquid and vapor densities as well as the interface width
    """
    with coffedir.CoffeWorkDir(work_dir,
                               "Getting Densities from gromacs files...",
                               locals()) as cwd:
        assert n_substances > 0, "There must be at least one substance!"

        def get_df_data(data):
            z_mid_dens = []
            z_edge_dens = []
            index = 0
            z_ll = z_l + (z_r - z_l) * 0.15
            z_rr = z_r - (z_r - z_l) * 0.15
            for x in data[:, 0]:
                if x >= z_ll and x <= z_rr:
                    z_mid_dens.append(data[index, 1])
                elif x <= z_ll or x >= z_rr:
                    z_edge_dens.append(data[index, 1])
                index += 1

            if len(z_mid_dens) > 1 and len(z_edge_dens) > 1:
                density_mid = sum(z_mid_dens) / len(z_mid_dens)
                density_edge = sum(z_edge_dens) / len(z_edge_dens)
            else:
                density_mid = rho_l
                density_edge = rho_v
            density_max = np.amax(data[:, 1])
            z_max = data[np.argmax(data[:, 1]), 0]
            density_min = np.amin(data[:, 1])
            z_min = data[np.argmin(data[:, 1]), 0]
            dfdata = {"Middle Density [{}]".format(unit): [density_mid],
                      "Edge Density [{}]".format(unit): [density_edge],
                      "Maximum Density [{}]".format(unit): [density_max],
                      "z|max. Dens [nm]": [z_max],
                      "Minimum Density [{}]".format(unit): [density_min],
                      "z|min. Dens [nm]": [z_min]}
            return dfdata

        unit = "[kg/m3]"
        if dens == "number":
            unit = "[1/nm³]"
        elif dens == "charge":
            unit = "[e/nm3]"

        if n_substances == 1:
            density_xvg = get_density_xvg(traj, topol, "0", first_frame,
                                          last_frame, dens, out, work_dir)
            rho_l, rho_v, D, z_l, z_r, data, popt_l, popt_r, split_out = \
                gmx_density_fit(density_xvg, dens, show_plot, work_dir)
            dfdata = get_df_data(data)
            df = pd.DataFrame(dfdata, index=["System"])
            return rho_l, rho_v, D, z_l, z_r, df

        elif n_substances > 1:
            density_xvg = get_density_xvg(traj, topol, "0", first_frame,
                                          last_frame, dens,
                                          out="density_system.xvg",
                                          work_dir=work_dir)  # System Density
            rho_l, rho_v, D, z_l, z_r, data, popt_l, popt_r, split_out = \
                gmx_density_fit(density_xvg, dens, show_plot, work_dir)
            dfdata = get_df_data(data)
            df = pd.DataFrame(dfdata, index=["System"])

            for i in range(n_substances):
                rho_temp = get_density_xvg(traj, topol, "{}".format(i + 2),
                                           first_frame, last_frame, dens,
                                           out="density_substance_{}.xvg".format(
                                               i + 1), work_dir=work_dir)
                rho_temp2 = cwd.abspath("rho_temp.xvg", check_exists=False)
                shutil.copy(rho_temp, rho_temp2)
                data_l, data_r, split_out = split_density(rho_temp2, split_out)
                dfdata = get_df_data(np.vstack((data_l, data_r)))
                df = df.append(
                    pd.DataFrame(dfdata, index=["Substance {}".format(i + 1)]))
                os.remove(rho_temp2)
        df_csv = df.to_csv(work_dir + "dataframe.csv")
        return rho_l, rho_v, D, z_l, z_r, df, popt_l, popt_r
