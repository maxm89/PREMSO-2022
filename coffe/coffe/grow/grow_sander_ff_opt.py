import os
import os.path
from os.path import join
import sys
import shutil
import glob
import subprocess
import fileinput
import re

''' REQUIRED ENVIRONMENTAL VARIABLE, DIRECTORIES AND FILES
1. BINDIR/00_qm_opt/molecule-*-gam.inp.log
2. leaprc.extrm
3. leaprc.extrm.w2p
4. molec.extrm.bcc.mol2
5. Force-field template file (e.g. ExTrM.template.dat)

'''

## IO helper -> move to other file
def DOES_FILE_EXIST(MYFILE):
    if not os.path.isfile(MYFILE):
        print('\033[92m','        ' + MYFILE + ' does not exists or is set incorrectly.', '\x1b[0m', '\n')
        sys.exit()

def DOES_DIR_EXIST(DIRECTORY):
    if not os.path.isdir(DIRECTORY):
        print('\033[92m','        The directory ' + DIRECTORY + ' does not exists.', '\x1b[0m', '\n')
        sys.exit()


class TopFileTemplate():
    def __init__(self, top_file_src, target_name):
        self._read_template(top_file_src)
        self._no_params = self._count_placeholders(self.content)
        self.target_name = target_name

    def write_to(self, target_dir, x):
        """
        Writes the given parameter vector (x) into the .top file template.
        Asserts that len(x) equals the number of place holders in the template.
        """
        content = self._fill_params(x)
        f = open(os.path.join(target_dir, self.target_name), "w")
        f.write(content)
        f.close()

    def _read_template(self, top_file_src):
        f = open(top_file_src)
        self.content = f.read()
        f.close()
        
    @property
    def file_name(self):
        return self.target_name

        
    def _fill_params(self, x):
        placeholders = ["<X_{num}>".format(num=i) for i in range(1, len(x)+1)]
        mappings = zip(placeholders, x)
        content = self._replace_all(mappings)
        return content

    def _replace_all(self, mappings):
        content = self.content
        for placeholder, replacement in mappings:
            content = content.replace(placeholder, str(replacement))
        return content

    def _count_placeholders(self, content):
        return len(re.findall(r'<\d+>', content))



