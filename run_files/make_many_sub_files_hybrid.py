import sys
import os

# kk=2
# for del_bl in (10,20,4,6,8):
#     fcontent = """#PBS -q regular
# #PBS -l mppwidth=48
# #PBS -l walltime=05:00:00
# #PBS -N gsm_hy_{0}
# #PBS -e out_files/gsm_hy_{1}.$PBS_JOBID.err
# #PBS -o out_files/gsm_hy_{2}.$PBS_JOBID.out
# #PBS -V

# module load python
# module load mpi4py

# cd $PBS_O_WORKDIR 
# # del_bl,num_bl (for one side of grid)
# aprun -n 48 python-mpi /global/homes/m/mpresley/scripts/mpi_Q_matrix_hybrid_grid.py {3} 20
# """.format(kk,kk,kk,del_bl)
#     with open('./run_mpi_gsm_{0}.sh'.format(kk), 'w') as file:
#         file.writelines(fcontent)
#     os.system('qsub ./run_mpi_gsm_{0}.sh'.format(kk))
#     kk += 1

kk=1
for del_bl in (10,20,4,6,8):
    fcontent = """#PBS -q regular
#PBS -l mppwidth=1536
#PBS -l walltime=05:00:00
#PBS -N gsm_hy_{0}
#PBS -e out_files/gsm_hy_{1}.$PBS_JOBID.err
#PBS -o out_files/gsm_hy_{2}.$PBS_JOBID.out
#PBS -V

module load python
module load mpi4py

cd $PBS_O_WORKDIR 
# del_bl,num_bl (for one side of grid)
aprun -n 1536 python-mpi /global/homes/m/mpresley/scripts/mpi_gsm_hybrid.py {3} 20
""".format(kk,kk,kk,del_bl)
    with open('./run_mpi_gsm_{0}.sh'.format(kk), 'w') as file:
        file.writelines(fcontent)
    os.system('qsub ./run_mpi_gsm_{0}.sh'.format(kk))
    kk += 1
