# -*- coding: utf-8 -*-
"""
This is the implementation of the model corresponding to the pre-print `Iso-orientation bias of layer 2/3 connections: the unifying mechanism of spontaneous, visually and optogenetically driven V1 dynamics`
Rózsa, T., Cagnol, R., Antolík, J. (2024).
https://www.biorxiv.org/ TODO: Update
"""

import matplotlib
matplotlib.use('Agg')

from mpi4py import MPI
from mozaik.storage.datastore import Hdf5DataStore, PickledDataStore
from parameters import ParameterSet
from analysis_and_visualization import perform_analysis_and_visualization_stc
from model import SelfSustainedPushPull
from experiments import create_experiments_stc
import mozaik
from mozaik.controller import run_workflow, setup_logging
import mozaik.controller
import sys
from pyNN import nest

mpi_comm = MPI.COMM_WORLD

import nest
nest.Install("stepcurrentmodule")

if True:
    data_store, model = run_workflow(
        'SelfSustainedPushPull', SelfSustainedPushPull, create_experiments_stc)
    data_store.save()


if mpi_comm.rank == 0:
    print("Starting visualization")
    perform_analysis_and_visualization_stc(data_store)
    data_store.save()