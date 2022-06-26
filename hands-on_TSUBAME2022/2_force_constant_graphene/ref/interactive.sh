#!/bin/sh
#QSUB2 queue qD
#QSUB2 core 48
#QSUB2 mpi 1
#QSUB2 smp 48
#QSUB2 wtime 1:00:00
#PBS -N hoge
#PBS -I

cd ${PBS_O_WORKDIR}
