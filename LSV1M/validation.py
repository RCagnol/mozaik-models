from mozaik.validation.sci_tests import *
from mozaik.validation.sci_models import *
from visualization_functions import ValidationFigTable
from mozaik.analysis.data_structures import ValidationTestResult
from parameters import ParameterSet
from mozaik.storage.queries import *
import numpy as np
import mozaik

logger = mozaik.getMozaikLogger()


def validate_spont(datastore):
    """
    Validates data corresponding to spontaneous activity
        
    
    Parameters
    -------------

    datastore : Mozaik Datastore object 

    """

    logger.info("Validating spontaneous activity")
    Sci_Model = ModelV1Spont(datastore)
    test_results = []


    Avg_rate_test = AverageFiringRate(0.32, "V1_Exc_L4")      
    score = Avg_rate_test.judge(Sci_Model, deep_error=True)
    datastore.add_analysis_result(ValidationTestResult(score, observation=0.32))

    print(score.summarize())

    Avg_rate_test_2 = AverageFiringRate(2, "V1_Exc_L4")
    score = Avg_rate_test_2.judge(Sci_Model, deep_error=True)
    datastore.add_analysis_result(ValidationTestResult(score, observation=0.2))

    print(score.summarize())

    datastore.save()    
    validation_fig = ValidationFigTable(datastore, ParameterSet({}), plot_file_name='TableTestsResults.png',
                        fig_param={'dpi': 200}).plot()




def validate_stc(datastore):
    """
    Validates data corresponding to
        
    
    Parameters
    -------------

    datastore : Mozaik Datastore object 

    """
    raise NotImplementedError()



def validate(datastore):
    """
    Validates data corresponding to
        
    
    Parameters
    -------------

    datastore : Mozaik Datastore object 

    """
    raise NotImplementedError()




