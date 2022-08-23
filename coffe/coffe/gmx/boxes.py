# -*- coding: utf-8 -*-

"""Tools for setting up simulation boxes in Gromacs"""

from __future__ import absolute_import, division, print_function

from coffe.core.decorators import args_from_configfile
import coffe.gmx.util as gmxutil
from coffe.core import coffedir
from coffe.misc import util

import os


@args_from_configfile
def gmx_mkbox_homogeneous(substance, n_mols=None, box_size=None, density=None,
                          m_mol=None, ff_dir=None, gmx_ff=None,
                          create_itp=True, include_topology=None, work_dir=".",
                          substance_name=None, box_name=None,
                          confout="out.gro"):
    """Make a homogeneous box of one or more substances.

    Args:
        substance(str or list of str): Input structure file containing a single molecule.
        n_mols(int or list of ints): Number of molecules.
        box_size(float or list of 3 floats): Box size in nm
        density(float or list of floats): density of the substances in kg/m³
        m_mol(float or list of floats): molar mass in g/mol

        (Instead of using the number of molecules and the box size
        only one of these arguments can be used with the density and molar mass)

        ff_dir(str): (Optional) Forcefield directory.
        gmx_ff(str): (Optional) Forcefield name of Gromacs' built-in force field.
        create_itp(bool): Flag to call pdb2gmx, if include_topology is not given (default: True).
        include_topology(str): (Optional) Include topology.
        work_dir(str): Working directory (default=".").
        substance_name(str): Name of the substance (default="substance").
        box_name(str): Name for the system (default="box").
        confout(str): Name of output structure file (default="out.gro").

    Returns:
        structure(str): Structure file.
        topology(str): Topology file.
    """

    with coffedir.CoffeWorkDir(work_dir, "Creating a homogeneous box",
                               locals()) as cwd:
        # Make sure variables are lists od the same length
        if isinstance(substance, str):
            substance = [substance]
        if isinstance(n_mols, int):
            n_mols = [n_mols]
        if isinstance(density, (int, float)):
            density = [density]
        if isinstance(m_mol, (int, float)):
            m_mol = [m_mol]
        if isinstance(substance_name, str):
            substance_name=[substance_name]
        if n_mols is not None and len(n_mols) is not len(substance):
            raise ValueError("Number of molecules needed for all substances")
        if density is not None and box_size is not None and len(density) is not len(substance):
            raise ValueError("Density  needed for all substances")
        if density is not None and box_size is not None and len(density) is not len(m_mol):
            raise ValueError("Molecular mass m_mol needed for all substances")
        if m_mol is not None and len(m_mol) is not len(substance):
            raise ValueError("Molecular mass m_mol needed for all substances")
        if m_mol is not None and box_size is not None and len(m_mol) is not len(density):
            raise ValueError("Density needed for all substances")
        if substance_name is not None and len(substance_name) is not len(
            substance):
            raise ValueError("For every substance there needs to be a name!")
        if substance_name is None:
            substance_name = substance
        substance_name=[os.path.basename(sub_name) for sub_name in substance_name]
        if box_name is None:
            box_name = "-".join(substance_name)

        if box_size is None and n_mols is not None:
            box_size, n = util.compute_box_size(n_mols, density, m_mol)
            if n is not None:
                n_mols = n

        if n_mols is None and box_size is not None:
            n_mols = util.compute_n_mols(box_size, density, m_mol)

        if include_topology is not None:
            include_topology = cwd.abspath(include_topology,
            check_exists=False)
        if ff_dir is not None:
            ff_dir = cwd.abspath(ff_dir)
        # Create itp
        # TODO(AK) enable usage of top files
        itp_list = [include_topology]
        if include_topology is None:
            itp_list=[]
            if create_itp:
                for sub,sub_name in zip(substance,substance_name):
                    itp = os.path.join(cwd.work_dir, sub_name+".itp")
                    itp, ff_itp = gmxutil.gmx_pdb2itp(sub, itp, ff_dir,
                                                      gmx_ff, cwd.work_dir)
                    gmxutil.rename_substance_in_itp(itp, sub_name)
                    itp_list.append(itp)
        else:
            ff_itp = os.path.join("{}.ff".format(gmx_ff), "forcefield.itp")
        # Create box
        if not isinstance(box_size, list):
            box_size = [box_size] * 3
        structure = cwd.abspath(confout, check_exists=False)
        gmxutil.gmx_insert_n_molecules(box_size, substance[0], n_mols[0], structure, cwd.work_dir)
        if len(substance)>1:
            for sub,n in zip(substance[1:],n_mols[1:]):
                gmxutil.gmx_insert_n_molecules(structure, sub, n, structure, cwd.work_dir)


        # Create topology
        topology = gmxutil.gmx_make_top(substance_name, n_mols, itp_list,
                                        os.path.dirname(ff_itp), cwd.work_dir,
                                        box_name)
        cwd.logger.info("Homogeneous system created successfully.")
        cwd.logger.info(".... Structure file: {}".format(structure))
        cwd.logger.info(".... Topology file: {}".format(topology))
        return os.path.abspath(structure), os.path.abspath(topology)


