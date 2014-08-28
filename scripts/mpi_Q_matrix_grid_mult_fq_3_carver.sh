# !/bin/bash

#PBS -S /bin/bash
#PBS -N mpi_Q_matrix_grid_mult_fq_3_carver
#PBS -j eo
#PBS -l nodes=9:ppn=8,walltime=04:00:00
#PBS -q regular
#PBS -A m1871

codeLoc="/global/scratch2/sd/acliu/GlobalSignalInterferometer/gs_mpi"
outputLoc="/global/scratch2/sd/acliu/GlobalSignalInterferometer/gs_data"
numProcs=72
maxl=7
beam_sig=1.57 
del_bl=0.844 
sqGridSideLen=12
lowerFreq=120 # in MHz
upperFreq=150 # in MHz
deltaFreq=1 # in MHz


module load python/2.7.3
module load numpy
module load matplotlib
module load openmpi-gnu
module load mpi4py

# For running on my laptop or Carver
echo "Starting run now..."
date
mpirun -np $numProcs python-mpi "$codeLoc/mpi_Q_matrix_grid_mult_fq_3.py" $outputLoc $maxl $beam_sig $del_bl $sqGridSideLen $lowerFreq $upperFreq $deltaFreq
date