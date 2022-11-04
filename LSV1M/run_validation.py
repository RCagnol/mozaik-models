from validation import validate_spont
from mozaik.storage.datastore import PickledDataStore
import sys
from parameters import ParameterSet
from mozaik.controller import Global
import mozaik
from mozaik.controller import setup_logging

########### Helper script to load a datastore and run validation 

assert len(sys.argv) == 2
Global.root_directory = sys.argv[1] + '/'
setup_logging()

data_store = PickledDataStore(load=True,parameters=ParameterSet({'root_directory': sys.argv[1], 'store_stimuli' : True}), replace=True)
validate_spont(data_store)


