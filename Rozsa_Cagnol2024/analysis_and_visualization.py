import os
import psutil
import sys
import mozaik
from mozaik.visualization.plotting import *
from mozaik.analysis.technical import NeuronAnnotationsToPerNeuronValues
from mozaik.analysis.analysis import *
from mozaik.analysis.vision import *
from mozaik.analysis.lfp import *
from mozaik.storage.queries import *
from mozaik.storage.datastore import PickledDataStore
from mozaik.controller import Global
from visualization_functions import *

logger = mozaik.getMozaikLogger()

process = psutil.Process(os.getpid())


low_contrast = 10
ttcc_contrast = 30 
high_contrast = 100
dpi = 300
paper_figures = True


def memory_usage_psutil():
    # return the memory usage in MB
    return process.memory_percent()


def analysis(data_store, analog_ids, analog_ids_inh, analog_ids23=None, analog_ids_inh23=None):
    sheets = list(set(data_store.sheets()) & set(
        ['V1_Exc_L4', 'V1_Inh_L4', 'V1_Exc_L2/3', 'V1_Inh_L2/3']))
    exc_sheets = list(set(data_store.sheets()) &
                      set(['V1_Exc_L4', 'V1_Exc_L2/3']))
    l23_flag = ('V1_Exc_L2/3' in set(sheets))

    logger.info('0: ' + str(memory_usage_psutil()))

    dsv = param_filter_query(
        data_store, st_name='FullfieldDriftingSinusoidalGrating', sheet_name=sheets)
    Analog_F0andF1(dsv, ParameterSet({})).analyse()

    TrialMean(dsv, ParameterSet(
        {'cond_exc': True, 'vm': True, 'cond_inh': True})).analyse()

    TrialAveragedFiringRate(param_filter_query(data_store, sheet_name=sheets,
                                               st_name='FullfieldDriftingSinusoidalGrating'), ParameterSet({})).analyse()
    TrialAveragedFiringRate(param_filter_query(
        data_store, st_direct_stimulation_name=None, st_name='InternalStimulus'), ParameterSet({})).analyse()
    logger.info('1: ' + str(memory_usage_psutil()))
    Irregularity(param_filter_query(data_store, st_direct_stimulation_name=None,
                                    st_name='InternalStimulus'), ParameterSet({})).analyse()

    PSTH(param_filter_query(data_store),
         ParameterSet({'bin_length': 10.0})).analyse()

    logger.info('2: ' + str(memory_usage_psutil()))
    NeuronToNeuronAnalogSignalCorrelations(param_filter_query(
        data_store, analysis_algorithm='PSTH'), ParameterSet({'convert_nan_to_zero': True})).analyse()

    logger.info('3: ' + str(memory_usage_psutil()))
    PopulationMeanAndVar(param_filter_query(data_store, st_direct_stimulation_name=None,
                                            st_name='InternalStimulus'), ParameterSet({'ignore_nan_and_inf': False})).analyse()

    dsv = queries.param_filter_query(
        data_store, st_name='FullfieldDriftingSinusoidalGrating', analysis_algorithm='PSTH')
    TrialMean(dsv, ParameterSet(
        {'cond_exc': False, 'vm': False, 'cond_inh': False})).analyse()

    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             analysis_algorithm='TrialAveragedFiringRate', value_name='Firing rate', sheet_name=sheets)
    GaussianTuningCurveFit(dsv, ParameterSet(
        {'parameter_name': 'orientation'})).analyse()

    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             analysis_algorithm='TrialAveragedFiringRate', value_name='Firing rate', sheet_name=sheets)
    PeriodicTuningCurvePreferenceAndSelectivity_VectorAverage(
        dsv, ParameterSet({'parameter_name': 'orientation'})).analyse()
    logger.info('4: ' + str(memory_usage_psutil()))

    dsv = param_filter_query(data_store, sheet_name=exc_sheets)
    ActionPotentialRemoval(dsv, ParameterSet({'window_length': 5.0})).analyse()

    logger.info('5: ' + str(memory_usage_psutil()))


    dsv = param_filter_query(
        data_store, st_name='InternalStimulus', st_direct_stimulation_name=None)
    Analog_MeanSTDAndFanoFactor(dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
    SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
    SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(VM)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Vm')
    OperationPNVfromPNVS(pnv, lambda x, y: -(x+y), '-(x+y)',
                         dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Inh_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             sheet_name='V1_Inh_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
    SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Inh_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             sheet_name='V1_Inh_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
    SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Inh_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(VM)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             sheet_name='V1_Inh_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Vm')
    OperationPNVfromPNVS(pnv, lambda x, y: -(x+y), '-(x+y)',
                         dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                             sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
    OperationPNVfromPNVS(pnv, lambda x, y: x-y, 'x-y',
                         dsv, ParameterSet({})).analyse()

    pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                             'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
    dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                             sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
    OperationPNVfromPNVS(pnv, lambda x, y: x-y, 'x-y',
                         dsv, ParameterSet({})).analyse()

    logger.info('8: ' + str(memory_usage_psutil()))
    if l23_flag:

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                                 sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
        SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                                 sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
        SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(VM)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                                 sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Vm')
        OperationPNVfromPNVS(pnv, lambda x, y: -(x+y),
                             '-(x+y)', dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Inh_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                                 sheet_name='V1_Inh_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
        SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Inh_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                                 sheet_name='V1_Inh_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
        SubtractPNVfromPNVS(pnv, dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Inh_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(VM)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                                 sheet_name='V1_Inh_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Vm')
        OperationPNVfromPNVS(pnv, lambda x, y: -(x+y),
                             '-(x+y)', dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                 sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
        OperationPNVfromPNVS(pnv, lambda x, y: x-y, 'x-y',
                             dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                 sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
        OperationPNVfromPNVS(pnv, lambda x, y: x-y, 'x-y',
                             dsv, ParameterSet({})).analyse()

    logger.info('9: ' + str(memory_usage_psutil()))
    dsv = queries.param_filter_query(
        data_store, y_axis_name='spike count (bin=13.0)')
    mozaik.analysis.analysis.TrialToTrialFanoFactorOfAnalogSignal(
        dsv, ParameterSet({})).analyse()

    if True:
        logger.info('10: ' + str(memory_usage_psutil()))

        TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L4', st_name="NaturalImageWithEyeMovement",
                                                                          analysis_algorithm='ActionPotentialRemoval'), ParameterSet({'neurons': list(analog_ids), 'window_min': 0, 'window_max': -1})).analyse()
        TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L4', st_name="NaturalImageWithEyeMovement", analysis_algorithm='PSTH'), ParameterSet({
                                                       'neurons': list(analog_ids), 'window_min': 0, 'window_max': -1})).analyse()
        TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L4', st_name='FullfieldDriftingSinusoidalGrating',
                                                                          analysis_algorithm='ActionPotentialRemoval', st_contrast=ttcc_contrast), ParameterSet({'neurons': list(analog_ids), 'window_min': 0, 'window_max': -1})).analyse()
        TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L4', st_name='FullfieldDriftingSinusoidalGrating',
                                                                          analysis_algorithm='PSTH', st_contrast=ttcc_contrast), ParameterSet({'neurons': list(analog_ids), 'window_min': 0, 'window_max': -1})).analyse()

        logger.info('11: ' + str(memory_usage_psutil()))
        if l23_flag:
            TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L2/3', st_name="NaturalImageWithEyeMovement",
                                                                              analysis_algorithm='ActionPotentialRemoval'), ParameterSet({'neurons': list(analog_ids23), 'window_min': 0, 'window_max': -1})).analyse()
            TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L2/3', st_name="NaturalImageWithEyeMovement",
                                                                              analysis_algorithm='PSTH'), ParameterSet({'neurons': list(analog_ids23), 'window_min': 0, 'window_max': -1})).analyse()
            TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L2/3', st_name='FullfieldDriftingSinusoidalGrating',
                                                                              analysis_algorithm='ActionPotentialRemoval', st_contrast=ttcc_contrast), ParameterSet({'neurons': list(analog_ids23), 'window_min': 0, 'window_max': -1})).analyse()
            TrialToTrialCrossCorrelationOfAnalogSignalList(param_filter_query(data_store, sheet_name='V1_Exc_L2/3', st_name='FullfieldDriftingSinusoidalGrating',
                                                                              analysis_algorithm='PSTH', st_contrast=ttcc_contrast), ParameterSet({'neurons': list(analog_ids23), 'window_min': 0, 'window_max': -1})).analyse()
        logger.info('12: ' + str(memory_usage_psutil()))

    dsv = param_filter_query(
        data_store, analysis_algorithm='ActionPotentialRemoval')
    dsv.print_content(full_ADS=True)
    TrialVariability(dsv, ParameterSet(
        {'vm': False,  'cond_exc': False, 'cond_inh': False})).analyse()
    param_filter_query(
        data_store, analysis_algorithm='TrialVariability').print_content(full_ADS=True)

    logger.info('13: ' + str(memory_usage_psutil()))
    ModulationRatio(param_filter_query(
        data_store, sheet_name=exc_sheets, st_contrast=[high_contrast]), ParameterSet({})).analyse()

    logger.info('14: ' + str(memory_usage_psutil()))

    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating',
                             analysis_algorithm='TrialAveragedFiringRate', value_name='Firing rate')
    CircularVarianceOfTuningCurve(dsv, ParameterSet(
        {'parameter_name': 'orientation'})).analyse()

    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating', value_name=[
                             'F1(psth (bin=10.0) trial-to-trial mean)'], analysis_algorithm='Analog_F0andF1', sheet_name=sheets)
    GaussianTuningCurveFit(dsv, ParameterSet(
        {'parameter_name': 'orientation'})).analyse()
    CircularVarianceOfTuningCurve(dsv, ParameterSet(
        {'parameter_name': 'orientation'})).analyse()

    dsv = param_filter_query(data_store, st_name='FullfieldDriftingSinusoidalGrating', value_name=[
                             'F0(psth (bin=10.0) trial-to-trial mean)'], analysis_algorithm='Analog_F0andF1', sheet_name=sheets)
    GaussianTuningCurveFit(dsv, ParameterSet(
        {'parameter_name': 'orientation'})).analyse()
    CircularVarianceOfTuningCurve(dsv, ParameterSet(
        {'parameter_name': 'orientation'})).analyse()

    logger.info('15: ' + str(memory_usage_psutil()))

    data_store.save()


