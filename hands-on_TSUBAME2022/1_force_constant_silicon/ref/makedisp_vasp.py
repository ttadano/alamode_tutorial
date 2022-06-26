from pymatgen.core import Structure
from pymatgen.io.vasp import inputs
from pymatgen.core.periodic_table import get_el_sp
import numpy as np
import os
import collections
import sys

scaling_matrix = [[-2, 2, 2],
                  [ 2,-2, 2],
                  [ 2, 2,-2]]

Bohr = 0.52917721067
POSCARname = "primitive.POSCAR.vasp"
prefix = "si222"
prefix_poscar = "harm_0.01_"
disp_magnitude_angstrom = 0.01
#vasp_command = "~/bin/vasp_std_O1"
ALAMODE_root = "~/src/alamode"


def gen_kpoints_file(structure):

    kmesh = inputs.Kpoints.automatic_density_by_vol(structure, 450)
    kmesh.write_file(filename="KPOINTS")


def gen_supercell_poscar(structure):

    with open("SPOSCAR", 'w') as f:
        f.write("%s\n" % structure.formula)
        f.write("1.000\n")
        for i in range(3):
            for j in range(3):
                f.write("%20.13f" % structure.lattice.matrix[i][j])
            f.write("\n")
        atomic_numbers_uniq = list(
            collections.OrderedDict.fromkeys(structure.atomic_numbers))
        num_species = []
        for num in atomic_numbers_uniq:
            f.write("%s " % get_el_sp(num))
            nspec = len(np.where(np.array(structure.atomic_numbers) == num)[0])
            num_species.append(nspec)
        f.write("\n")
        for elem in num_species:
            f.write("%i " % elem)
        f.write("\n")
        f.write("Direct\n")
        for i in range(len(structure.frac_coords)):
            f.write("%20.14f " % structure.frac_coords[i][0])
            f.write("%20.14f " % structure.frac_coords[i][1])
            f.write("%20.14f\n" % structure.frac_coords[i][2])


def gen_species_dictionary(structure):

    species_dict = {}
    counter = 1
    for elem in structure.types_of_specie:
        species_dict[elem.value] = counter
        counter += 1
    return species_dict


def gen_species_dictionary2(atomic_number_uniq):

    species_dict = {}
    counter = 1
    for num in atomic_number_uniq:
        species_dict[num] = counter
        counter += 1
    return species_dict


def gen_alm_input(filename, prefix, mode, structure, norder, str_cutoff,
                  ndata=0, dfset='DFSET'):

    if (mode != "suggest" and mode != "optimize"):
        print("Invalid MODE: %s" % mode)
        exit(1)

    atomic_numbers_uniq = list(
        collections.OrderedDict.fromkeys(structure.atomic_numbers))

    species_index = gen_species_dictionary2(atomic_numbers_uniq)
    # Make input for ALM
    with open(filename, 'w') as f:
        f.write("&general\n")
        f.write(" PREFIX = %s\n" % prefix)
        f.write(" MODE = %s\n" % mode)
        f.write(" NAT = %i\n" % structure.num_sites)
        str_spec = ""
        for num in atomic_numbers_uniq:
            str_spec += str(get_el_sp(num)) + " "
        f.write(" NKD = %i; KD = %s\n" % (structure.ntypesp, str_spec))
        f.write(" TOLERANCE = 1.0e-3\n")
        f.write("/\n\n")
        f.write("&interaction\n")
        f.write(" NORDER = %i\n" % norder)
        f.write("/\n\n")
        f.write("&cutoff\n")
        f.write(" %s\n" % str_cutoff)
        f.write("/\n\n")
        f.write("&cell\n")
        f.write("%20.14f\n" % (1.0/Bohr))
        for i in range(3):
            for j in range(3):
                f.write("%20.13f" % structure.lattice.matrix[i][j])
            f.write("\n")
        f.write("/\n\n")
        f.write("&position\n")
        for i in range(len(structure.frac_coords)):
            f.write("%4i " % species_index[structure.atomic_numbers[i]])
            f.write("%20.14f " % structure.frac_coords[i][0])
            f.write("%20.14f " % structure.frac_coords[i][1])
            f.write("%20.14f\n" % structure.frac_coords[i][2])
        f.write("/\n\n")

        if mode == "optimize":
            f.write("&optimize\n")
            f.write(" DFSET = %s\n" % dfset)
            f.write("/\n\n")


if __name__ == '__main__':

    # Make POSCAR of supercell
    structure = Structure.from_file(POSCARname)
    Structure.make_supercell(structure, scaling_matrix)
    gen_supercell_poscar(structure)
    gen_kpoints_file(structure)

    print("Supercell generated. # Atoms: %i" % structure.num_sites)
    print("")

    gen_alm_input('ALM0.in', prefix, 'suggest', structure, 1, "*-* None")
