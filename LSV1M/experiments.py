# #!/usr/local/bin/ipython -i
# from mozaik.experiments import *
# from mozaik.experiments.vision import *
# from mozaik.sheets.population_selector import RCRandomPercentage
# from parameters import ParameterSet


# def create_experiments(model):

#     return [
#         # Lets kick the network up into activation

#         # Spontaneous Activity
#         NoStimulation(model, ParameterSet(
#             {'duration': 3*8*2*5*3*8*7})),

#         # Measure orientation tuning with full-filed sinusoidal gratins
#         MeasureOrientationTuningFullfield(model, ParameterSet(
#             {'num_orientations': 10, 'spatial_frequency': 0.8, 'temporal_frequency': 2, 'grating_duration': 2*143*7, 'contrasts': [10,30,100], 'num_trials':10, 'shuffle_stimuli': True})),

#         # Measure response to natural image with simulated eye movement
#         MeasureNaturalImagesWithEyeMovement(model, ParameterSet(
#             {'stimulus_duration': 2*143*7, 'num_trials': 10, 'size':30, 'shuffle_stimuli': False})),
#     ]


# def create_experiments_stc(model):

#     return [

#         # Spontaneous Activity
#         NoStimulation(model, ParameterSet({'duration': 2*5*3*8*7})),

#         # Size Tuning
#         MeasureSizeTuning(model, ParameterSet({'num_sizes': 12, 'max_size': 5.0, 'log_spacing': True, 'orientations': [0], 'positions': [(0,0)],
#                                                'spatial_frequency': 0.8, 'temporal_frequency': 2, 'grating_duration': 2*143*7, 'contrasts': [10, 100], 'num_trials': 10, 'shuffle_stimuli': True})),
#     ]


# def create_experiments_spont(model):
#     return [
#         # Spontaneous Activity
#         NoStimulation(model, ParameterSet(
#             {'duration': 3*8*2*5*3*8*7})),
#     ]

#!/usr/local/bin/ipython -i
from mozaik.experiments import *
from mozaik.experiments.vision import *
from mozaik.sheets.population_selector import RCRandomPercentage
from parameters import ParameterSet
import numpy as np

def create_experiments(model):
    return [
        MeasureNaturalImagesWithEyeMovement(
            model, ParameterSet({"stimulus_duration": 11 * 143 * 7, "num_trials": 473, "size": 34.731934731934736, 
                                "data_dir": "/home/rozsa/dev/Julia_analysis/Latency_shortening/data",
                                "data_filename": "HIME_20140904_rec5_blk2_eye_position.hdf5",
                                "stim_dir": "/home/rozsa/dev/Julia_analysis/Latency_shortening/stimuli"
                                })
        ),
    ]


# def create_experiments(model):
#     return [
#         # Spontaneous Activity
#         NoStimulation(model, ParameterSet({"duration": 10 * 1001})),
#     ]