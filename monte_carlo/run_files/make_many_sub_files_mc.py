import sys
import os

kk=0
for beam_sig in (0.087,0.175,0.349,0.689,1.047):
    for del_bl in (4,6,8):#,10,20):
        fcontent = """#PBS -q regular
#PBS -l mppwidth=24
#PBS -l walltime=02:30:00
#PBS -N mc_grid_{0}
#PBS -e out_files/mc_grid_{1}.$PBS_JOBID.err
#PBS -o out_files/mc_grid_{2}.$PBS_JOBID.out
#PBS -V

module load python
module load mpi4py

cd $PBS_O_WORKDIR 
# num0,save_interval,beam_sig,del_bl,num_bl (for one side of grid)
aprun -n 24 python-mpi /global/homes/m/mpresley/gs_mpi/monte_carlo/mpi_monte_carlo_gen_y_mult_fq.py 10000 1000 {3} {4} 10
""".format(kk,kk,kk,beam_sig,del_bl)
        with open('./run_mpi_mc_grid_{0}.sh'.format(kk), 'w') as file:
            file.writelines(fcontent)
        os.system('qsub ./run_mpi_mc_grid_{0}.sh'.format(kk))
        kk += 1

