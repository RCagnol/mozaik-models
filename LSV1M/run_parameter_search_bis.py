# -*- coding: utf-8 -*-
import sys
from mozaik.meta_workflow.parameter_search import CombinationParameterSearch, SlurmSequentialBackend
import numpy
import time


if True:
    CombinationParameterSearch(SlurmSequentialBackend(num_threads=1, num_mpi=16,slurm_options=['--hint=nomultithread'],path_to_mozaik_env='/home/cagnol/virt_env/mozaik_validation/bin/activate'), {
    #CombinationParameterSearch(SlurmSequentialBackend(num_threads=16, num_mpi=1,slurm_options=['--hint=nomultithread'],path_to_mozaik_env='/home/cagnol/virt_env/mozaik_mpi_nest3/bin/activate'), {
      'trial' : [1],
      #'pynn_seed' : [263,1503,1701,1947,619,811],
    }).run_parameter_search()



