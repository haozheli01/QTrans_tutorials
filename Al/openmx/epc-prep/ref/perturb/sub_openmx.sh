#!/bin/bash
#SBATCH -p queue1-1 
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
##SBATCH --cpus-per-task=2
#SBATCH --exclusive 
#SBATCH --cpus-per-task=1
export I_MPI_PMI_LIBRARY=/opt/gridview/slurm/lib/libpmi2.so
ulimit -s unlimited

module purge
module load openmx.3.9

export UCX_TLS=dc,self
export OMP_NUM_THREADS=1

#srun --mpi=pmi2 openmx_postprocess openmx.dat > openmx.std 2>&1 
for i in {0..3}
do
mkdir ${i}
cd ./${i}
mv ../QTepc-${i}.dat ./openmx.dat
srun --mpi=pmi2 openmx openmx.dat > openmx.out 2>&1
cd ..
done