def mstart(x, OUTPATH, BINDIR, TPDUMMY, MOL2_FILE, LEAPRC_FILE, W2P_FILE, target_names):

    ###########################################################
    def relative_energy(completeList = [], *args):
        RELATIVE_E = []
        energylist = []
        for line in completeList:
            energylist.append(line.split(' ')[1])
        EMIN = energylist[0]
        print('First entry in completeList:',completeList[0])
        print('EMIN = ',EMIN)
        for E in range(0,len(energylist)):
            RELATIVE_E.append(completeList[E].split(' ')[0] + ' ' + str(float(energylist[E])-float(EMIN)))
        return RELATIVE_E

    ## Collects final energies of MM minimizations
    def GET_AMBER_ENERGY(LOG,moleculeName):
        START = 'FINAL RESULTS'
        END = 'BOND'
        LINES= []
        print("file:::", LOG)
        with open(LOG) as input_data:
            for line in input_data:
                if line.strip() == START:
                    break
            # Reads text until the end of the block:
            for line in input_data:
                if line.strip() == END:
                    break
                LINES.append(line.split())
        LINES = [x for x in LINES if x]  ## remove empty lists
        AMBER_ENERGIES.append(moleculeName + " " + LINES[1][1])

    def create_mm_mol2_coords(INFILE, MOL2):
        START = '@<TRIPOS>ATOM'
        END = '@<TRIPOS>BOND'
        COORD = []
        ATOMLABEL = []
        RESNAME = []
        ATOMTYPES = []
        CHARGES = []
        LINE = []
        ## Extract unique xyz coordinates
        if MOL2.endswith('.mol2'):
            with open(MOL2) as input_data_1:
                for line in input_data_1:
                    if line.strip() == START:
                        break
                # Reads text until the end of the block:
                for line in input_data_1:
                    if line.strip() == END:
                        break
                    COORD.append(line[19:46])

        if MOL2.endswith('.xyz'):
            i=1
            with open(MOL2) as input_data_1:
                for line in input_data_1:
                    if i > 2:
                        COORD.append(line[16:68])
                    i+=1

        ## Extract proper labels, atom types and charges
        with open(INFILE) as input_data:
            for line in input_data:
                if line.strip() == START:
                    break
            for line in input_data:
                if line.strip() == END:
                    break
                ATOMLABEL.append(line[0:18])
                RESNAME.append(line[50:65])
                ATOMTYPES.append(line.split()[5])
                CHARGES.append(line.split()[8])

        ## combine them
        for a, b, c, d, e in zip(ATOMLABEL,COORD,ATOMTYPES,RESNAME,CHARGES):
            LINE.append(a + ' ' + b + ' ' + c + ' ' + d + ' ' + e)
        return LINE

    def psi2xyz(INFILE,OUTFILE):
        START = 'Final optimized geometry and variables:'
        END = 'Cleaning optimization helper files.'
        GEOM = []
        i = 1
        with open(INFILE) as input_data:
            for line in input_data:
                if line.strip() == START:
                    break
            # Reads text until the end of the block:
            for line in input_data:  ## This keeps reading the file
                if (i > 5):          ## Skip 5 lines before recording
                    if line.strip() == END:
                        break
                    GEOM.append(line)
                i += 1

        if GEOM[len(GEOM)-1] == '\n':
            GEOM = GEOM[0:len(GEOM)-1]
        number_of_atoms = len(GEOM)

        filename = os.path.basename(INFILE)


        f=open(OUTFILE,'w')
        f.write(str(number_of_atoms) + '\n')
        f.write(filename + '\n')
        for coord in GEOM:
            if coord.endswith('\n'):
                f.write(coord)
            else:
                f.write(coord + '\n')
        f.close()

    def write_template(out_dir, x):
        tp = TopFileTemplate(TPDUMMY, "ExTrM.Amber.hydrocarbons.dat")
        tp.write_to(out_dir, x)

    ###########################################################

    # Convert gromacs units to amber units
    SIGMA_1 = (x[0]*10*2**(1.0/6.0))/2.0
    SIGMA_2 = (x[1]*10*2**(1.0/6.0))/2.0
    EPSILON_1 = x[2]/4.184
    EPSILON_2 = x[3]/4.184

    print("params:", SIGMA_1, SIGMA_2, EPSILON_1, EPSILON_2)

    ## Check if required directories exist
    if not os.path.exists(BINDIR):
        os.makedirs(BINDIR)
    if not os.path.exists(BINDIR + '/06_mm_opt/'):
        os.makedirs(BINDIR + '/06_mm_opt/')

    BINDIR_QM_MM = os.path.join(os.path.dirname(OUTPATH),'BINDIR')
    if not os.path.exists(BINDIR_QM_MM):
        os.makedirs(BINDIR_QM_MM)
    if not os.path.exists(os.path.join(BINDIR_QM_MM, '06_mm_opt/')):
        os.makedirs(os.path.join(BINDIR_QM_MM, '06_mm_opt/'))

    os.environ['BINDIR_QM_MM'] = BINDIR_QM_MM

    DOES_DIR_EXIST(BINDIR + '/00_qm_opt/')
    ###########################################################
    ## Variables
    DOES_FILE_EXIST(MOL2_FILE)
    DOES_FILE_EXIST(LEAPRC_FILE)
    DOES_FILE_EXIST(W2P_FILE)

    shutil.copy2(MOL2_FILE, os.path.join(BINDIR_QM_MM, '06_mm_opt/'))
    shutil.copy2(LEAPRC_FILE, os.path.join(BINDIR_QM_MM, '06_mm_opt/'))
    shutil.copy2(W2P_FILE, os.path.join(BINDIR_QM_MM, '06_mm_opt/'))

    MOL2_TEMPLATE = os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'),os.path.basename(MOL2_FILE))
    FF_SOURCE_1 = os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'),os.path.basename(LEAPRC_FILE))
    FF_SOURCE_2 = os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'),os.path.basename(W2P_FILE))

    shutil.copy2(os.path.join(os.path.join(BINDIR, '06_mm_opt/'),'frcmod.extrm.w2p'),os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'),'frcmod.extrm.w2p'))

    HEAD = []
    TAIL = []
    AMBER_ENERGIES = []

    ###########################################################
    ## Initialize variables and parse command line

    ## Call helper script
    SUBDIR_PATH=OUTPATH + "/subdir"

    os.environ["working_dir"] = OUTPATH

    if not os.path.exists(SUBDIR_PATH):
        os.makedirs(SUBDIR_PATH)

    if not os.path.exists(os.path.join(BINDIR_QM_MM, '06_mm_opt/')):
        os.makedirs(os.path.join(BINDIR_QM_MM, '06_mm_opt/'))

    write_template(BINDIR_QM_MM + "/06_mm_opt/", [SIGMA_1,SIGMA_2,EPSILON_1,EPSILON_2])

    QMLOG = glob.glob(BINDIR + '/00_qm_opt/molecule-*-psi.inp.log')    ## original was looking for -psi.inp.log
    QMLOG=sorted(QMLOG)

    ###########################################################
    ## Gather the AMBER proper head and end of mol2 file
    with open(BINDIR_QM_MM + '/06_mm_opt/molec.extrm.bcc.mol2') as file:
        HEAD = [next(file) for x in range(6)]
        for line in file:
            if '@<TRIPOS>BOND' in line:
                for line in file:
                    TAIL.append(line)

    HEAD = [s.rstrip() for s in HEAD]
    TAIL = [s.rstrip() for s in TAIL]

    ## Amber files needed for referencing the force force.
    ## Replace location of w2p force-field supplementary parameters.
    shutil.copy2(W2P_FILE,os.path.join(BINDIR_QM_MM, '06_mm_opt/'))
    shutil.copy2(LEAPRC_FILE,os.path.join(BINDIR_QM_MM, '06_mm_opt/'))
    print("replace in grow_sander")
    #for line in fileinput.FileInput([os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'), os.path.basename(W2P_FILE))], inplace=True):
        #print(line.replace('SOURCEDIR', BINDIR_QM_MM + '/06_mm_opt'), end='')
    filee = os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'), os.path.basename(W2P_FILE))
    with open(filee, 'r') as f:
        dataa = f.read()
        dataa = dataa.replace('SOURCEDIR', BINDIR_QM_MM + '/06_mm_opt')
    with open(filee, 'w') as f:
        f.write(dataa)
    #for line in fileinput.FileInput([os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'), os.path.basename(LEAPRC_FILE))], inplace=True):
        #print(line.replace('SOURCEDIR', BINDIR_QM_MM + '/06_mm_opt'), end='')
    filee = os.path.join(os.path.join(BINDIR_QM_MM, '06_mm_opt/'), os.path.basename(LEAPRC_FILE))
    with open(filee, 'r') as f:
        dataa = f.read()
        dataa = dataa.replace('SOURCEDIR', BINDIR_QM_MM + '/06_mm_opt')
    with open(filee, 'w') as f:
        f.write(dataa)
    ###########################################################
    ## 1. Create a mol2 file from the QM log files such that AMBER's tleap can read it.
    ## 2. Create leap input and run tleap
    ## 3. Execute Sander minimization
    ## 4. Convert optimized geometry rst file to pdb for easy viewing
    ## 5. Grab raw energy out of the output file.

    print("STARTING MINIM")
    with open(BINDIR_QM_MM + '/06_mm_opt/min.in', 'w') as f:
        f.write('Constraint Minimization\n')
        f.write('&cntrl\n')
        f.write('imin=1, dielc=1,ntb=0,\n')
        f.write('maxcyc=20000, cut=40.0,\n')
        f.write('ntc=1, ntf=1,\n')
        f.write('drms=0.01,nmropt=0\n')
        f.write('&end\n')


    for LOG in QMLOG:
        LOGNAME = LOG.split('/')
        BASENAME = (LOGNAME[-1]).split('.')
        ## For use with GAMESS QM log files
        psi2xyz(LOG, os.path.join(OUTPATH, BASENAME[0] + '.xyz'))

        ## Create a mol2 file from a GAMESS log file
        FNULL = open(os.devnull, 'w')

        ## Collect unique coordinates for each structure
        MOL2_COORDS = []
        MOL2_COORDS = create_mm_mol2_coords(MOL2_TEMPLATE, os.path.join(OUTPATH, BASENAME[0] + '.xyz'))

        ## Put it all together into a single file
        with open(os.path.join(OUTPATH,BASENAME[0] + '.mol2'),'w') as f:
            for item in HEAD:
                f.write("%s\n" % item)
            for item in MOL2_COORDS:
                f.write("%s\n" % item)
            f.write("@<TRIPOS>BOND\n")
            for item in TAIL:
                f.write("%s\n" % item)
        shutil.copy2(os.path.join(OUTPATH,BASENAME[0] + '.mol2'),BINDIR_QM_MM + '/06_mm_opt')

        ## Create each leap.in
        with open(join(OUTPATH, BASENAME[0]+'.leap.in'), 'w') as f:
            f.write('logfile ' + join(OUTPATH, BASENAME[0]) + '.leap.log\n')
            f.write('source ' + FF_SOURCE_1 +'\n')
            f.write('source ' + FF_SOURCE_2 +'\n')
            f.write('verbosity 2\n')
            f.write('a = loadmol2 ' + os.path.join(BINDIR_QM_MM, '06_mm_opt/') + BASENAME[0] + '.mol2\n')
            f.write('saveamberparm a ' + join(OUTPATH, BASENAME[0]) + '.leap.top ' + join(OUTPATH, BASENAME[0]) + '.leap.crd\n')
            f.write('savepdb a ' + os.path.join(BINDIR_QM_MM, '06_mm_opt/') + BASENAME[0] + '.leap.pdb\n')
            f.write('quit\n')

        ## Run tleap to get filename.top and filename.crd --> used as input for MM minimization or MD
        TLEAP = ['tleap', '-s -f', join(OUTPATH, BASENAME[0]) + '.leap.in']
        subprocess.call(TLEAP, stdout=FNULL, stderr=subprocess.STDOUT)
        DOES_FILE_EXIST(join(OUTPATH, BASENAME[0])+'.leap.top')
        
        print("TLEAP DONE")
        ## Run minimizations
        SANDER = ['sander', '-O', '-i', os.path.join(BINDIR_QM_MM, '06_mm_opt/') + 'min.in', '-o', join(OUTPATH, BASENAME[0]) + '.min.out', '-p', join(OUTPATH, BASENAME[0]) + '.leap.top', '-c', join(OUTPATH, BASENAME[0]) + '.leap.crd', '-r', join(OUTPATH, BASENAME[0]) + '.min.rst', '-ref', join(OUTPATH, BASENAME[0]) + '.leap.crd']
        subprocess.call(SANDER, stdout=FNULL, stderr=subprocess.STDOUT)
        print("SANDER DONE")
        DOES_FILE_EXIST(join(OUTPATH, BASENAME[0])+'.min.out')

        ## create pdb from MM minimization restart file (i.e. final optimized structure).
        AMBPDB = ['ambpdb', '-p', join(OUTPATH, BASENAME[0])+'.leap.top', '-c', join(OUTPATH, BASENAME[0])+'.min.rst']
        subprocess.call(AMBPDB, stdout=open(join(OUTPATH, BASENAME[0])+'.min.rst.pdb', 'w'), stderr=FNULL)
        print("AMBPDB DONE")
        ## Obtain raw energy
        GET_AMBER_ENERGY(join(OUTPATH, BASENAME[0])+'.min.out', BASENAME[0])
        print("GET ENERGY DONE")
    ###########################################################
    ## write out raw energy data

    with open(join(OUTPATH, 'Energy.raw.extrm.txt'), 'w') as f:
        for item in AMBER_ENERGIES:
            f.write('%s\n' % item)


    RELATIVE_E = relative_energy(AMBER_ENERGIES)

    ## write out relative energy data
    with open(join(OUTPATH, 'Energy.rel.extrm.txt'), 'w') as f:
        for item in RELATIVE_E:
            f.write('%s\n' % item)

    # HARDCODED!!!
    f = target_names
    f = open(target_names, 'r')
    test_names = f.readlines()
    f.close()

    f = open(join(OUTPATH, 'Energy.rel.extrm.txt'), 'r')
    rel_e = f.readlines()
    f.close()

    if not len(test_names) == len(rel_e):
        print('len(test_names) = %s and len(rel_e) = %s are not equal!' %(len(test_names), len(rel_e)))
        sys.exit()

    properties=[]
    for line in range(0,len(test_names)):
        if not test_names[line].split('.')[0] == rel_e[line].split(' ')[0].split('.')[0]:
            print('molecule names %s and %s are not equal, might be a wrong ordering.' %(test_names[line].split('.')[0], rel_e[line].split(' ')[0].split('.')[0]))
            sys.exit()
        properties.append(str(rel_e[line].split(' ')[1]))

    with open(join(OUTPATH, 'properties.txt'),'w') as f:
        for item in properties:
            if not item.endswith('\n'):
                f.write('%s\n' % item)
            else:
                f.write('%s' % item)

    if os.path.isfile(join(OUTPATH, 'properties.txt')):
        print("Simulation successfully terminated.", join(OUTPATH, 'terminated.txt'))
    else:
        print("grow_sander_ff_opt.py: ", join(OUTPATH, 'properties.txt'), " not found")