def perform_analysis_and_visualization_stc(data_store):
    l23 = 'V1_Exc_L2/3' in set(data_store.sheets())
    analog_ids = param_filter_query(data_store, sheet_name="V1_Exc_L4").get_segments()[
        0].get_stored_esyn_ids()
    analog_ids_inh = param_filter_query(
        data_store, sheet_name="V1_Inh_L4").get_segments()[0].get_stored_esyn_ids()
    spike_ids = param_filter_query(data_store, sheet_name="V1_Exc_L4").get_segments()[
        0].get_stored_spike_train_ids()
    spike_ids_inh = param_filter_query(data_store, sheet_name="V1_Inh_L4").get_segments()[
        0].get_stored_spike_train_ids()

    NeuronAnnotationsToPerNeuronValues(data_store, ParameterSet({})).analyse()

    if l23:
        analog_ids23 = param_filter_query(
            data_store, sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_esyn_ids()
        analog_ids_inh23 = param_filter_query(
            data_store, sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_esyn_ids()
        spike_ids23 = param_filter_query(
            data_store, sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_spike_train_ids()
        spike_ids_inh23 = param_filter_query(
            data_store, sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_spike_train_ids()
        l23_exc_or = data_store.get_analysis_result(
            identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Exc_L2/3')[0]
        l23_exc_or_many = numpy.array(spike_ids23)[numpy.nonzero(numpy.array([circular_dist(
            l23_exc_or.get_value_by_id(i), 0, numpy.pi) for i in spike_ids23]) < 0.25)[0]]
        idx23 = data_store.get_sheet_indexes(
            sheet_name='V1_Exc_L2/3', neuron_ids=l23_exc_or_many)

    l4_exc_or = data_store.get_analysis_result(
        identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Exc_L4')[0]
    l4_exc_or_many = numpy.array(spike_ids)[numpy.nonzero(numpy.array([circular_dist(
        l4_exc_or.get_value_by_id(i), 0, numpy.pi) for i in spike_ids]) < 0.25)[0]]
    idx4 = data_store.get_sheet_indexes(
        sheet_name='V1_Exc_L4', neuron_ids=l4_exc_or_many)

    x = data_store.get_neuron_positions()['V1_Exc_L4'][0][idx4]
    y = data_store.get_neuron_positions()['V1_Exc_L4'][1][idx4]
    center4 = l4_exc_or_many[numpy.nonzero(numpy.sqrt(
        numpy.multiply(x, x)+numpy.multiply(y, y)) < 0.4)[0]]
    analog_center4 = set(center4).intersection(analog_ids)
    logger.info(str(analog_center4))

    if l23:
        x = data_store.get_neuron_positions()['V1_Exc_L2/3'][0][idx23]
        y = data_store.get_neuron_positions()['V1_Exc_L2/3'][1][idx23]
        center23 = l23_exc_or_many[numpy.nonzero(numpy.sqrt(
            numpy.multiply(x, x)+numpy.multiply(y, y)) < 0.4)[0]]
        analog_center23 = set(center23).intersection(analog_ids23)
        logger.info(str(analog_center23))

    if True:
        TrialAveragedFiringRate(param_filter_query(data_store, sheet_name=[
                                'V1_Exc_L4', 'V1_Exc_L2/3'], st_name='DriftingSinusoidalGratingDisk'), ParameterSet({})).analyse()

        dsv = param_filter_query(data_store, sheet_name=[
                                 'V1_Exc_L4', 'V1_Exc_L2/3'], st_name='DriftingSinusoidalGratingDisk')
        Analog_F0andF1(dsv, ParameterSet({})).analyse()

        dsv = param_filter_query(
            data_store, st_name='InternalStimulus', st_direct_stimulation_name=None)
        Analog_MeanSTDAndFanoFactor(dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(VM)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                 sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Vm')
        OperationPNVfromPNVS(pnv, lambda x, y: -(x+y),
                             '-(x+y)', dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                 sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
        OperationPNVfromPNVS(pnv, lambda x, y: x-y, 'x-y',
                             dsv, ParameterSet({})).analyse()

        pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L4', analysis_algorithm=[
                                 'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                 sheet_name='V1_Exc_L4', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
        OperationPNVfromPNVS(pnv, lambda x, y: x-y, 'x-y',
                             dsv, ParameterSet({})).analyse()

        if l23:
            pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                     'Analog_MeanSTDAndFanoFactor'], value_name='Mean(VM)', st_direct_stimulation_name=None).get_analysis_result()[0]
            dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                     sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Vm')
            OperationPNVfromPNVS(pnv, lambda x, y: -(x+y),
                                 '-(x+y)', dsv, ParameterSet({})).analyse()

            pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                     'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ECond)', st_direct_stimulation_name=None).get_analysis_result()[0]
            dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                     sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Exc_Cond')
            OperationPNVfromPNVS(pnv, lambda x, y: x-y,
                                 'x-y', dsv, ParameterSet({})).analyse()

            pnv = param_filter_query(data_store, st_name='InternalStimulus', sheet_name='V1_Exc_L2/3', analysis_algorithm=[
                                     'Analog_MeanSTDAndFanoFactor'], value_name='Mean(ICond)', st_direct_stimulation_name=None).get_analysis_result()[0]
            dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                     sheet_name='V1_Exc_L2/3', analysis_algorithm=['Analog_F0andF1'], value_name='F0_Inh_Cond')
            OperationPNVfromPNVS(pnv, lambda x, y: x-y,
                                 'x-y', dsv, ParameterSet({})).analyse()

        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk',
                                 analysis_algorithm='TrialAveragedFiringRate', value_name='Firing rate')
        SizeTuningAnalysis(dsv, ParameterSet(
            {'neurons': center4.tolist(), 'sheet_name': 'V1_Exc_L4'})).analyse()
        if l23:
            SizeTuningAnalysis(dsv, ParameterSet(
                {'neurons': center23.tolist(), 'sheet_name': 'V1_Exc_L2/3'})).analyse()
        data_store.save()
    
    if paper_figures:
        if l23:
            SizeTuningOverviewNew(data_store, ParameterSet({'l4_neurons': list(center4), 'l23_neurons': list(center23), 'l4_neurons_analog': list(
                analog_center4), 'l23_neurons_analog': list(analog_center23)}), plot_file_name='SizeTuning.png', fig_param={'dpi': dpi, 'figsize': (18, 11)}).plot()
        else:
            SizeTuningOverviewNew(data_store, ParameterSet({'l4_neurons': list(center4), 'l23_neurons': [], 'l4_neurons_analog': list(
                analog_center4), 'l23_neurons_analog': []}), plot_file_name='SizeTuning.png', fig_param={'dpi': dpi, 'figsize': (18, 11)}).plot()

    else:
        dsv = param_filter_query(data_store, st_name='DriftingSinusoidalGratingDisk', analysis_algorithm=[
                                 'TrialAveragedFiringRate'], value_name="Firing rate")
        PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'radius', 'neurons': list(center4), 'sheet_name': 'V1_Exc_L4', 'centered': False,
                                           'mean': False, 'polar': False, 'pool': False}), plot_file_name='SizeTuningExcL4.png', fig_param={'dpi': 100, 'figsize': (32, 7)}).plot()
        PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'radius', 'neurons': list(center4), 'sheet_name': 'V1_Exc_L4', 'centered': False,
                                           'mean': True, 'polar': False, 'pool': False}), plot_file_name='SizeTuningExcL4M.png', fig_param={'dpi': 100, 'figsize': (32, 7)}).plot()

        if l23:
            PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'radius', 'neurons': list(center23), 'sheet_name': 'V1_Exc_L2/3', 'centered': False,
                                               'mean': False, 'polar': False, 'pool': False}), plot_file_name='SizeTuningExcL23.png', fig_param={'dpi': 100, 'figsize': (32, 7)}).plot()
            PlotTuningCurve(dsv, ParameterSet({'parameter_name': 'radius', 'neurons': list(center23), 'sheet_name': 'V1_Exc_L2/3', 'centered': False,
                                               'mean': True, 'polar': False, 'pool': False}), plot_file_name='SizeTuningExcL23M.png', fig_param={'dpi': 100, 'figsize': (32, 7)}).plot()

        if True:
            dsv = param_filter_query(data_store, st_name=[
                                     'DriftingSinusoidalGratingDisk'])
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': list(analog_center4)[0], 'sheet_activity': {
            }, 'spontaneous': True}), fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='Overview_ExcL4_1.png').plot()

            if l23:
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L2/3', 'neuron': list(analog_center23)[0], 'sheet_activity': {
                }, 'spontaneous': True}), fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='Overview_ExcL23_1.png').plot()

        if l23:
            SizeTuningOverview(data_store, ParameterSet({'l4_neurons': list(center4), 'l23_neurons': list(center23), 'l4_neurons_analog': list(
                analog_center4), 'l23_neurons_analog': list(analog_center23)}), plot_file_name='SizeTuningOverview.png', fig_param={'dpi': 300, 'figsize': (18, 8)}).plot()
            SizeTuningOverviewNew(data_store, ParameterSet({'l4_neurons': list(center4), 'l23_neurons': list(center23), 'l4_neurons_analog': list(
                analog_center4), 'l23_neurons_analog': list(analog_center23)}), plot_file_name='SizeTuningOverviewNew.png', fig_param={'dpi': dpi, 'figsize': (18, 11)}).plot()
        else:
            SizeTuningOverview(data_store, ParameterSet({'l4_neurons': list(center4), 'l23_neurons': None, 'l4_neurons_analog': list(
                analog_center4), 'l23_neurons_analog': None}), plot_file_name='SizeTuningOverview.png', fig_param={'dpi': 300, 'figsize': (18, 8)}).plot()
            SizeTuningOverviewNew(data_store, ParameterSet({'l4_neurons': list(center4), 'l23_neurons': [], 'l4_neurons_analog': list(
                analog_center4), 'l23_neurons_analog': []}), plot_file_name='SizeTuningOverviewNew.png', fig_param={'dpi': dpi, 'figsize': (18, 11)}).plot()