@args_from_configfile
def gmx_mkbox_twophase(substance, density_v=None, density_l=None, n_mols_v=None,
                       n_mols_l=None, box_size=None, m_mol=None, ff_dir=None,
                       gmx_ff=None, create_itp=True, include_topology=None,
                       work_dir=".", substance_name=None, box_name="box",
                       confout="out.gro"):
    """Make a box that contains two phases with molecules of a single species.

    Args:
        substance: Input structure file containing a single molecule.
        density_v: (partial) densities of substances in vapor phase
        density_l: (partial) densities of substances in liquid phase
        n_mols_v: Number of molecules in the in each vapor phase
        n_mols_l: Number of molecules in the liquid phase
        box_size: Liquid box size in nm, box will be surrounded by two vapor
        boxes of same size.
        m_mol: Molecular masses of substances
        ff_dir: (Optional) Forcefield directory.
        gmx_ff: (Optional) Forcefield name of Gromacs' built-in force field.
        create_itp: Flag to call pdb2gmx, if include_topology is not given (default: True).
        include_topology: (Optional) Include topology.
        work_dir: Working directory (default=".").
        substance_name: Name of the substance (default="substance").
        box_name: Name for the system (default="box").
        confout: Name of output structure file (default="out.gro").

    Returns:
        structure(str): Structure file.
        topology(str): Topology file.

    """

    with coffedir.CoffeWorkDir(work_dir, "Creating a two-phase box", locals()) as cwd:
        _substance = []
        # Make sure variables are lists od the same length
        if isinstance(substance, str):
            substance = [substance]
        if isinstance(n_mols_v, (int, float)):
            n_mols_v = [n_mols_v]
        if isinstance(n_mols_l, (int, float)):
            n_mols_l = [n_mols_l]
        if isinstance(density_v, (int, float)):
            density_v = [density_v]
        if isinstance(density_l, (int, float)):
            density_l = [density_l]
        if isinstance(m_mol, (int, float)):
            m_mol = [m_mol]
        if isinstance(substance_name, str):
            substance_name=[substance_name]
        if isinstance(box_size, (int, float)):
            box_size = [box_size] * 3
        if box_size is not None and len(box_size) is not 3:
            raise ValueError("box_size must be one coordinate or list of "
                             "three coordinates!")
        if n_mols_v is not None and len(n_mols_v) is not len(substance):
            raise ValueError("For every substance there needs to be a number "
                             "of molecules!")
        if n_mols_l is not None and len(n_mols_l) is not len(substance):
            raise ValueError("For every substance there needs to be a number "
                             "of molecules!")
        if density_v is not None and len(density_v) is not len(substance):
            raise ValueError("Density  needed for all substances")
        if density_v is not None and len(density_v) is not len(m_mol):
            raise ValueError("Molecular mass m_mol needed for all substances")
        if density_l is not None and len(density_l) is not len(substance):
            raise ValueError("Density  needed for all substances")
        if density_l is not None and len(density_l) is not len(m_mol):
            raise ValueError("Molecular mass m_mol needed for all substances")
        if m_mol is not None and len(m_mol) is not len(substance):
            raise ValueError("Molecular mass m_mol needed for all substances")
        if m_mol is not None and len(m_mol) is not len(density_v):
            raise ValueError("Density needed for all substances")
        if substance_name is not None and len(substance_name) is not len(
            substance):
            raise ValueError("For every substance there needs to be a name!")
        if substance_name is None:
            substance_name = substance
        substance_name=[os.path.basename(sub_name) for sub_name in substance_name]
        if box_name is None:
            box_name = "-".join(substance_name)

        # TODO: create box with density and n_mols

        if n_mols_v is None and box_size is not None:
            n_mols_v = util.compute_n_mols(box_size, density_v, m_mol)

        if n_mols_l is None and box_size is not None:
            n_mols_l = util.compute_n_mols(box_size, density_l, m_mol)

        if include_topology is not None:
            include_topology = cwd.abspath(include_topology, check_exists=False)
        if ff_dir is not None:
            ff_dir = cwd.abspath(ff_dir)

        # Create itp
        itp_list = [include_topology]
        if include_topology is None:
            itp_list = []
            if create_itp:
                for sub, sub_name in zip(substance, substance_name):
                    itp = os.path.join(cwd.work_dir, sub_name + ".itp")
                    itp, ff_itp = gmxutil.gmx_pdb2itp(sub, itp, ff_dir,
                                                      gmx_ff, cwd.work_dir)
                    gmxutil.rename_substance_in_itp(itp, sub_name)
                    itp_list.append(itp)
        else:
            ff_itp = os.path.join("{}.ff".format(gmx_ff), "forcefield.itp")

        structure_v = cwd.abspath("conf_v.gro", check_exists=False)
        gmxutil.gmx_insert_n_molecules(box_size, substance[0], n_mols_v[0],
                                       structure_v, cwd.work_dir)
        if len(substance) > 1:
            for sub, n in zip(substance[1:], n_mols_v[1:]):
                gmxutil.gmx_insert_n_molecules(structure_v, sub, n,
                                               structure_v, cwd.work_dir)

        structure_l = cwd.abspath("conf_l.gro", check_exists=False)
        gmxutil.gmx_insert_n_molecules(box_size, substance[0], n_mols_l[0],
                                       structure_l, cwd.work_dir)
        if len(substance) > 1:
            for sub, n in zip(substance[1:], n_mols_l[1:]):
                gmxutil.gmx_insert_n_molecules(structure_l, sub, n,
                                               structure_l, cwd.work_dir)

        # double the vapor box
        conf_vapor = gmxutil.gmx_genconf(structure_v, n_box=[1, 1, 2],
                                         dist = [0, 0,box_size[0]],
                                         work_dir=work_dir,
                                         confout="conf_v_doubled.gro")

        # read the vapor box
        with open(conf_vapor, "r") as vapor_file:
            vapor_lines = vapor_file.readlines()
            vapor_len = len(vapor_lines)
            vapor_n_atoms = int(vapor_lines[1])

        # translate the liquid box and renumber residues
        conf_liquid = gmxutil.gmx_editconf(
            initial_structure=structure_l, box_resize=True,
            box_size=[box_size[0], box_size[1], 3 * box_size[2]],
            trans=[0, 0, box_size[0]], renumber=sum(n_mols_v) * 2 + 1,
            work_dir=work_dir, confout="conf_l_translated_renumbered.gro")

        # read the liquid box
        with open(conf_liquid, "r") as liquid_file:
            liquid_lines = liquid_file.readlines()
            liquid_len = len(liquid_lines)
            liquid_n_atoms = int(liquid_lines[1])

        # Combine both boxes
        n_atoms_combined = liquid_n_atoms + vapor_n_atoms
        conf_combined = str(os.path.dirname(structure_l)) + "/conf_combined.gro"
        combined_file = open(conf_combined, "w")
        combined_file.write(vapor_lines[0])
        combined_file.write(str(n_atoms_combined) + "\n")

        for i in range(2, vapor_len - 1):
            combined_file.write(vapor_lines[i])

        for i in range(2, liquid_len):
            combined_file.write(liquid_lines[i])

        combined_file.close()

        # renumber the combined box
        twophase_file = gmxutil.gmx_editconf(
            initial_structure=combined_file.name, confout=confout, renumber=1,
            work_dir=work_dir)

        # Create topology
        n_mols_all=[]
        substance_top=[]
        itp_top=[]
        if len(substance_name)>1:
            for sub_name, n_v,i in zip(substance_name, n_mols_v, itp_list):
                substance_top.append(sub_name)
                n_mols_all.append(n_v)
                itp_top.append(i)
            for sub_name, n_v, i in zip(substance_name, n_mols_v, itp_list):
                substance_top.append(sub_name)
                n_mols_all.append(n_v)
            for sub_name, n_l, i in zip(substance_name, n_mols_l, itp_list):
                substance_top.append(sub_name)
                n_mols_all.append(n_l)

        else:
            substance_top.append(substance_name[0])
            n_mols_all.append(2*n_mols_v[0]+n_mols_l[0])
            itp_top.append(itp_list[0])

        topology = gmxutil.gmx_make_top(substance_top,
                                        n_mols_all, itp_top,
                                        os.path.dirname(ff_itp), cwd.work_dir,
                                        box_name)
        cwd.logger.info("Two-phase system created successfully.")
        cwd.logger.info(".... Structure file: {}".format(twophase_file))
        cwd.logger.info(".... Topology file: {}".format(topology))
        os.remove(combined_file.name)
        os.remove(conf_vapor)
        os.remove(conf_liquid)
        os.remove(structure_l)
        os.remove(structure_v)
        return os.path.abspath(twophase_file), os.path.abspath(topology)


@args_from_configfile
def gmx_mkbox_solvation():
    # TODO(AK) create box to calculate free energies of solvation
    raise NotImplementedError()


# === High-level interface ===

ALLOWED_BOX_TYPES = ["homogeneous", "twophase", "solvation"]


@args_from_configfile
def gmx_mkbox(boxtype=None, *args, **kwargs):
    assert boxtype in ALLOWED_BOX_TYPES,\
        "boxtype {} is not in allowed boxtypes {}"\
            .format(boxtype, ", ".join(ALLOWED_BOX_TYPES))
    if boxtype == "homogeneous":
        return gmx_mkbox_homogeneous(*args, **kwargs)
    elif boxtype == "twophase":
        return gmx_mkbox_twophase(*args, **kwargs)
    elif boxtype == "solvation":
        return gmx_mkbox_solvation(*args, **kwargs)
    else:
        raise NotImplementedError()