def perform_analysis_and_visualization(data_store):

    sheets = list(set(data_store.sheets()) & set(
        ['V1_Exc_L4', 'V1_Inh_L4', 'V1_Exc_L2/3', 'V1_Inh_L2/3']))
    exc_sheets = list(set(data_store.sheets()) &
                      set(['V1_Exc_L4', 'V1_Exc_L2/3']))
    l23_flag = 'V1_Exc_L2/3' in set(sheets)

    NeuronAnnotationsToPerNeuronValues(data_store, ParameterSet({})).analyse()

    analog_ids = param_filter_query(data_store, sheet_name="V1_Exc_L4").get_segments()[
        0].get_stored_esyn_ids()
    analog_ids_inh = param_filter_query(
        data_store, sheet_name="V1_Inh_L4").get_segments()[0].get_stored_esyn_ids()
    spike_ids = param_filter_query(data_store, sheet_name="V1_Exc_L4").get_segments()[
        0].get_stored_spike_train_ids()
    spike_ids_inh = param_filter_query(data_store, sheet_name="V1_Inh_L4").get_segments()[
        0].get_stored_spike_train_ids()
    analog_ids_ON = param_filter_query(data_store,sheet_name="X_ON").get_segments()[0].get_stored_esyn_ids()
    analog_ids_OFF = param_filter_query(data_store,sheet_name="X_OFF").get_segments()[0].get_stored_esyn_ids()
    spike_ids_ON = param_filter_query(data_store, sheet_name="X_ON").get_segments()[
        0].get_stored_spike_train_ids()
    spike_ids_OFF = param_filter_query(data_store, sheet_name="X_OFF").get_segments()[
        0].get_stored_spike_train_ids()

    if l23_flag:
        analog_ids23 = param_filter_query(
            data_store, sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_esyn_ids()
        analog_ids_inh23 = param_filter_query(
            data_store, sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_esyn_ids()
        spike_ids23 = param_filter_query(
            data_store, sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_spike_train_ids()
        spike_ids_inh23 = param_filter_query(
            data_store, sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_spike_train_ids()
    else:
        analog_ids23 = None
        analog_ids_inh23 = None

    if l23_flag:
        l23_exc_or = data_store.get_analysis_result(
            identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Exc_L2/3')[0]
        l23_inh_or = data_store.get_analysis_result(
            identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Inh_L2/3')[0]

    l4_exc_or = data_store.get_analysis_result(
        identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Exc_L4')
    l4_exc_phase = data_store.get_analysis_result(
        identifier='PerNeuronValue', value_name='LGNAfferentPhase', sheet_name='V1_Exc_L4')
    l4_exc = analog_ids[numpy.argmin([circular_dist(o, 0, numpy.pi) for (o, p) in zip(
        l4_exc_or[0].get_value_by_id(analog_ids), l4_exc_phase[0].get_value_by_id(analog_ids))])]
    l4_inh_or = data_store.get_analysis_result(
        identifier='PerNeuronValue', value_name='LGNAfferentOrientation', sheet_name='V1_Inh_L4')
    l4_inh_phase = data_store.get_analysis_result(
        identifier='PerNeuronValue', value_name='LGNAfferentPhase', sheet_name='V1_Inh_L4')
    l4_inh = analog_ids_inh[numpy.argmin([circular_dist(o, 0, numpy.pi) for (o, p) in zip(
        l4_inh_or[0].get_value_by_id(analog_ids_inh), l4_inh_phase[0].get_value_by_id(analog_ids_inh))])]
    l4_exc_or_many = numpy.array(l4_exc_or[0].ids)[numpy.nonzero(numpy.array([circular_dist(
        o, 0, numpy.pi) for (o, p) in zip(l4_exc_or[0].values, l4_exc_phase[0].values)]) < 0.1)[0]]

    l4_exc_or_many = list(set(l4_exc_or_many) & set(spike_ids))

    if l23_flag:
        l23_exc_or_many = numpy.array(l23_exc_or.ids)[numpy.nonzero(numpy.array(
            [circular_dist(o, 0, numpy.pi) for o in l23_exc_or.values]) < 0.1)[0]]
        l23_exc_or_many = list(set(l23_exc_or_many) & set(spike_ids23))

    orr = list(set([MozaikParametrized.idd(s).orientation for s in queries.param_filter_query(
        data_store, st_name='FullfieldDriftingSinusoidalGrating', st_contrast=high_contrast).get_stimuli()]))

    l4_exc_or_many_analog = numpy.array(analog_ids)[numpy.nonzero(numpy.array(
        [circular_dist(l4_exc_or[0].get_value_by_id(i), 0, numpy.pi) for i in analog_ids]) < 0.1)[0]]
    l4_inh_or_many_analog = numpy.array(analog_ids_inh)[numpy.nonzero(numpy.array(
        [circular_dist(l4_inh_or[0].get_value_by_id(i), 0, numpy.pi) for i in analog_ids_inh]) < 0.15)[0]]

    if l23_flag:
        l23_inh_or_many_analog = numpy.array(analog_ids_inh23)[numpy.nonzero(numpy.array(
            [circular_dist(l23_inh_or.get_value_by_id(i), 0, numpy.pi) for i in analog_ids_inh23]) < 0.15)[0]]
        l23_exc_or_many_analog = numpy.array(analog_ids23)[numpy.nonzero(numpy.array(
            [circular_dist(l23_exc_or.get_value_by_id(i), 0, numpy.pi) for i in analog_ids23]) < 0.1)[0]]

    #if False:
    if True:
        if l23_flag:
            analysis(data_store, analog_ids, analog_ids_inh,
                     analog_ids23, analog_ids_inh23)
        else:
            analysis(data_store, analog_ids, analog_ids_inh)

    if True:  # PLOTTING
        activity_plot_param = {
            'frame_rate': 5,
            'bin_width': 5.0,
            'scatter':  True,
            'resolution': 0
        }
        if paper_figures:
            if l23_flag:
                OrientationTuningSummaryAnalogSignals(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'V1_Exc_L2/3', 'inh_sheet_name2': 'V1_Inh_L2/3'}), fig_param={
                                                      'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='FigureS3.png').plot({'*.fontsize': 19, '*.y_lim': (0, None)})
                OrientationTuningSummaryFiringRates(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'V1_Exc_L2/3', 'inh_sheet_name2': 'V1_Inh_L2/3'}), fig_param={
                                                    'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='FigureS2.png').plot({'*.fontsize': 19})
                TrialToTrialVariabilityComparisonNew(data_store, ParameterSet({'sheet_name1': 'V1_Exc_L4', 'sheet_name2': 'V1_Exc_L2/3', 'data_dg': 0.93, 'data_ni': 1.19}), fig_param={
                                                     'dpi': dpi, 'figsize': (15, 7.5)}, plot_file_name='FigureS5GHIJ.png').plot()
            else:
                OrientationTuningSummaryAnalogSignals(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'None', 'inh_sheet_name2': 'None'}), fig_param={
                                                      'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='FigureS3.png').plot({'*.fontsize': 19, '*.y_lim': (0, None)})
                OrientationTuningSummaryFiringRates(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'None', 'inh_sheet_name2': 'None'}), fig_param={
                                                    'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='FigureS2.png').plot({'*.fontsize': 19})
                TrialToTrialVariabilityComparisonNew(data_store, ParameterSet({'sheet_name1': 'V1_Exc_L4', 'sheet_name2': 'None', 'data_dg': 0.93, 'data_ni': 1.19}), fig_param={
                                                    'dpi': dpi, 'figsize': (15, 7.5)}, plot_file_name='FigureS5GHIJ.png').plot()


            if l23_flag:
                MRfigReal(param_filter_query(data_store, sheet_name=['V1_Exc_L2/3', 'V1_Exc_L4', 'V1_Inh_L2/3', 'V1_Inh_L4'], st_contrast=[high_contrast], st_name='FullfieldDriftingSinusoidalGrating'), ParameterSet(
                    {'SimpleSheetName': 'V1_Exc_L4', 'ComplexSheetName': 'V1_Exc_L2/3'}), plot_file_name='FigureS4.png', fig_param={'dpi': dpi, 'figsize': (20, 9)}).plot()
            else:
                MRfigReal(param_filter_query(data_store, sheet_name=['V1_Exc_L4', 'V1_Inh_L4'], st_contrast=[high_contrast], st_name='FullfieldDriftingSinusoidalGrating'), ParameterSet(
                    {'SimpleSheetName': 'V1_Exc_L4', 'ComplexSheetName': 'None'}), plot_file_name='FigureS4.png', fig_param={'dpi': dpi, 'figsize': (16, 12)}).plot()

            TrialCrossCorrelationAnalysis(data_store, ParameterSet({'neurons1': list(analog_ids), 'sheet_name1': 'V1_Exc_L4', 'neurons2': list(
                analog_ids23), 'sheet_name2': 'V1_Exc_L2/3', 'window_length': 250}), fig_param={"dpi": dpi, "figsize": (15, 6.5)}, plot_file_name="FigureS5CDE.png").plot({'*.Vm.title': None, '*.fontsize': 19})

            StimulusResponseComparison(data_store,ParameterSet({'neuron' : l4_exc_or_many_analog[17],'sheet_name' : 'V1_Exc_L4'}),fig_param={'dpi' : dpi,'figsize': (18,6)},plot_file_name='FigureS5AB.png').plot(
                                         {'*.Vm_plot.x_ticks':[0,2000],
                                         '*.Conductance_plot.x_ticks':[0,2000],
                                         "*.title" : None,
                                         '*.Vm_plot.y_lim' : (-80,-50),
                                         '*.Conductance_plot.y_lim' : (0,50),
                                         })

        else:
            ## self sustained plotting
            dsv = param_filter_query(data_store, st_name=[
                                     'InternalStimulus'], st_direct_stimulation_name=None)
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[0], 'sheet_activity': {
            }, 'spontaneous': True}), fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSExcAnalog.png').plot()
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neuron': analog_ids_inh[0], 'sheet_activity': {
            }, 'spontaneous': True}), fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSInhAnalog.png').plot()

            RasterPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neurons': spike_ids, 'trial_averaged_histogram': False, 'spontaneous': False}), fig_param={
                       'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSExcRasterL4.png').plot({'SpikeRasterPlot.group_trials': True})
            RasterPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neurons': spike_ids_inh, 'trial_averaged_histogram': False, 'spontaneous': False}), fig_param={
                       'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSInhRasterL4.png').plot({'SpikeRasterPlot.group_trials': True})
            if l23_flag:
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L2/3', 'neuron': analog_ids23[0], 'sheet_activity': {
                }, 'spontaneous': True}), fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSExcAnalog23.png').plot()
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L2/3', 'neuron': analog_ids_inh23[0], 'sheet_activity': {
                }, 'spontaneous': True}), fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSInhAnalog23.png').plot()

                RasterPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L2/3', 'neurons': spike_ids23, 'trial_averaged_histogram': False, 'spontaneous': False}),
                           fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSExcRasterL23.png').plot({'SpikeRasterPlot.group_trials': True})
                RasterPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L2/3', 'neurons': spike_ids_inh23, 'trial_averaged_histogram': False, 'spontaneous': False}),
                           fig_param={'dpi': 100, 'figsize': (28, 12)}, plot_file_name='SSInhRasterL23.png').plot({'SpikeRasterPlot.group_trials': True})


            dsv = param_filter_query(
                data_store, st_name='FullfieldDriftingSinusoidalGrating')
            RasterPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neurons': spike_ids, 'trial_averaged_histogram': False, 'spontaneous': False}), fig_param={
                       'dpi': 100, 'figsize': (28, 12)}, plot_file_name='EvokedExcRaster.png').plot({'SpikeRasterPlot.group_trials': True})
            RasterPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neurons': spike_ids_inh, 'trial_averaged_histogram': False, 'spontaneous': False}), fig_param={
                       'dpi': 100, 'figsize': (28, 12)}, plot_file_name='EvokedInhRaster.png').plot({'SpikeRasterPlot.group_trials': True})


            dsv = param_filter_query(
                data_store, st_name='FullfieldDriftingSinusoidalGrating', st_orientation=[0, numpy.pi/2])
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': l4_exc, 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Exc.png").plot({'Vm_plot.y_lim': (-80, -50)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neuron': l4_inh, 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Inh.png").plot({'Vm_plot.y_lim': (-80, -50)})
            
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[0], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Exc1.png").plot({'Vm_plot.y_lim': (-80, -50)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[1], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Exc2.png").plot({'Vm_plot.y_lim': (-80, -50)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[2], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Exc3.png").plot({'Vm_plot.y_lim': (-80, -50)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[3], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Exc4.png").plot({'Vm_plot.y_lim': (-80, -50)})

            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neuron': analog_ids_inh[0], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Inh1.png").plot({'Vm_plot.y_lim': (-80, -50)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neuron': analog_ids_inh[1], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Inh2.png").plot({'Vm_plot.y_lim': (-80, -50)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neuron': analog_ids_inh[2], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                         'dpi': 100, 'figsize': (25, 12)}, plot_file_name="Inh3.png").plot({'Vm_plot.y_lim': (-80, -50)})

            if l23_flag:
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L2/3', 'neuron': analog_ids23[0], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                             'dpi': 100, 'figsize': (25, 12)}, plot_file_name="ExcL231.png").plot({'Vm_plot.y_lim': (-80, -50)})
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L2/3', 'neuron': analog_ids23[1], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                             'dpi': 100, 'figsize': (25, 12)}, plot_file_name="ExcL232.png").plot({'Vm_plot.y_lim': (-80, -50)})
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L2/3', 'neuron': analog_ids23[2], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                             'dpi': 100, 'figsize': (25, 12)}, plot_file_name="ExcL233.png").plot({'Vm_plot.y_lim': (-80, -50)})

                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L2/3', 'neuron': analog_ids_inh23[0], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                             'dpi': 100, 'figsize': (25, 12)}, plot_file_name="InhL231.png").plot({'Vm_plot.y_lim': (-80, -50)})
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L2/3', 'neuron': analog_ids_inh23[1], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                             'dpi': 100, 'figsize': (25, 12)}, plot_file_name="InhL232.png").plot({'Vm_plot.y_lim': (-80, -50)})
                OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L2/3', 'neuron': analog_ids_inh23[2], 'sheet_activity': {}, 'spontaneous': True}), fig_param={
                             'dpi': 100, 'figsize': (25, 12)}, plot_file_name="InhL233.png").plot({'Vm_plot.y_lim': (-80, -50)})

            if l23_flag:
                SpontActOverview(data_store, ParameterSet({'l4_exc_neuron': analog_ids[0], 'l4_inh_neuron': analog_ids_inh[0], 'l23_exc_neuron': analog_ids23[
                                 0], 'l23_inh_neuron': analog_ids_inh23[0]}), plot_file_name='SpontActOverview.png', fig_param={'dpi': dpi, 'figsize': (18, 14.5)}).plot()
                OrientationTuningSummaryAnalogSignals(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'V1_Exc_L2/3', 'inh_sheet_name2': 'V1_Inh_L2/3'}), fig_param={
                                                      'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='OrientationTuningSummaryAnalogSignals.png').plot({'*.fontsize': 19, '*.y_lim': (0, None)})
                OrientationTuningSummaryFiringRates(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'V1_Exc_L2/3', 'inh_sheet_name2': 'V1_Inh_L2/3'}), fig_param={
                                                    'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='OrientationTuningSummary.png').plot({'*.fontsize': 19})
                TrialToTrialVariabilityComparisonNew(data_store, ParameterSet({'sheet_name1': 'V1_Exc_L4', 'sheet_name2': 'V1_Exc_L2/3', 'data_dg': 0.93, 'data_ni': 1.19}), fig_param={
                                                     'dpi': dpi, 'figsize': (15, 7.5)}, plot_file_name='TrialToTrialVariabilityComparisonNew.png').plot()
            else:
                SpontActOverview(data_store, ParameterSet({'l4_exc_neuron': analog_ids[0], 'l4_inh_neuron': analog_ids_inh[0], 'l23_exc_neuron': -1,
                                                           'l23_inh_neuron': -1}), plot_file_name='SpontActOverview.png', fig_param={'dpi': dpi, 'figsize': (18, 14.5)}).plot()
                OrientationTuningSummaryAnalogSignals(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'None', 'inh_sheet_name2': 'None'}), fig_param={
                                                      'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='OrientationTuningSummaryAnalogSignals.png').plot({'*.fontsize': 19, '*.y_lim': (0, None)})
                OrientationTuningSummaryFiringRates(data_store, ParameterSet({'exc_sheet_name1': 'V1_Exc_L4', 'inh_sheet_name1': 'V1_Inh_L4', 'exc_sheet_name2': 'None', 'inh_sheet_name2': 'None'}), fig_param={
                                                    'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='OrientationTuningSummary.png').plot({'*.fontsize': 19})
                TrialToTrialVariabilityComparisonNew(data_store, ParameterSet({'sheet_name1': 'V1_Exc_L4', 'sheet_name2': 'None', 'data_dg': 0.93, 'data_ni': 1.19}), fig_param={
                                                    'dpi': dpi, 'figsize': (15, 7.5)}, plot_file_name='TrialToTrialVariabilityComparisonNew.png').plot()


            SpontStatisticsOverview(data_store, ParameterSet({}), fig_param={
                                    'dpi': dpi, 'figsize': (18, 12)}, plot_file_name='SpontStatisticsOverview.png').plot()

            if l23_flag:
                MRfigReal(param_filter_query(data_store, sheet_name=['V1_Exc_L2/3', 'V1_Exc_L4', 'V1_Inh_L2/3', 'V1_Inh_L4'], st_contrast=[high_contrast], st_name='FullfieldDriftingSinusoidalGrating'), ParameterSet(
                    {'SimpleSheetName': 'V1_Exc_L4', 'ComplexSheetName': 'V1_Exc_L2/3'}), plot_file_name='MRReal.png', fig_param={'dpi': dpi, 'figsize': (20, 9)}).plot()
            else:
                MRfigReal(param_filter_query(data_store, sheet_name=['V1_Exc_L4', 'V1_Inh_L4'], st_contrast=[high_contrast], st_name='FullfieldDriftingSinusoidalGrating'), ParameterSet(
                    {'SimpleSheetName': 'V1_Exc_L4', 'ComplexSheetName': 'None'}), plot_file_name='MRReal.png', fig_param={'dpi': dpi, 'figsize': (16, 12)}).plot()

            dsv = param_filter_query(
                data_store, st_name='NaturalImageWithEyeMovement')
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': l4_exc, 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMExc.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[0], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMExc1.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[1], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMExc2.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[2], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMExc3.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[3], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMExc4.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Exc_L4', 'neuron': analog_ids[4], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMExc5.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'V1_Inh_L4', 'neuron': l4_inh, 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMInh.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_ON', 'neuron': analog_ids_ON[0], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMON1.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_ON', 'neuron': analog_ids_ON[1], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMON2.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_ON', 'neuron': analog_ids_ON[2], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMON3.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_ON', 'neuron': analog_ids_ON[3], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMON4.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_ON', 'neuron': analog_ids_ON[4], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMON5.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_OFF', 'neuron': analog_ids_OFF[0], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMOFF1.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_OFF', 'neuron': analog_ids_OFF[1], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMOFF2.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_OFF', 'neuron': analog_ids_OFF[2], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMOFF3.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_OFF', 'neuron': analog_ids_OFF[3], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMOFF4.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})
            OverviewPlot(dsv, ParameterSet({'sheet_name': 'X_OFF', 'neuron': analog_ids_OFF[4], 'sheet_activity': {}, 'spontaneous': True}), plot_file_name='NMOFF5.png', fig_param={
                         'dpi': 100, 'figsize': (28, 12)}).plot({'Vm_plot.y_lim': (-70, -50), 'Conductance_plot.y_lim': (0, 50.0)})

            TrialCrossCorrelationAnalysis(data_store, ParameterSet({'neurons1': list(analog_ids), 'sheet_name1': 'V1_Exc_L4', 'neurons2': list(
                analog_ids23), 'sheet_name2': 'V1_Exc_L2/3', 'window_length': 250}), fig_param={"dpi": dpi, "figsize": (15, 6.5)}, plot_file_name="trial-to-trial-cross-correlation.png").plot({'*.Vm.title': None, '*.fontsize': 19})

            dsv = queries.param_filter_query(data_store, value_name=[
                                             'orientation HWHH of Firing rate', 'orientation CV(Firing rate)'], sheet_name=["V1_Exc_L2/3"], st_contrast=high_contrast)
            PerNeuronValueScatterPlot(dsv, ParameterSet({'only_matching_units': False, 'ignore_nan': True, 'lexicographic_order': False, 'neuron_ids':[]}), plot_file_name='CVvsHWHH.png').plot(
                {'*.x_lim': (0, 90), '*.y_lim': (0, 1.0)})


            # orientation tuning plotting
            dsv = param_filter_query(data_store,sheet_name=['V1_Exc_L4','V1_Inh_L4'],value_name='LGNAfferentOrientation')
            PerNeuronValuePlot(dsv,ParameterSet({"cortical_view" : True}),plot_file_name='ORSet.png').plot()

            LSV1MReponseOverview(data_store,ParameterSet
            ({'l4_exc_neuron' : l4_exc_or_many_analog[0], 'l4_inh_neuron' : l4_inh_or_many_analog[3],'l23_exc_neuron' : l23_exc_or_many_analog[5], 'l23_inh_neuron' : l23_inh_or_many_analog[2]}),
                                             fig_param={'dpi' : dpi,'figsize': (18,9)},plot_file_name='SingleCellOverview.png').plot(
                                                {'*.Vm_plot.x_ticks':[0,2000],
                                                 '*.Conductance_plot.x_ticks':[0,2000],
                                                 "*.title" : None,
                                                 '*.Vm_plot.y_lim' : (-80,-50),
                                                 'ExcOr0L4.Conductance_plot.y_lim' : (0,15),
                                                 'ExcOrPiL4.Conductance_plot.y_lim' : (0,15),
                                                 'InhOr0L4.Conductance_plot.y_lim' : (0,15),
                                                 'InhOrPiL4.Conductance_plot.y_lim' : (0,15),
                                                 'ExcOr0L23.Conductance_plot.y_lim' : (0,70),
                                                 'ExcOrPiL23.Conductance_plot.y_lim' : (0,70),
                                                 'InhOr0L23.Conductance_plot.y_lim' : (0,70),
                                                 'InhOrPiL23.Conductance_plot.y_lim' : (0,70),
                                                 })

            StimulusResponseComparison(data_store,ParameterSet({'neuron' : l4_exc_or_many_analog[22],'sheet_name' : 'V1_Exc_L4'}),fig_param={'dpi' : dpi,'figsize': (18,6)},plot_file_name='StimulusResponseComparison1L4.png').plot(
                                         {'*.Vm_plot.x_ticks':[0,2000], 
                                         '*.Conductance_plot.x_ticks':[0,2000], 
                                         "*.title" : None,
                                         '*.Vm_plot.y_lim' : (-80,-50),
                                         '*.Conductance_plot.y_lim' : (0,30),
                                         })

            OrientationMapMatching(data_store,ParameterSet({}), plot_file_name='OrientationComparison.png',fig_param={'dpi' : dpi,'figsize': (6,6)}).plot()


def perform_analysis_and_visualization_spont(data_store):
    sheets = list(set(data_store.sheets()) & set(['V1_Exc_L4','V1_Inh_L4','V1_Exc_L2/3','V1_Inh_L2/3']))
    exc_sheets = list(set(data_store.sheets()) & set(['V1_Exc_L4', 'V1_Exc_L2/3']))

    l23_flag = 'V1_Exc_L2/3' in set(sheets)

    analog_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_esyn_ids()
    analog_ids_inh = param_filter_query(data_store,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_esyn_ids()
    spike_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids()
    spike_ids_inh = param_filter_query(data_store,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_spike_train_ids()

    if l23_flag:

        analog_ids23 = param_filter_query(data_store,sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_esyn_ids()
        analog_ids_inh23 = param_filter_query(data_store,sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_esyn_ids()
        spike_ids23 = param_filter_query(data_store,sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_spike_train_ids()
        spike_ids_inh23 = param_filter_query(data_store,sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_spike_train_ids()
    else:
        analog_ids23 = []
        analog_ids_inh23 = []
        spike_ids23 = []
        spike_ids_inh23 = []
    
    if True:
        TrialAveragedFiringRate(data_store,ParameterSet({})).analyse()
        Analog_MeanSTDAndFanoFactor(param_filter_query(data_store,st_direct_stimulation_name=None),ParameterSet({})).analyse()
        TrialAveragedVarianceAndVarianceRatioOfConductances(param_filter_query(data_store,st_direct_stimulation_name=None),ParameterSet({})).analyse()
        PSTH(param_filter_query(data_store,st_direct_stimulation_name=None),ParameterSet({'bin_length' : 10.0})).analyse()
        Irregularity(param_filter_query(data_store,st_direct_stimulation_name=None),ParameterSet({})).analyse()
        CrossCorrelationOfExcitatoryAndInhibitoryConductances(param_filter_query(data_store,st_direct_stimulation_name=None),ParameterSet({})).analyse()
        NeuronToNeuronAnalogSignalCorrelations(param_filter_query(data_store,analysis_algorithm='PSTH'),ParameterSet({'convert_nan_to_zero' : True})).analyse()

        dsv = param_filter_query(data_store,st_direct_stimulation_name=None,st_name="InternalStimulus",sheet_name=sheets,identifier='PerNeuronValue')
        dsv.print_content()
        PopulationMeanAndVar(dsv,ParameterSet({'ignore_nan_and_inf': False})).analyse()

        data_store.save()
    
    if paper_figures:
        if l23_flag:
            SpontActOverview(data_store,ParameterSet({'l4_exc_neuron' : analog_ids[0], 'l4_inh_neuron' : analog_ids_inh[0],'l23_exc_neuron' : analog_ids23[0],'l23_inh_neuron' : analog_ids_inh23[0]}),plot_file_name='SpontActOverview.png', fig_param={'dpi' : dpi,'figsize': (15,12)}).plot()
            SpontStatisticsOverview(data_store,ParameterSet({}), fig_param={'dpi' : dpi,'figsize': (15,10)},plot_file_name='FigureS1.png').plot()
        else:
            SpontActOverview(data_store,ParameterSet({'l4_exc_neuron' : analog_ids[0], 'l4_inh_neuron' : analog_ids_inh[0],'l23_exc_neuron' : -1,'l23_inh_neuron' : -1}),plot_file_name='SpontAcOverview.png', fig_param={'dpi' : dpi,'figsize': (15,12)}).plot()
            SpontStatisticsOverview(data_store,ParameterSet({}), fig_param={'dpi' : dpi,'figsize': (15,10)},plot_file_name='FigureS1.png').plot()

    else:
        dsv = param_filter_query(data_store,st_name=['InternalStimulus'],st_direct_stimulation_name=None)
        OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neuron' : analog_ids[0], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSExcAnalogL4.png').plot()
        OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neuron' : analog_ids_inh[0], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSInhAnalogL4.png').plot()

        RasterPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L4', 'neurons' : spike_ids,'trial_averaged_histogram': False, 'spontaneous' : False}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSExcRasterL4.png').plot({'SpikeRasterPlot.group_trials':True})
        RasterPlot(dsv,ParameterSet({'sheet_name' : 'V1_Inh_L4', 'neurons' : spike_ids_inh,'trial_averaged_histogram': False, 'spontaneous' : False}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSInhRasterL4.png').plot({'SpikeRasterPlot.group_trials':True})

        if l23_flag:
            dsv = param_filter_query(data_store,st_name=['InternalStimulus'],st_direct_stimulation_name=None)
            OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L2/3', 'neuron' : analog_ids23[0], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSExcAnalogL23.png').plot()
            OverviewPlot(dsv,ParameterSet({'sheet_name' : 'V1_Inh_L2/3', 'neuron' : analog_ids_inh23[0], 'sheet_activity' : {}, 'spontaneous' : True}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSInhAnalogL23.png').plot()

            RasterPlot(dsv,ParameterSet({'sheet_name' : 'V1_Exc_L2/3', 'neurons' : spike_ids23,'trial_averaged_histogram': False, 'spontaneous' : False}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSExcRasterL23.png').plot({'SpikeRasterPlot.group_trials':True})
            RasterPlot(dsv,ParameterSet({'sheet_name' : 'V1_Inh_L2/3', 'neurons' : spike_ids_inh23,'trial_averaged_histogram': False, 'spontaneous' : False}),fig_param={'dpi' : 100,'figsize': (28,12)},plot_file_name='SSInhRasterL23.png').plot({'SpikeRasterPlot.group_trials':True})


        if l23_flag:
            SpontActOverview(data_store,ParameterSet({'l4_exc_neuron' : analog_ids[0], 'l4_inh_neuron' : analog_ids_inh[0],'l23_exc_neuron' : analog_ids23[0],'l23_inh_neuron' : analog_ids_inh23[0]}),plot_file_name='SpontActOverview.png', fig_param={'dpi' : dpi,'figsize': (15,12)}).plot()
            SpontStatisticsOverview(data_store,ParameterSet({}), fig_param={'dpi' : dpi,'figsize': (15,10)},plot_file_name='SpontStatisticsOverview.png').plot()
        else:
            SpontActOverview(data_store,ParameterSet({'l4_exc_neuron' : analog_ids[0], 'l4_inh_neuron' : analog_ids_inh[0],'l23_exc_neuron' : -1,'l23_inh_neuron' : -1}),plot_file_name='SpontActOverview.png', fig_param={'dpi' : dpi,'figsize': (15,12)}).plot()
            SpontStatisticsOverview(data_store,ParameterSet({}), fig_param={'dpi' : dpi,'figsize': (15,10)},plot_file_name='SpontStatisticsOverview.png').plot()

def perform_analysis_and_visualization_STW(data_store):
    sheets = list(set(data_store.sheets()) & set(['V1_Exc_L4','V1_Inh_L4','V1_Exc_L2/3','V1_Inh_L2/3']))
    analyzed_sheets = ['V1_Exc_L2/3']

    l23_flag = 'V1_Exc_L2/3' in set(sheets)

    analog_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_esyn_ids()
    analog_ids_inh = param_filter_query(data_store,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_esyn_ids()
    spike_ids = param_filter_query(data_store,sheet_name="V1_Exc_L4").get_segments()[0].get_stored_spike_train_ids()
    spike_ids_inh = param_filter_query(data_store,sheet_name="V1_Inh_L4").get_segments()[0].get_stored_spike_train_ids()

    if l23_flag:

        analog_ids23 = param_filter_query(data_store,sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_esyn_ids()
        analog_ids_inh23 = param_filter_query(data_store,sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_esyn_ids()
        spike_ids23 = param_filter_query(data_store,sheet_name="V1_Exc_L2/3").get_segments()[0].get_stored_spike_train_ids()
        spike_ids_inh23 = param_filter_query(data_store,sheet_name="V1_Inh_L2/3").get_segments()[0].get_stored_spike_train_ids()
    else:
        analog_ids23 = []
        analog_ids_inh23 = []
        spike_ids23 = []
        spike_ids_inh23 = []
    
    points_distance = 50
    gaussian_sigma = 5 
    if True:
        NeuronAnnotationsToPerNeuronValues(data_store, ParameterSet({})).analyse()
        TrialAveragedFiringRate(data_store,ParameterSet({})).analyse()
        PSTH(param_filter_query(data_store,sheet_name=analyzed_sheets),ParameterSet({'bin_length': 10.0})).analyse()
        Analog_MeanSTDAndFanoFactor(param_filter_query(data_store,sheet_name=analyzed_sheets,st_direct_stimulation_name=None),ParameterSet({})).analyse()
        Irregularity(param_filter_query(data_store,st_direct_stimulation_name=None),ParameterSet({})).analyse()

        LFPFromSynapticCurrents(param_filter_query(data_store, sheet_name= analyzed_sheets, st_direct_stimulation_name=None,
                                            st_name='InternalStimulus'), ParameterSet({'downsampling': 1, 'points_distance': points_distance, 'gaussian_convolution':False,'gaussian_sigma':gaussian_sigma,'cropped_length': 5000,'normalization_per_channel': False})).analyse()
        LFPFromSynapticCurrents(param_filter_query(data_store, sheet_name= analyzed_sheets, st_direct_stimulation_name=None,
                                            st_name='InternalStimulus'), ParameterSet({'downsampling': 1, 'points_distance': points_distance, 'gaussian_convolution':True,'gaussian_sigma':gaussian_sigma,'cropped_length': 5000,'normalization_per_channel': False})).analyse()
        LFPFromSynapticCurrents(param_filter_query(data_store, sheet_name= analyzed_sheets, st_direct_stimulation_name=None,
                                            st_name='InternalStimulus'), ParameterSet({'downsampling': 1, 'points_distance': points_distance, 'gaussian_convolution':True,'gaussian_sigma':gaussian_sigma,'cropped_length': 4000,'normalization_per_channel': False})).analyse()
        LFPFromSynapticCurrents(param_filter_query(data_store, sheet_name= analyzed_sheets, st_direct_stimulation_name=None,
                                            st_name='InternalStimulus'), ParameterSet({'downsampling': 1, 'points_distance': points_distance, 'gaussian_convolution':False,'gaussian_sigma':gaussian_sigma,'cropped_length': 4000,'normalization_per_channel': False})).analyse()
        LFPFromSynapticCurrents(param_filter_query(data_store, sheet_name= analyzed_sheets, st_direct_stimulation_name=None,
                                                   st_name='InternalStimulus'), ParameterSet({'downsampling': 1, 'points_distance': points_distance, 'gaussian_convolution':True,'gaussian_sigma':gaussian_sigma,'cropped_length': 5000,'normalization_per_channel': True})).analyse()
        ButterworthFiltering(param_filter_query(data_store, sheet_name= analyzed_sheets, st_direct_stimulation_name=None,
                                        st_name='InternalStimulus',identifier='PerAreaAnalogSignalList',analysis_algorithm='LFPFromSynapticCurrents'),
                                        ParameterSet({'order': 4, 'type': 'band', 'low_frequency': 5, 'high_frequency':100,'vm':False,'cond_exc':False,'cond_inh':False})).analyse()

        GeneralizedPhase(param_filter_query(data_store, sheet_name=analyzed_sheets, st_direct_stimulation_name=None,
                                            st_name='InternalStimulus',identifier='PerAreaAnalogSignalList',analysis_algorithm=['ButterworthFiltering','LFPFromPSTH']), ParameterSet({'threshold':0.8})).analyse()
        AreaOrientationLabeling(param_filter_query(data_store, sheet_name=analyzed_sheets,identifier='PerAreaAnalogSignalList',analysis_algorithm='LFPFromSynapticCurrents',y_axis_name='LFP'), ParameterSet({'map_file': 'or_map_new_16x16', 'cropped_length': 5000})).analyse()
       
        NauhausAnalysis(param_filter_query(data_store, sheet_name=analyzed_sheets), ParameterSet({'points_distance':points_distance,'electrodes_spacing':400,'n_neurons':330,'duration_analysis':20,'cropped_length': 4000, 'paasl_name': 'Butterworth band-pass filtered of (LFP) freq=[5,100], order = 4','time_correction':0})).analyse()
        data_store.save()

    if paper_figures:
       SpontaneousDynamics(data_store,ParameterSet({'sheet_name': analyzed_sheets[0]}), fig_param={'dpi' : 200,'figsize': (18,15)},plot_file_name='Figure2CDFG.png').plot()
       OrientationBiasSpikeTriggeredLFPResiduals(data_store,ParameterSet({'sheet_name': analyzed_sheets[0]}), fig_param={'dpi' : 200,'figsize': (13,11)},plot_file_name='Figure2K.png').plot()
    else:
       SpontaneousDynamics(data_store,ParameterSet({'sheet_name': analyzed_sheets[0]}), fig_param={'dpi' : 200,'figsize': (18,15)},plot_file_name='SpontDynamics.png').plot()
       OrientationBiasSpikeTriggeredLFPResiduals(data_store,ParameterSet({'sheet_name': analyzed_sheets[0]}), fig_param={'dpi' : 200,'figsize': (13,11)},plot_file_name='STLFPResiduals.png').plot()

