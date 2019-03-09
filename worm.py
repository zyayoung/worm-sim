# GoPiGo Connectome
# Written by Timothy Busbice, Gabriel Garrett, Geoffrey Churchill (c) 2014, in Python 2.7
# The GoPiGo Connectome uses a self.postSynaptic dictionary based on the C Elegans Connectome Model
# This application can be ran on the Raspberry Pi GoPiGo robot with a Sonar that represents Nose Touch when activated
# To run standalone without a GoPiGo robot, simply comment out the sections with Start and End comments 

#TIME STATE EXPERIMENTAL OPTIMIZATION
#The previous version had a logic error whereby if more than one neuron fired into the same neuron in the next time state,
# it would overwrite the contribution from the previous neuron. Thus, only one neuron could fire into the same neuron at any given time state.
# This version also explicitly lists all left and right muscles, so that during the muscle checks for the motor control function, instead of 
# iterating through each neuron, we now iterate only through the relevant muscle neurons.

# three levels of verbosity: [], -v, -vv
# 0: only print starting and exiting messages
# 1: print only when obstacles/food found
# 2: print speed, left and right every time


import time
import copy
import signal
import sys

class Worm:
    disembodied = False
    verbosity = False

    action = 0

    us_dist = 18
    speed = 0

    
    def fwd(self, ):
        self.action = 1

    def bwd(self, ):
        self.action = 2

    def left_rot(self, ):
        self.action = 3

    def right_rot(self, ):
        self.action = 4

    def stop(self, ):
        self.action = 5

    def set_speed(self, v):
        self.speed = v

    # The self.postSynaptic dictionary contains the accumulated weighted values as the
    # connectome is executed
    postSynaptic = {}

    thisState = 0 
    nextState = 1

    # The Threshold is the maximum sccumulated value that must be exceeded before
    # the Neurite will fire
    threshold = 30

    # Accumulators are used to decide the value to send to the Left and Right motors
    # of the GoPiGo robot
    accumleft = 0
    accumright = 0

    # Used to remove from Axon firing since muscles cannot fire.
    muscles = ['MVU', 'MVL', 'MDL', 'MVR', 'MDR']

    muscleList = ['MDL07', 'MDL08', 'MDL09', 'MDL10', 'MDL11', 'MDL12', 'MDL13', 'MDL14', 'MDL15', 'MDL16', 'MDL17', 'MDL18', 'MDL19', 'MDL20', 'MDL21', 'MDL22', 'MDL23', 'MVL07', 'MVL08', 'MVL09', 'MVL10', 'MVL11', 'MVL12', 'MVL13', 'MVL14', 'MVL15', 'MVL16', 'MVL17', 'MVL18', 'MVL19', 'MVL20', 'MVL21', 'MVL22', 'MVL23', 'MDR07', 'MDR08', 'MDR09', 'MDR10', 'MDR11', 'MDR12', 'MDR13', 'MDR14', 'MDR15', 'MDR16', 'MDR17', 'MDR18', 'MDR19', 'MDR20', 'MDL21', 'MDR22', 'MDR23', 'MVR07', 'MVR08', 'MVR09', 'MVR10', 'MVR11', 'MVR12', 'MVR13', 'MVR14', 'MVR15', 'MVR16', 'MVR17', 'MVR18', 'MVR19', 'MVR20', 'MVL21', 'MVR22', 'MVR23']

    mLeft = ['MDL07', 'MDL08', 'MDL09', 'MDL10', 'MDL11', 'MDL12', 'MDL13', 'MDL14', 'MDL15', 'MDL16', 'MDL17', 'MDL18', 'MDL19', 'MDL20', 'MDL21', 'MDL22', 'MDL23', 'MVL07', 'MVL08', 'MVL09', 'MVL10', 'MVL11', 'MVL12', 'MVL13', 'MVL14', 'MVL15', 'MVL16', 'MVL17', 'MVL18', 'MVL19', 'MVL20', 'MVL21', 'MVL22', 'MVL23']
    mRight = ['MDR07', 'MDR08', 'MDR09', 'MDR10', 'MDR11', 'MDR12', 'MDR13', 'MDR14', 'MDR15', 'MDR16', 'MDR17', 'MDR18', 'MDR19', 'MDR20', 'MDL21', 'MDR22', 'MDR23', 'MVR07', 'MVR08', 'MVR09', 'MVR10', 'MVR11', 'MVR12', 'MVR13', 'MVR14', 'MVR15', 'MVR16', 'MVR17', 'MVR18', 'MVR19', 'MVR20', 'MVL21', 'MVR22', 'MVR23']
    # Used to accumulate muscle weighted values in body muscles 07-23 = worm locomotion
    musDleft = ['MDL07', 'MDL08', 'MDL09', 'MDL10', 'MDL11', 'MDL12', 'MDL13', 'MDL14', 'MDL15', 'MDL16', 'MDL17', 'MDL18', 'MDL19', 'MDL20', 'MDL21', 'MDL22', 'MDL23']
    musVleft = ['MVL07', 'MVL08', 'MVL09', 'MVL10', 'MVL11', 'MVL12', 'MVL13', 'MVL14', 'MVL15', 'MVL16', 'MVL17', 'MVL18', 'MVL19', 'MVL20', 'MVL21', 'MVL22', 'MVL23']
    musDright = ['MDR07', 'MDR08', 'MDR09', 'MDR10', 'MDR11', 'MDR12', 'MDR13', 'MDR14', 'MDR15', 'MDR16', 'MDR17', 'MDR18', 'MDR19', 'MDR20', 'MDL21', 'MDR22', 'MDR23']
    musVright = ['MVR07', 'MVR08', 'MVR09', 'MVR10', 'MVR11', 'MVR12', 'MVR13', 'MVR14', 'MVR15', 'MVR16', 'MVR17', 'MVR18', 'MVR19', 'MVR20', 'MVL21', 'MVR22', 'MVR23']

    """This is the full C Elegans Connectome as expresed in the form of the Presynatptic
    neurite and the self.postSynaptic neurites.

    self.postSynaptic['ADAR'][self.nextState] = (2 + self.postSynaptic['ADAR'][thisState])
    arr=self.postSynaptic['AIBR'] potential optimization
    """

    def ADAL(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 2
            self.postSynaptic['ADFL'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 2
            self.postSynaptic['ASHL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 4
            self.postSynaptic['AVBR'][self.nextState] += 7
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 5
            self.postSynaptic['FLPR'][self.nextState] += 1
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 3
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 2

    def ADAR(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['ADFR'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 5
            self.postSynaptic['AVDL'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 3
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RIMR'][self.nextState] += 5
            self.postSynaptic['RIPR'][self.nextState] += 1
            self.postSynaptic['RIVR'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 2

    def ADEL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['AINL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['BDUL'][self.nextState] += 1
            self.postSynaptic['CEPDL'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['IL1L'][self.nextState] += 1
            self.postSynaptic['IL2L'][self.nextState] += 1
            self.postSynaptic['MDL05'][self.nextState] += 1
            self.postSynaptic['OLLL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIFL'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 5
            self.postSynaptic['RIGR'][self.nextState] += 3
            self.postSynaptic['RIH'][self.nextState] += 2
            self.postSynaptic['RIVL'][self.nextState] += 1
            self.postSynaptic['RIVR'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 2
            self.postSynaptic['RMGL'][self.nextState] += 1
            self.postSynaptic['RMHL'][self.nextState] += 1
            self.postSynaptic['SIADR'][self.nextState] += 1
            self.postSynaptic['SIBDR'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['URBL'][self.nextState] += 1

    def ADER(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['ADEL'][self.nextState] += 2
            self.postSynaptic['ALA'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 2
            self.postSynaptic['AVKR'][self.nextState] += 1
            self.postSynaptic['CEPDR'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['FLPR'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 2
            self.postSynaptic['PVR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 7
            self.postSynaptic['RIGR'][self.nextState] += 4
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 2
            self.postSynaptic['SAAVR'][self.nextState] += 1

    def ADFL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 2
            self.postSynaptic['AIZL'][self.nextState] += 12
            self.postSynaptic['AUAL'][self.nextState] += 5
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 15
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 2
            self.postSynaptic['SMBVL'][self.nextState] += 2

    def ADFR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 2
            self.postSynaptic['AIAR'][self.nextState] += 1
            self.postSynaptic['AIYR'][self.nextState] += 1
            self.postSynaptic['AIZR'][self.nextState] += 8
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['AUAR'][self.nextState] += 4
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 16
            self.postSynaptic['RIGR'][self.nextState] += 3
            self.postSynaptic['RIR'][self.nextState] += 3
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['SMBVR'][self.nextState] += 2
            self.postSynaptic['URXR'][self.nextState] += 1

    def ADLL(self, ):
            self.postSynaptic['ADLR'][self.nextState] += 1
            self.postSynaptic['AIAL'][self.nextState] += 6
            self.postSynaptic['AIBL'][self.nextState] += 7
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['ALA'][self.nextState] += 2
            self.postSynaptic['ASER'][self.nextState] += 3
            self.postSynaptic['ASHL'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 4
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 3
            self.postSynaptic['AWBL'][self.nextState] += 2
            self.postSynaptic['OLQVL'][self.nextState] += 2
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 1

    def ADLR(self, ):
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['AIAR'][self.nextState] += 10
            self.postSynaptic['AIBR'][self.nextState] += 10
            self.postSynaptic['ASER'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 3
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVDL'][self.nextState] += 5
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 3
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1

    def AFDL(self, ):
            self.postSynaptic['AFDR'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AINR'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 7

    def AFDR(self, ):
            self.postSynaptic['AFDL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AIYR'][self.nextState] += 13
            self.postSynaptic['ASER'][self.nextState] += 1
                    
    def AIAL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['AIAR'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 10
            self.postSynaptic['AIML'][self.nextState] += 2
            self.postSynaptic['AIZL'][self.nextState] += 1
            self.postSynaptic['ASER'][self.nextState] += 3
            self.postSynaptic['ASGL'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 1
            self.postSynaptic['ASIL'][self.nextState] += 2
            self.postSynaptic['ASKL'][self.nextState] += 3
            self.postSynaptic['AWAL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 1
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['RIFL'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 1

    def AIAR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['ADFR'][self.nextState] += 1
            self.postSynaptic['ADLR'][self.nextState] += 2
            self.postSynaptic['AIAL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 14
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['ASER'][self.nextState] += 1
            self.postSynaptic['ASGR'][self.nextState] += 1
            self.postSynaptic['ASIR'][self.nextState] += 2
            self.postSynaptic['AWAR'][self.nextState] += 2
            self.postSynaptic['AWCL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 3
            self.postSynaptic['RIFR'][self.nextState] += 2

    def AIBL(self, ):
            self.postSynaptic['AFDL'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 1
            self.postSynaptic['ASER'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 5
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 4
            self.postSynaptic['RIFL'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 3
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 13
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['RIVL'][self.nextState] += 1
            self.postSynaptic['SAADL'][self.nextState] += 2
            self.postSynaptic['SAADR'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 4

    def AIBR(self, ):
            self.postSynaptic['AFDR'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 3
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 2
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 4
            self.postSynaptic['RIGL'][self.nextState] += 3
            self.postSynaptic['RIML'][self.nextState] += 16
            self.postSynaptic['RIML'][self.nextState] += 1
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RIVR'][self.nextState] += 1
            self.postSynaptic['SAADL'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 3
            self.postSynaptic['SMDVL'][self.nextState] += 1
            self.postSynaptic['VB1'][self.nextState] += 3

    def AIML(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 5
            self.postSynaptic['ALML'][self.nextState] += 1
            self.postSynaptic['ASGL'][self.nextState] += 2
            self.postSynaptic['ASKL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 4
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['AVHL'][self.nextState] += 2
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['RIFL'][self.nextState] += 1
            self.postSynaptic['SIBDR'][self.nextState] += 1
            self.postSynaptic['SMBVL'][self.nextState] += 1

    def AIMR(self, ):
            self.postSynaptic['AIAR'][self.nextState] += 5
            self.postSynaptic['ASGR'][self.nextState] += 2
            self.postSynaptic['ASJR'][self.nextState] += 2
            self.postSynaptic['ASKR'][self.nextState] += 3
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 2
            self.postSynaptic['OLQDR'][self.nextState] += 1
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['RIFR'][self.nextState] += 1
            self.postSynaptic['RMGR'][self.nextState] += 1

    def AINL(self, ):
            self.postSynaptic['ADEL'][self.nextState] += 1
            self.postSynaptic['AFDR'][self.nextState] += 5
            self.postSynaptic['AINR'][self.nextState] += 2
            self.postSynaptic['ASEL'][self.nextState] += 3
            self.postSynaptic['ASGR'][self.nextState] += 2
            self.postSynaptic['AUAR'][self.nextState] += 2
            self.postSynaptic['BAGL'][self.nextState] += 3
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 2

    def AINR(self, ):
            self.postSynaptic['AFDL'][self.nextState] += 4
            self.postSynaptic['AFDR'][self.nextState] += 1
            self.postSynaptic['AIAL'][self.nextState] += 2
            self.postSynaptic['AIBL'][self.nextState] += 2
            self.postSynaptic['AINL'][self.nextState] += 2
            self.postSynaptic['ASEL'][self.nextState] += 1
            self.postSynaptic['ASER'][self.nextState] += 1
            self.postSynaptic['ASGL'][self.nextState] += 1
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['AUAR'][self.nextState] += 1
            self.postSynaptic['BAGR'][self.nextState] += 3
            self.postSynaptic['RIBL'][self.nextState] += 2
            self.postSynaptic['RID'][self.nextState] += 1

    def AIYL(self, ):
            self.postSynaptic['AIYR'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 13
            self.postSynaptic['AWAL'][self.nextState] += 3
            self.postSynaptic['AWCL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 7
            self.postSynaptic['RIBL'][self.nextState] += 4
            self.postSynaptic['RIML'][self.nextState] += 1

    def AIYR(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 1
            self.postSynaptic['AIZR'][self.nextState] += 8
            self.postSynaptic['AWAR'][self.nextState] += 1
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 6
            self.postSynaptic['RIBR'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 1

    def AIZL(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 3
            self.postSynaptic['AIBL'][self.nextState] += 2
            self.postSynaptic['AIBR'][self.nextState] += 8
            self.postSynaptic['AIZR'][self.nextState] += 2
            self.postSynaptic['ASEL'][self.nextState] += 1
            self.postSynaptic['ASGL'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 5
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 8
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 4
            self.postSynaptic['SMBDL'][self.nextState] += 9
            self.postSynaptic['SMBVL'][self.nextState] += 7
            self.postSynaptic['VB2'][self.nextState] += 1

    def AIZR(self, ):
            self.postSynaptic['AIAR'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 8
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 2
            self.postSynaptic['ASGR'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 4
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AWAR'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 7
            self.postSynaptic['RIMR'][self.nextState] += 4
            self.postSynaptic['SMBDR'][self.nextState] += 5
            self.postSynaptic['SMBVR'][self.nextState] += 3
            self.postSynaptic['SMDDR'][self.nextState] += 1

    def ALA(self, ):
            self.postSynaptic['ADEL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['RID'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 1

    def ALML(self, ):
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVM'][self.nextState] += 1
            self.postSynaptic['BDUL'][self.nextState] += 6
            self.postSynaptic['CEPDL'][self.nextState] += 3
            self.postSynaptic['CEPVL'][self.nextState] += 2
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 1
            self.postSynaptic['SDQL'][self.nextState] += 1

    def ALMR(self, ):
            self.postSynaptic['AVM'][self.nextState] += 1
            self.postSynaptic['BDUR'][self.nextState] += 5
            self.postSynaptic['CEPDR'][self.nextState] += 1
            self.postSynaptic['CEPVR'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 3
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['SIADL'][self.nextState] += 1

    def ALNL(self, ):
            self.postSynaptic['SAAVL'][self.nextState] += 3
            self.postSynaptic['SMBDR'][self.nextState] += 2
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 1

    def ALNR(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['RMHR'][self.nextState] += 1
            self.postSynaptic['SAAVR'][self.nextState] += 2
            self.postSynaptic['SMBDL'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 1

    def AQR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 4
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 2
            self.postSynaptic['AVKR'][self.nextState] += 1
            self.postSynaptic['BAGL'][self.nextState] += 2
            self.postSynaptic['BAGR'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 2
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 7
            self.postSynaptic['PVPR'][self.nextState] += 9
            self.postSynaptic['RIAL'][self.nextState] += 3
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 2
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['URXL'][self.nextState] += 1

    def AS1(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 2
            self.postSynaptic['MDL05'][self.nextState] += 3
            self.postSynaptic['MDL08'][self.nextState] += 3
            self.postSynaptic['MDR05'][self.nextState] += 3
            self.postSynaptic['MDR08'][self.nextState] += 4
            self.postSynaptic['VA3'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 5
            self.postSynaptic['VD2'][self.nextState] += 1

    def AS2(self, ):
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['MDL07'][self.nextState] += 3
            self.postSynaptic['MDL08'][self.nextState] += 2
            self.postSynaptic['MDR07'][self.nextState] += 3
            self.postSynaptic['MDR08'][self.nextState] += 3
            self.postSynaptic['VA4'][self.nextState] += 2
            self.postSynaptic['VD2'][self.nextState] += 10

    def AS3(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['MDL09'][self.nextState] += 3
            self.postSynaptic['MDL10'][self.nextState] += 3
            self.postSynaptic['MDR09'][self.nextState] += 3
            self.postSynaptic['MDR10'][self.nextState] += 3
            self.postSynaptic['VA5'][self.nextState] += 2
            self.postSynaptic['VD2'][self.nextState] += 1
            self.postSynaptic['VD3'][self.nextState] += 15

    def AS4(self, ):
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 1
            self.postSynaptic['MDL11'][self.nextState] += 2
            self.postSynaptic['MDL12'][self.nextState] += 2
            self.postSynaptic['MDR11'][self.nextState] += 3
            self.postSynaptic['MDR12'][self.nextState] += 2
            self.postSynaptic['VD4'][self.nextState] += 11

    def AS5(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 1
            self.postSynaptic['MDL11'][self.nextState] += 2
            self.postSynaptic['MDL14'][self.nextState] += 3
            self.postSynaptic['MDR11'][self.nextState] += 2
            self.postSynaptic['MDR14'][self.nextState] += 3
            self.postSynaptic['VA7'][self.nextState] += 1
            self.postSynaptic['VD5'][self.nextState] += 9

    def AS6(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DA5'][self.nextState] += 2
            self.postSynaptic['MDL13'][self.nextState] += 3
            self.postSynaptic['MDL14'][self.nextState] += 2
            self.postSynaptic['MDR13'][self.nextState] += 3
            self.postSynaptic['MDR14'][self.nextState] += 2
            self.postSynaptic['VA8'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 13

    def AS7(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVAR'][self.nextState] += 5
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['MDL13'][self.nextState] += 2
            self.postSynaptic['MDL16'][self.nextState] += 3
            self.postSynaptic['MDR13'][self.nextState] += 2
            self.postSynaptic['MDR16'][self.nextState] += 3

    def AS8(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 4
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['MDL15'][self.nextState] += 2
            self.postSynaptic['MDL18'][self.nextState] += 3
            self.postSynaptic['MDR15'][self.nextState] += 2
            self.postSynaptic['MDR18'][self.nextState] += 3

    def AS9(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 4
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DVB'][self.nextState] += 7
            self.postSynaptic['MDL17'][self.nextState] += 2
            self.postSynaptic['MDL20'][self.nextState] += 3
            self.postSynaptic['MDR17'][self.nextState] += 2
            self.postSynaptic['MDR20'][self.nextState] += 3

    def AS10(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['MDL19'][self.nextState] += 3
            self.postSynaptic['MDL20'][self.nextState] += 2
            self.postSynaptic['MDR19'][self.nextState] += 3
            self.postSynaptic['MDR20'][self.nextState] += 2

    def AS11(self, ):
            self.postSynaptic['MDL21'][self.nextState] += 1
            self.postSynaptic['MDL22'][self.nextState] += 1
            self.postSynaptic['MDL23'][self.nextState] += 1
            self.postSynaptic['MDL24'][self.nextState] += 1
            self.postSynaptic['MDR21'][self.nextState] += 1
            self.postSynaptic['MDR22'][self.nextState] += 1
            self.postSynaptic['MDR23'][self.nextState] += 1
            self.postSynaptic['MDR24'][self.nextState] += 1
            self.postSynaptic['PDA'][self.nextState] += 1
            self.postSynaptic['PDB'][self.nextState] += 1
            self.postSynaptic['PDB'][self.nextState] += 2
            self.postSynaptic['VD13'][self.nextState] += 2

    def ASEL(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 1
            self.postSynaptic['AIAL'][self.nextState] += 3
            self.postSynaptic['AIBL'][self.nextState] += 7
            self.postSynaptic['AIBR'][self.nextState] += 2
            self.postSynaptic['AIYL'][self.nextState] += 13
            self.postSynaptic['AIYR'][self.nextState] += 6
            self.postSynaptic['AWCL'][self.nextState] += 4
            self.postSynaptic['AWCR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1

    def ASER(self, ):
            self.postSynaptic['AFDL'][self.nextState] += 1
            self.postSynaptic['AFDR'][self.nextState] += 2
            self.postSynaptic['AIAL'][self.nextState] += 1
            self.postSynaptic['AIAR'][self.nextState] += 3
            self.postSynaptic['AIBL'][self.nextState] += 2
            self.postSynaptic['AIBR'][self.nextState] += 10
            self.postSynaptic['AIYL'][self.nextState] += 2
            self.postSynaptic['AIYR'][self.nextState] += 14
            self.postSynaptic['AWAR'][self.nextState] += 1
            self.postSynaptic['AWCL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 1

    def ASGL(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 9
            self.postSynaptic['AIBL'][self.nextState] += 3
            self.postSynaptic['AINR'][self.nextState] += 2
            self.postSynaptic['AIZL'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 1

    def ASGR(self, ):
            self.postSynaptic['AIAR'][self.nextState] += 10
            self.postSynaptic['AIBR'][self.nextState] += 2
            self.postSynaptic['AINL'][self.nextState] += 1
            self.postSynaptic['AIYR'][self.nextState] += 1
            self.postSynaptic['AIZR'][self.nextState] += 1

    def ASHL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 2
            self.postSynaptic['ADFL'][self.nextState] += 3
            self.postSynaptic['AIAL'][self.nextState] += 7
            self.postSynaptic['AIBL'][self.nextState] += 5
            self.postSynaptic['AIZL'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 6
            self.postSynaptic['AVDL'][self.nextState] += 2
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['RIAL'][self.nextState] += 4
            self.postSynaptic['RICL'][self.nextState] += 2
            self.postSynaptic['RIML'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 1

    def ASHR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 3
            self.postSynaptic['ADFR'][self.nextState] += 2
            self.postSynaptic['AIAR'][self.nextState] += 10
            self.postSynaptic['AIBR'][self.nextState] += 3
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 1
            self.postSynaptic['ASKR'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 5
            self.postSynaptic['AVBR'][self.nextState] += 3
            self.postSynaptic['AVDL'][self.nextState] += 5
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 3
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 2
            self.postSynaptic['RICR'][self.nextState] += 2
            self.postSynaptic['RMGR'][self.nextState] += 2
            self.postSynaptic['RMGR'][self.nextState] += 1

    def ASIL(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 2
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 2
            self.postSynaptic['AIZL'][self.nextState] += 1
            self.postSynaptic['ASER'][self.nextState] += 1
            self.postSynaptic['ASIR'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 2
            self.postSynaptic['AWCL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1

    def ASIR(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 1
            self.postSynaptic['AIAR'][self.nextState] += 3
            self.postSynaptic['AIAR'][self.nextState] += 2
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['ASEL'][self.nextState] += 2
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['ASIL'][self.nextState] += 1
            self.postSynaptic['AWCL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 1

    def ASJL(self, ):
            self.postSynaptic['ASJR'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 4
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PVQL'][self.nextState] += 14

    def ASJR(self, ):
            self.postSynaptic['ASJL'][self.nextState] += 1
            self.postSynaptic['ASKR'][self.nextState] += 4
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 13

    def ASKL(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 11
            self.postSynaptic['AIBL'][self.nextState] += 2
            self.postSynaptic['AIML'][self.nextState] += 2
            self.postSynaptic['ASKR'][self.nextState] += 1
            self.postSynaptic['PVQL'][self.nextState] += 5
            self.postSynaptic['RMGL'][self.nextState] += 1

    def ASKR(self, ):
            self.postSynaptic['AIAR'][self.nextState] += 11
            self.postSynaptic['AIMR'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 1
            self.postSynaptic['AWAR'][self.nextState] += 1
            self.postSynaptic['CEPVR'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 4
            self.postSynaptic['RIFR'][self.nextState] += 1
            self.postSynaptic['RMGR'][self.nextState] += 1

    def AUAL(self, ):
            self.postSynaptic['AINR'][self.nextState] += 1
            self.postSynaptic['AUAR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 3
            self.postSynaptic['AWBL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 5
            self.postSynaptic['RIBL'][self.nextState] += 9

    def AUAR(self, ):
            self.postSynaptic['AINL'][self.nextState] += 1
            self.postSynaptic['AIYR'][self.nextState] += 1
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 4
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 6
            self.postSynaptic['RIBR'][self.nextState] += 13
            self.postSynaptic['URXR'][self.nextState] += 1

    def AVAL(self, ):
            self.postSynaptic['AS1'][self.nextState] += 3
            self.postSynaptic['AS10'][self.nextState] += 3
            self.postSynaptic['AS11'][self.nextState] += 4
            self.postSynaptic['AS2'][self.nextState] += 1
            self.postSynaptic['AS3'][self.nextState] += 3
            self.postSynaptic['AS4'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 4
            self.postSynaptic['AS6'][self.nextState] += 1
            self.postSynaptic['AS7'][self.nextState] += 14
            self.postSynaptic['AS8'][self.nextState] += 9
            self.postSynaptic['AS9'][self.nextState] += 12
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVHL'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 4
            self.postSynaptic['DA2'][self.nextState] += 4
            self.postSynaptic['DA3'][self.nextState] += 6
            self.postSynaptic['DA4'][self.nextState] += 10
            self.postSynaptic['DA5'][self.nextState] += 8
            self.postSynaptic['DA6'][self.nextState] += 21
            self.postSynaptic['DA7'][self.nextState] += 4
            self.postSynaptic['DA8'][self.nextState] += 4
            self.postSynaptic['DA9'][self.nextState] += 3
            self.postSynaptic['DB5'][self.nextState] += 2
            self.postSynaptic['DB6'][self.nextState] += 4
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['LUAL'][self.nextState] += 2
            self.postSynaptic['PVCL'][self.nextState] += 12
            self.postSynaptic['PVCR'][self.nextState] += 11
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['RIMR'][self.nextState] += 3
            self.postSynaptic['SABD'][self.nextState] += 4
            self.postSynaptic['SABVR'][self.nextState] += 1
            self.postSynaptic['SDQR'][self.nextState] += 1
            self.postSynaptic['URYDL'][self.nextState] += 1
            self.postSynaptic['URYVR'][self.nextState] += 1
            self.postSynaptic['VA1'][self.nextState] += 3
            self.postSynaptic['VA10'][self.nextState] += 6
            self.postSynaptic['VA11'][self.nextState] += 7
            self.postSynaptic['VA12'][self.nextState] += 2
            self.postSynaptic['VA2'][self.nextState] += 5
            self.postSynaptic['VA3'][self.nextState] += 3
            self.postSynaptic['VA4'][self.nextState] += 3
            self.postSynaptic['VA5'][self.nextState] += 8
            self.postSynaptic['VA6'][self.nextState] += 10
            self.postSynaptic['VA7'][self.nextState] += 2
            self.postSynaptic['VA8'][self.nextState] += 19
            self.postSynaptic['VA9'][self.nextState] += 8
            self.postSynaptic['VB9'][self.nextState] += 5

    def AVAR(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['AS1'][self.nextState] += 3
            self.postSynaptic['AS10'][self.nextState] += 2
            self.postSynaptic['AS11'][self.nextState] += 6
            self.postSynaptic['AS2'][self.nextState] += 2
            self.postSynaptic['AS3'][self.nextState] += 2
            self.postSynaptic['AS4'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 2
            self.postSynaptic['AS6'][self.nextState] += 3
            self.postSynaptic['AS7'][self.nextState] += 8
            self.postSynaptic['AS8'][self.nextState] += 9
            self.postSynaptic['AS9'][self.nextState] += 6
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 8
            self.postSynaptic['DA2'][self.nextState] += 4
            self.postSynaptic['DA3'][self.nextState] += 5
            self.postSynaptic['DA4'][self.nextState] += 8
            self.postSynaptic['DA5'][self.nextState] += 7
            self.postSynaptic['DA6'][self.nextState] += 13
            self.postSynaptic['DA7'][self.nextState] += 3
            self.postSynaptic['DA8'][self.nextState] += 9
            self.postSynaptic['DA9'][self.nextState] += 2
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['DB5'][self.nextState] += 3
            self.postSynaptic['DB6'][self.nextState] += 5
            self.postSynaptic['LUAL'][self.nextState] += 1
            self.postSynaptic['LUAR'][self.nextState] += 3
            self.postSynaptic['PDEL'][self.nextState] += 1
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 7
            self.postSynaptic['PVCR'][self.nextState] += 8
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['SABVL'][self.nextState] += 6
            self.postSynaptic['SABVR'][self.nextState] += 1
            self.postSynaptic['URYDR'][self.nextState] += 1
            self.postSynaptic['URYVL'][self.nextState] += 1
            self.postSynaptic['VA10'][self.nextState] += 5
            self.postSynaptic['VA11'][self.nextState] += 15
            self.postSynaptic['VA12'][self.nextState] += 1
            self.postSynaptic['VA2'][self.nextState] += 2
            self.postSynaptic['VA3'][self.nextState] += 7
            self.postSynaptic['VA4'][self.nextState] += 5
            self.postSynaptic['VA5'][self.nextState] += 4
            self.postSynaptic['VA6'][self.nextState] += 5
            self.postSynaptic['VA7'][self.nextState] += 4
            self.postSynaptic['VA8'][self.nextState] += 16
            self.postSynaptic['VB9'][self.nextState] += 10
            self.postSynaptic['VD13'][self.nextState] += 2

    def AVBL(self, ):
            self.postSynaptic['AQR'][self.nextState] += 1
            self.postSynaptic['AS10'][self.nextState] += 1
            self.postSynaptic['AS3'][self.nextState] += 1
            self.postSynaptic['AS4'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['AS6'][self.nextState] += 1
            self.postSynaptic['AS7'][self.nextState] += 2
            self.postSynaptic['AS9'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 7
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVBR'][self.nextState] += 4
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DB5'][self.nextState] += 1
            self.postSynaptic['DB6'][self.nextState] += 2
            self.postSynaptic['DB7'][self.nextState] += 2
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RID'][self.nextState] += 1
            self.postSynaptic['SDQR'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 1
            self.postSynaptic['VA10'][self.nextState] += 1
            self.postSynaptic['VA2'][self.nextState] += 1
            self.postSynaptic['VA7'][self.nextState] += 1
            self.postSynaptic['VB1'][self.nextState] += 1
            self.postSynaptic['VB10'][self.nextState] += 2
            self.postSynaptic['VB11'][self.nextState] += 2
            self.postSynaptic['VB2'][self.nextState] += 4
            self.postSynaptic['VB4'][self.nextState] += 1
            self.postSynaptic['VB5'][self.nextState] += 1
            self.postSynaptic['VB6'][self.nextState] += 1
            self.postSynaptic['VB7'][self.nextState] += 2
            self.postSynaptic['VB8'][self.nextState] += 7
            self.postSynaptic['VB9'][self.nextState] += 1
            self.postSynaptic['VC3'][self.nextState] += 1

    def AVBR(self, ):
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['AS10'][self.nextState] += 1
            self.postSynaptic['AS3'][self.nextState] += 1
            self.postSynaptic['AS4'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['AS6'][self.nextState] += 2
            self.postSynaptic['AS7'][self.nextState] += 3
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVBL'][self.nextState] += 4
            self.postSynaptic['DA5'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 3
            self.postSynaptic['DB2'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DB5'][self.nextState] += 1
            self.postSynaptic['DB6'][self.nextState] += 1
            self.postSynaptic['DB7'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 2
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RID'][self.nextState] += 2
            self.postSynaptic['SIBVL'][self.nextState] += 1
            self.postSynaptic['VA4'][self.nextState] += 1
            self.postSynaptic['VA8'][self.nextState] += 1
            self.postSynaptic['VA9'][self.nextState] += 2
            self.postSynaptic['VB10'][self.nextState] += 1
            self.postSynaptic['VB11'][self.nextState] += 1
            self.postSynaptic['VB2'][self.nextState] += 1
            self.postSynaptic['VB3'][self.nextState] += 1
            self.postSynaptic['VB4'][self.nextState] += 1
            self.postSynaptic['VB6'][self.nextState] += 2
            self.postSynaptic['VB7'][self.nextState] += 2
            self.postSynaptic['VB8'][self.nextState] += 3
            self.postSynaptic['VB9'][self.nextState] += 6
            self.postSynaptic['VD10'][self.nextState] += 1
            self.postSynaptic['VD3'][self.nextState] += 1

    def AVDL(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 2
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['AS10'][self.nextState] += 1
            self.postSynaptic['AS11'][self.nextState] += 2
            self.postSynaptic['AS4'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 13
            self.postSynaptic['AVAR'][self.nextState] += 19
            self.postSynaptic['AVM'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 1
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 4
            self.postSynaptic['DA4'][self.nextState] += 1
            self.postSynaptic['DA5'][self.nextState] += 1
            self.postSynaptic['DA8'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['FLPR'][self.nextState] += 1
            self.postSynaptic['LUAL'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['SABVL'][self.nextState] += 1
            self.postSynaptic['SABVR'][self.nextState] += 1
            self.postSynaptic['VA5'][self.nextState] += 1

    def AVDR(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 2
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['AS10'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 16
            self.postSynaptic['AVAR'][self.nextState] += 15
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 2
            self.postSynaptic['AVJL'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 2
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 1
            self.postSynaptic['DA4'][self.nextState] += 1
            self.postSynaptic['DA5'][self.nextState] += 2
            self.postSynaptic['DA8'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['FLPR'][self.nextState] += 1
            self.postSynaptic['LUAL'][self.nextState] += 2
            self.postSynaptic['PQR'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['SABVL'][self.nextState] += 3
            self.postSynaptic['SABVR'][self.nextState] += 1
            self.postSynaptic['VA11'][self.nextState] += 1
            self.postSynaptic['VA2'][self.nextState] += 1
            self.postSynaptic['VA3'][self.nextState] += 2
            self.postSynaptic['VA6'][self.nextState] += 1

    def AVEL(self, ):
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 12
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['DA1'][self.nextState] += 5
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 3
            self.postSynaptic['DA4'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 3
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 6
            self.postSynaptic['SABVL'][self.nextState] += 7
            self.postSynaptic['SABVR'][self.nextState] += 3
            self.postSynaptic['VA1'][self.nextState] += 5
            self.postSynaptic['VA3'][self.nextState] += 3
            self.postSynaptic['VD2'][self.nextState] += 1
            self.postSynaptic['VD3'][self.nextState] += 1

    def AVER(self, ):
            self.postSynaptic['AS1'][self.nextState] += 3
            self.postSynaptic['AS2'][self.nextState] += 2
            self.postSynaptic['AS3'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 7
            self.postSynaptic['AVAR'][self.nextState] += 16
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['DA1'][self.nextState] += 5
            self.postSynaptic['DA2'][self.nextState] += 3
            self.postSynaptic['DA3'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 3
            self.postSynaptic['RIMR'][self.nextState] += 2
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 2
            self.postSynaptic['SABVL'][self.nextState] += 3
            self.postSynaptic['SABVR'][self.nextState] += 3
            self.postSynaptic['VA1'][self.nextState] += 1
            self.postSynaptic['VA2'][self.nextState] += 1
            self.postSynaptic['VA3'][self.nextState] += 2
            self.postSynaptic['VA4'][self.nextState] += 1
            self.postSynaptic['VA5'][self.nextState] += 1

    def AVFL(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVFR'][self.nextState] += 30
            self.postSynaptic['AVG'][self.nextState] += 1
            self.postSynaptic['AVHL'][self.nextState] += 4
            self.postSynaptic['AVHR'][self.nextState] += 7
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['MVL11'][self.nextState] += 1
            self.postSynaptic['MVL12'][self.nextState] += 1
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 2
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 2
            self.postSynaptic['VB1'][self.nextState] += 1

    def AVFR(self, ):
            self.postSynaptic['ASJL'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 5
            self.postSynaptic['AVFL'][self.nextState] += 24
            self.postSynaptic['AVHL'][self.nextState] += 4
            self.postSynaptic['AVHR'][self.nextState] += 2
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['MVL14'][self.nextState] += 2
            self.postSynaptic['MVR14'][self.nextState] += 2
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['VC4'][self.nextState] += 1
            self.postSynaptic['VD11'][self.nextState] += 1

    def AVG(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['DA8'][self.nextState] += 1
            self.postSynaptic['PHAL'][self.nextState] += 2
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIFL'][self.nextState] += 1
            self.postSynaptic['RIFR'][self.nextState] += 1
            self.postSynaptic['VA11'][self.nextState] += 1

    def AVHL(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 2
            self.postSynaptic['AVFR'][self.nextState] += 5
            self.postSynaptic['AVHR'][self.nextState] += 2
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['PHBR'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 2
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 3
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['SMBVR'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 1

    def AVHR(self, ):
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['ADLR'][self.nextState] += 2
            self.postSynaptic['AQR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 2
            self.postSynaptic['AVHL'][self.nextState] += 2
            self.postSynaptic['AVJR'][self.nextState] += 4
            self.postSynaptic['PVNL'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 3
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 4
            self.postSynaptic['SMBDL'][self.nextState] += 1
            self.postSynaptic['SMBVL'][self.nextState] += 1

    def AVJL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 4
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['AVHL'][self.nextState] += 2
            self.postSynaptic['AVJR'][self.nextState] += 4
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PLMR'][self.nextState] += 2
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 5
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['RIFR'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 2

    def AVJR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 3
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 3
            self.postSynaptic['AVER'][self.nextState] += 3
            self.postSynaptic['AVJL'][self.nextState] += 5
            self.postSynaptic['PVCL'][self.nextState] += 3
            self.postSynaptic['PVCR'][self.nextState] += 4
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['SABVL'][self.nextState] += 1

    def AVKL(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['AQR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 2
            self.postSynaptic['AVM'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['PDEL'][self.nextState] += 3
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PVM'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 2
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['RMFR'][self.nextState] += 1
            self.postSynaptic['SAADR'][self.nextState] += 1
            self.postSynaptic['SIAVR'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['SMBVR'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['VB1'][self.nextState] += 4
            self.postSynaptic['VB10'][self.nextState] += 1

    def AVKR(self, ):
            self.postSynaptic['ADEL'][self.nextState] += 1
            self.postSynaptic['AQR'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 2
            self.postSynaptic['BDUL'][self.nextState] += 1
            self.postSynaptic['MVL10'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 6
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 2
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMFL'][self.nextState] += 1
            self.postSynaptic['SAADL'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 2
            self.postSynaptic['SMBDR'][self.nextState] += 2
            self.postSynaptic['SMBVR'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 2

    def AVL(self, ):
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['DD6'][self.nextState] += 2
            self.postSynaptic['DVB'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 9
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['MVL10'][self.nextState] += -5
            self.postSynaptic['MVR10'][self.nextState] += -5
            self.postSynaptic['PVM'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['PVWL'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 5
            self.postSynaptic['SABVL'][self.nextState] += 4
            self.postSynaptic['SABVR'][self.nextState] += 3
            self.postSynaptic['VD12'][self.nextState] += 4

    def AVM(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['ALML'][self.nextState] += 1
            self.postSynaptic['ALMR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 6
            self.postSynaptic['AVBR'][self.nextState] += 6
            self.postSynaptic['AVDL'][self.nextState] += 2
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['BDUL'][self.nextState] += 3
            self.postSynaptic['BDUR'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 4
            self.postSynaptic['PVCR'][self.nextState] += 5
            self.postSynaptic['PVNL'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 3
            self.postSynaptic['RID'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 1
            self.postSynaptic['VA1'][self.nextState] += 2

    def AWAL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['AFDL'][self.nextState] += 5
            self.postSynaptic['AIAL'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 10
            self.postSynaptic['ASEL'][self.nextState] += 4
            self.postSynaptic['ASGL'][self.nextState] += 1
            self.postSynaptic['AWAR'][self.nextState] += 1
            self.postSynaptic['AWBL'][self.nextState] += 1

    def AWAR(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 3
            self.postSynaptic['AFDR'][self.nextState] += 7
            self.postSynaptic['AIAR'][self.nextState] += 1
            self.postSynaptic['AIYR'][self.nextState] += 2
            self.postSynaptic['AIZR'][self.nextState] += 7
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['ASEL'][self.nextState] += 1
            self.postSynaptic['ASER'][self.nextState] += 2
            self.postSynaptic['AUAR'][self.nextState] += 1
            self.postSynaptic['AWAL'][self.nextState] += 1
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['RIFR'][self.nextState] += 2
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 2

    def AWBL(self, ):
            self.postSynaptic['ADFL'][self.nextState] += 9
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 9
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 3
            self.postSynaptic['RMGL'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 1

    def AWBR(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 4
            self.postSynaptic['AIZR'][self.nextState] += 4
            self.postSynaptic['ASGR'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 2
            self.postSynaptic['AUAR'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AWBL'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 2
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['SMBVR'][self.nextState] += 1

    def AWCL(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 2
            self.postSynaptic['AIAR'][self.nextState] += 4
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 10
            self.postSynaptic['ASEL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AWCR'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 3

    def AWCR(self, ):
            self.postSynaptic['AIAR'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 4
            self.postSynaptic['AIYL'][self.nextState] += 4
            self.postSynaptic['AIYR'][self.nextState] += 9
            self.postSynaptic['ASEL'][self.nextState] += 1
            self.postSynaptic['ASGR'][self.nextState] += 1
            self.postSynaptic['AWCL'][self.nextState] += 5

    def BAGL(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 4
            self.postSynaptic['BAGR'][self.nextState] += 2
            self.postSynaptic['RIAR'][self.nextState] += 5
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 7
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 4
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 1

    def BAGR(self, ):
            self.postSynaptic['AIYL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['BAGL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 5
            self.postSynaptic['RIBL'][self.nextState] += 4
            self.postSynaptic['RIGL'][self.nextState] += 5
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 1

    def BDUL(self, ):
            self.postSynaptic['ADEL'][self.nextState] += 3
            self.postSynaptic['AVHL'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 2
            self.postSynaptic['PVNR'][self.nextState] += 2
            self.postSynaptic['SAADL'][self.nextState] += 1
            self.postSynaptic['URADL'][self.nextState] += 1

    def BDUR(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['ALMR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVHL'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 2
            self.postSynaptic['HSNR'][self.nextState] += 4
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 2
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['SDQL'][self.nextState] += 1
            self.postSynaptic['URADR'][self.nextState] += 1

    def CEPDL(self, ):
            self.postSynaptic['AVER'][self.nextState] += 5
            self.postSynaptic['IL1DL'][self.nextState] += 4
            self.postSynaptic['OLLL'][self.nextState] += 2
            self.postSynaptic['OLQDL'][self.nextState] += 6
            self.postSynaptic['OLQDL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 2
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 2
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 2
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 3
            self.postSynaptic['RMGL'][self.nextState] += 4
            self.postSynaptic['RMHR'][self.nextState] += 4
            self.postSynaptic['SIADR'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['URADL'][self.nextState] += 2
            self.postSynaptic['URBL'][self.nextState] += 4
            self.postSynaptic['URYDL'][self.nextState] += 2

    def CEPDR(self, ):
            self.postSynaptic['AVEL'][self.nextState] += 6
            self.postSynaptic['BDUR'][self.nextState] += 1
            self.postSynaptic['IL1DR'][self.nextState] += 5
            self.postSynaptic['IL1R'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 8
            self.postSynaptic['OLQDR'][self.nextState] += 5
            self.postSynaptic['OLQDR'][self.nextState] += 2
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 4
            self.postSynaptic['RICR'][self.nextState] += 3
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 2
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['RMHL'][self.nextState] += 4
            self.postSynaptic['RMHR'][self.nextState] += 1
            self.postSynaptic['SIADL'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['URADR'][self.nextState] += 1
            self.postSynaptic['URBR'][self.nextState] += 2
            self.postSynaptic['URYDR'][self.nextState] += 1

    def CEPVL(self, ):
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 3
            self.postSynaptic['IL1VL'][self.nextState] += 2
            self.postSynaptic['MVL03'][self.nextState] += 1
            self.postSynaptic['OLLL'][self.nextState] += 4
            self.postSynaptic['OLQVL'][self.nextState] += 6
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 7
            self.postSynaptic['RICR'][self.nextState] += 4
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 4
            self.postSynaptic['RMHL'][self.nextState] += 1
            self.postSynaptic['SIAVL'][self.nextState] += 1
            self.postSynaptic['URAVL'][self.nextState] += 2

    def CEPVR(self, ):
            self.postSynaptic['ASGR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 5
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['IL2VR'][self.nextState] += 2
            self.postSynaptic['MVR04'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 7
            self.postSynaptic['OLQVR'][self.nextState] += 3
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 2
            self.postSynaptic['RICR'][self.nextState] += 2
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIPR'][self.nextState] += 1
            self.postSynaptic['RIVL'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 2
            self.postSynaptic['RMHR'][self.nextState] += 2
            self.postSynaptic['SIAVR'][self.nextState] += 2
            self.postSynaptic['URAVR'][self.nextState] += 1

    def DA1(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 6
            self.postSynaptic['DA4'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 4
            self.postSynaptic['MDL08'][self.nextState] += 8
            self.postSynaptic['MDR08'][self.nextState] += 8
            self.postSynaptic['SABVL'][self.nextState] += 2
            self.postSynaptic['SABVR'][self.nextState] += 3
            self.postSynaptic['VD1'][self.nextState] += 17
            self.postSynaptic['VD2'][self.nextState] += 1

    def DA2(self, ):
            self.postSynaptic['AS2'][self.nextState] += 2
            self.postSynaptic['AS3'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['MDL07'][self.nextState] += 2
            self.postSynaptic['MDL08'][self.nextState] += 1
            self.postSynaptic['MDL09'][self.nextState] += 2
            self.postSynaptic['MDL10'][self.nextState] += 2
            self.postSynaptic['MDR07'][self.nextState] += 2
            self.postSynaptic['MDR08'][self.nextState] += 2
            self.postSynaptic['MDR09'][self.nextState] += 2
            self.postSynaptic['MDR10'][self.nextState] += 2
            self.postSynaptic['SABVL'][self.nextState] += 1
            self.postSynaptic['VA1'][self.nextState] += 2
            self.postSynaptic['VD1'][self.nextState] += 2
            self.postSynaptic['VD2'][self.nextState] += 11
            self.postSynaptic['VD3'][self.nextState] += 5

    def DA3(self, ):
            self.postSynaptic['AS4'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DA4'][self.nextState] += 2
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 1
            self.postSynaptic['MDL09'][self.nextState] += 5
            self.postSynaptic['MDL10'][self.nextState] += 5
            self.postSynaptic['MDL12'][self.nextState] += 5
            self.postSynaptic['MDR09'][self.nextState] += 5
            self.postSynaptic['MDR10'][self.nextState] += 5
            self.postSynaptic['MDR12'][self.nextState] += 5
            self.postSynaptic['VD3'][self.nextState] += 25
            self.postSynaptic['VD4'][self.nextState] += 6

    def DA4(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DA1'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 2
            self.postSynaptic['DD2'][self.nextState] += 1
            self.postSynaptic['MDL11'][self.nextState] += 4
            self.postSynaptic['MDL12'][self.nextState] += 4
            self.postSynaptic['MDL14'][self.nextState] += 5
            self.postSynaptic['MDR11'][self.nextState] += 4
            self.postSynaptic['MDR12'][self.nextState] += 4
            self.postSynaptic['MDR14'][self.nextState] += 5
            self.postSynaptic['VB6'][self.nextState] += 1
            self.postSynaptic['VD4'][self.nextState] += 12
            self.postSynaptic['VD5'][self.nextState] += 15

    def DA5(self, ):
            self.postSynaptic['AS6'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 5
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['MDL13'][self.nextState] += 5
            self.postSynaptic['MDL14'][self.nextState] += 4
            self.postSynaptic['MDR13'][self.nextState] += 5
            self.postSynaptic['MDR14'][self.nextState] += 4
            self.postSynaptic['VA4'][self.nextState] += 1
            self.postSynaptic['VA5'][self.nextState] += 2
            self.postSynaptic['VD5'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 16

    def DA6(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 10
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['MDL11'][self.nextState] += 6
            self.postSynaptic['MDL12'][self.nextState] += 4
            self.postSynaptic['MDL13'][self.nextState] += 4
            self.postSynaptic['MDL14'][self.nextState] += 4
            self.postSynaptic['MDL16'][self.nextState] += 4
            self.postSynaptic['MDR11'][self.nextState] += 4
            self.postSynaptic['MDR12'][self.nextState] += 4
            self.postSynaptic['MDR13'][self.nextState] += 4
            self.postSynaptic['MDR14'][self.nextState] += 4
            self.postSynaptic['MDR16'][self.nextState] += 4
            self.postSynaptic['VD4'][self.nextState] += 4
            self.postSynaptic['VD5'][self.nextState] += 3
            self.postSynaptic['VD6'][self.nextState] += 3

    def DA7(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['MDL15'][self.nextState] += 4
            self.postSynaptic['MDL17'][self.nextState] += 4
            self.postSynaptic['MDL18'][self.nextState] += 4
            self.postSynaptic['MDR15'][self.nextState] += 4
            self.postSynaptic['MDR17'][self.nextState] += 4
            self.postSynaptic['MDR18'][self.nextState] += 4

    def DA8(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['MDL17'][self.nextState] += 4
            self.postSynaptic['MDL19'][self.nextState] += 4
            self.postSynaptic['MDL20'][self.nextState] += 4
            self.postSynaptic['MDR17'][self.nextState] += 4
            self.postSynaptic['MDR19'][self.nextState] += 4
            self.postSynaptic['MDR20'][self.nextState] += 4

    def DA9(self, ):
            self.postSynaptic['DA8'][self.nextState] += 1
            self.postSynaptic['DD6'][self.nextState] += 1
            self.postSynaptic['MDL19'][self.nextState] += 4
            self.postSynaptic['MDL21'][self.nextState] += 4
            self.postSynaptic['MDL22'][self.nextState] += 4
            self.postSynaptic['MDL23'][self.nextState] += 4
            self.postSynaptic['MDL24'][self.nextState] += 4
            self.postSynaptic['MDR19'][self.nextState] += 4
            self.postSynaptic['MDR21'][self.nextState] += 4
            self.postSynaptic['MDR22'][self.nextState] += 4
            self.postSynaptic['MDR23'][self.nextState] += 4
            self.postSynaptic['MDR24'][self.nextState] += 4
            self.postSynaptic['PDA'][self.nextState] += 1
            self.postSynaptic['PHCL'][self.nextState] += 1
            self.postSynaptic['RID'][self.nextState] += 1
            self.postSynaptic['VD13'][self.nextState] += 1

    def DB1(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['AS2'][self.nextState] += 1
            self.postSynaptic['AS3'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 3
            self.postSynaptic['DB2'][self.nextState] += 1
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 10
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['MDL07'][self.nextState] += 1
            self.postSynaptic['MDL08'][self.nextState] += 1
            self.postSynaptic['MDR07'][self.nextState] += 1
            self.postSynaptic['MDR08'][self.nextState] += 1
            self.postSynaptic['RID'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['VB3'][self.nextState] += 1
            self.postSynaptic['VB4'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 21
            self.postSynaptic['VD2'][self.nextState] += 15
            self.postSynaptic['VD3'][self.nextState] += 1

    def DB2(self, ):
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DA3'][self.nextState] += 5
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 6
            self.postSynaptic['DD2'][self.nextState] += 3
            self.postSynaptic['MDL09'][self.nextState] += 3
            self.postSynaptic['MDL10'][self.nextState] += 3
            self.postSynaptic['MDL11'][self.nextState] += 3
            self.postSynaptic['MDL12'][self.nextState] += 3
            self.postSynaptic['MDR09'][self.nextState] += 3
            self.postSynaptic['MDR10'][self.nextState] += 3
            self.postSynaptic['MDR11'][self.nextState] += 3
            self.postSynaptic['MDR12'][self.nextState] += 3
            self.postSynaptic['VB1'][self.nextState] += 2
            self.postSynaptic['VD3'][self.nextState] += 23
            self.postSynaptic['VD4'][self.nextState] += 14
            self.postSynaptic['VD5'][self.nextState] += 1

    def DB3(self, ):
            self.postSynaptic['AS4'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DA4'][self.nextState] += 1
            self.postSynaptic['DB2'][self.nextState] += 6
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 4
            self.postSynaptic['DD3'][self.nextState] += 10
            self.postSynaptic['MDL11'][self.nextState] += 3
            self.postSynaptic['MDL12'][self.nextState] += 3
            self.postSynaptic['MDL13'][self.nextState] += 4
            self.postSynaptic['MDL14'][self.nextState] += 3
            self.postSynaptic['MDR11'][self.nextState] += 3
            self.postSynaptic['MDR12'][self.nextState] += 3
            self.postSynaptic['MDR13'][self.nextState] += 4
            self.postSynaptic['MDR14'][self.nextState] += 3
            self.postSynaptic['VD4'][self.nextState] += 9
            self.postSynaptic['VD5'][self.nextState] += 26
            self.postSynaptic['VD6'][self.nextState] += 7

    def DB4(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['DD3'][self.nextState] += 3
            self.postSynaptic['MDL13'][self.nextState] += 2
            self.postSynaptic['MDL14'][self.nextState] += 2
            self.postSynaptic['MDL16'][self.nextState] += 2
            self.postSynaptic['MDR13'][self.nextState] += 2
            self.postSynaptic['MDR14'][self.nextState] += 2
            self.postSynaptic['MDR16'][self.nextState] += 2
            self.postSynaptic['VB2'][self.nextState] += 1
            self.postSynaptic['VB4'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 13

    def DB5(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['MDL15'][self.nextState] += 2
            self.postSynaptic['MDL17'][self.nextState] += 2
            self.postSynaptic['MDL18'][self.nextState] += 2
            self.postSynaptic['MDR15'][self.nextState] += 2
            self.postSynaptic['MDR17'][self.nextState] += 2
            self.postSynaptic['MDR18'][self.nextState] += 2

    def DB6(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['MDL17'][self.nextState] += 2
            self.postSynaptic['MDL19'][self.nextState] += 2
            self.postSynaptic['MDL20'][self.nextState] += 2
            self.postSynaptic['MDR17'][self.nextState] += 2
            self.postSynaptic['MDR19'][self.nextState] += 2
            self.postSynaptic['MDR20'][self.nextState] += 2

    def DB7(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['MDL19'][self.nextState] += 2
            self.postSynaptic['MDL21'][self.nextState] += 2
            self.postSynaptic['MDL22'][self.nextState] += 2
            self.postSynaptic['MDL23'][self.nextState] += 2
            self.postSynaptic['MDL24'][self.nextState] += 2
            self.postSynaptic['MDR19'][self.nextState] += 2
            self.postSynaptic['MDR21'][self.nextState] += 2
            self.postSynaptic['MDR22'][self.nextState] += 2
            self.postSynaptic['MDR23'][self.nextState] += 2
            self.postSynaptic['MDR24'][self.nextState] += 2
            self.postSynaptic['VD13'][self.nextState] += 2

    def DD1(self, ):
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 3
            self.postSynaptic['MDL07'][self.nextState] += -6
            self.postSynaptic['MDL08'][self.nextState] += -6
            self.postSynaptic['MDL09'][self.nextState] += -7
            self.postSynaptic['MDL10'][self.nextState] += -6
            self.postSynaptic['MDR07'][self.nextState] += -6
            self.postSynaptic['MDR08'][self.nextState] += -6
            self.postSynaptic['MDR09'][self.nextState] += -7
            self.postSynaptic['MDR10'][self.nextState] += -6
            self.postSynaptic['VD1'][self.nextState] += 4
            self.postSynaptic['VD2'][self.nextState] += 1
            self.postSynaptic['VD2'][self.nextState] += 2

    def DD2(self, ):
            self.postSynaptic['DA3'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['DD3'][self.nextState] += 2
            self.postSynaptic['MDL09'][self.nextState] += -6
            self.postSynaptic['MDL11'][self.nextState] += -7
            self.postSynaptic['MDL12'][self.nextState] += -6
            self.postSynaptic['MDR09'][self.nextState] += -6
            self.postSynaptic['MDR11'][self.nextState] += -7
            self.postSynaptic['MDR12'][self.nextState] += -6
            self.postSynaptic['VD3'][self.nextState] += 1
            self.postSynaptic['VD4'][self.nextState] += 3

    def DD3(self, ):
            self.postSynaptic['DD2'][self.nextState] += 2
            self.postSynaptic['DD4'][self.nextState] += 1
            self.postSynaptic['MDL11'][self.nextState] += -7
            self.postSynaptic['MDL13'][self.nextState] += -9
            self.postSynaptic['MDL14'][self.nextState] += -7
            self.postSynaptic['MDR11'][self.nextState] += -7
            self.postSynaptic['MDR13'][self.nextState] += -9
            self.postSynaptic['MDR14'][self.nextState] += -7

    def DD4(self, ):
            self.postSynaptic['DD3'][self.nextState] += 1
            self.postSynaptic['MDL13'][self.nextState] += -7
            self.postSynaptic['MDL15'][self.nextState] += -7
            self.postSynaptic['MDL16'][self.nextState] += -7
            self.postSynaptic['MDR13'][self.nextState] += -7
            self.postSynaptic['MDR15'][self.nextState] += -7
            self.postSynaptic['MDR16'][self.nextState] += -7
            self.postSynaptic['VC3'][self.nextState] += 1
            self.postSynaptic['VD8'][self.nextState] += 1

    def DD5(self, ):
            self.postSynaptic['MDL17'][self.nextState] += -7
            self.postSynaptic['MDL18'][self.nextState] += -7
            self.postSynaptic['MDL20'][self.nextState] += -7
            self.postSynaptic['MDR17'][self.nextState] += -7
            self.postSynaptic['MDR18'][self.nextState] += -7
            self.postSynaptic['MDR20'][self.nextState] += -7
            self.postSynaptic['VB8'][self.nextState] += 1
            self.postSynaptic['VD10'][self.nextState] += 1
            self.postSynaptic['VD9'][self.nextState] += 1

    def DD6(self, ):
            self.postSynaptic['MDL19'][self.nextState] += -7
            self.postSynaptic['MDL21'][self.nextState] += -7
            self.postSynaptic['MDL22'][self.nextState] += -7
            self.postSynaptic['MDL23'][self.nextState] += -7
            self.postSynaptic['MDL24'][self.nextState] += -7
            self.postSynaptic['MDR19'][self.nextState] += -7
            self.postSynaptic['MDR21'][self.nextState] += -7
            self.postSynaptic['MDR22'][self.nextState] += -7
            self.postSynaptic['MDR23'][self.nextState] += -7
            self.postSynaptic['MDR24'][self.nextState] += -7

    def DVA(self, ):
            self.postSynaptic['AIZL'][self.nextState] += 3
            self.postSynaptic['AQR'][self.nextState] += 4
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['AUAR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 9
            self.postSynaptic['AVER'][self.nextState] += 5
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DB2'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 2
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DB5'][self.nextState] += 1
            self.postSynaptic['DB6'][self.nextState] += 2
            self.postSynaptic['DB7'][self.nextState] += 1
            self.postSynaptic['PDEL'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 3
            self.postSynaptic['PVR'][self.nextState] += 2
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 3
            self.postSynaptic['SAADR'][self.nextState] += 1
            self.postSynaptic['SAAVL'][self.nextState] += 1
            self.postSynaptic['SAAVR'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 3
            self.postSynaptic['SMBDR'][self.nextState] += 2
            self.postSynaptic['SMBVL'][self.nextState] += 3
            self.postSynaptic['SMBVR'][self.nextState] += 2
            self.postSynaptic['VA12'][self.nextState] += 1
            self.postSynaptic['VA2'][self.nextState] += 1
            self.postSynaptic['VB1'][self.nextState] += 1
            self.postSynaptic['VB11'][self.nextState] += 2

    def DVB(self, ):
            self.postSynaptic['AS9'][self.nextState] += 7
            self.postSynaptic['AVL'][self.nextState] += 5
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['DA8'][self.nextState] += 2
            self.postSynaptic['DD6'][self.nextState] += 3
            self.postSynaptic['DVC'][self.nextState] += 3
            # self.postSynaptic['MANAL'][self.nextState] += -5 - just not needed or used
            self.postSynaptic['PDA'][self.nextState] += 1
            self.postSynaptic['PHCL'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VB9'][self.nextState] += 1

    def DVC(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 2
            self.postSynaptic['AIBR'][self.nextState] += 5
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 2
            self.postSynaptic['AVKR'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 9
            self.postSynaptic['PVPL'][self.nextState] += 2
            self.postSynaptic['PVPR'][self.nextState] += 13
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 5
            self.postSynaptic['RIGR'][self.nextState] += 5
            self.postSynaptic['RMFL'][self.nextState] += 2
            self.postSynaptic['RMFR'][self.nextState] += 4
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 5
            self.postSynaptic['VD10'][self.nextState] += 4

    def FLPL(self, ):
            self.postSynaptic['ADEL'][self.nextState] += 2
            self.postSynaptic['ADER'][self.nextState] += 2
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 15
            self.postSynaptic['AVAR'][self.nextState] += 17
            self.postSynaptic['AVBL'][self.nextState] += 4
            self.postSynaptic['AVBR'][self.nextState] += 5
            self.postSynaptic['AVDL'][self.nextState] += 7
            self.postSynaptic['AVDR'][self.nextState] += 13
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['FLPR'][self.nextState] += 3
            self.postSynaptic['RIH'][self.nextState] += 1

    def FLPR(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 12
            self.postSynaptic['AVAR'][self.nextState] += 5
            self.postSynaptic['AVBL'][self.nextState] += 5
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 10
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 4
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 4
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['VB1'][self.nextState] += 1

    def HSNL(self, ):
            self.postSynaptic['AIAL'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 2
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 2
            self.postSynaptic['ASJR'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVFL'][self.nextState] += 6
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AWBL'][self.nextState] += 1
            self.postSynaptic['AWBR'][self.nextState] += 2
            self.postSynaptic['HSNR'][self.nextState] += 3
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['MVULVA'][self.nextState] += 7
            self.postSynaptic['RIFL'][self.nextState] += 3
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['SABVL'][self.nextState] += 2
            self.postSynaptic['VC5'][self.nextState] += 3

    def HSNR(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 1
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 2
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['AWBL'][self.nextState] += 1
            self.postSynaptic['BDUR'][self.nextState] += 1
            self.postSynaptic['DA5'][self.nextState] += 1
            self.postSynaptic['DA6'][self.nextState] += 1
            self.postSynaptic['HSNL'][self.nextState] += 2
            self.postSynaptic['MVULVA'][self.nextState] += 6
            self.postSynaptic['PVNR'][self.nextState] += 2
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['RIFR'][self.nextState] += 4
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['SABVR'][self.nextState] += 1
            self.postSynaptic['VA6'][self.nextState] += 1
            self.postSynaptic['VC2'][self.nextState] += 3
            self.postSynaptic['VC3'][self.nextState] += 1
            self.postSynaptic['VD4'][self.nextState] += 2

    def I1L(self, ):
            self.postSynaptic['I1R'][self.nextState] += 1
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['I5'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RIPR'][self.nextState] += 1

    def I1R(self, ):
            self.postSynaptic['I1L'][self.nextState] += 1
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['I5'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RIPR'][self.nextState] += 1

    def I2L(self, ):
            self.postSynaptic['I1L'][self.nextState] += 1
            self.postSynaptic['I1R'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 4

    def I2R(self, ):
            self.postSynaptic['I1L'][self.nextState] += 1
            self.postSynaptic['I1R'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 4

    def I3(self, ):
            self.postSynaptic['M1'][self.nextState] += 4
            self.postSynaptic['M2L'][self.nextState] += 2
            self.postSynaptic['M2R'][self.nextState] += 2

    def I4(self, ):
            self.postSynaptic['I2L'][self.nextState] += 5
            self.postSynaptic['I2R'][self.nextState] += 5
            self.postSynaptic['I5'][self.nextState] += 2
            self.postSynaptic['M1'][self.nextState] += 4

    def I5(self, ):
            self.postSynaptic['I1L'][self.nextState] += 4
            self.postSynaptic['I1R'][self.nextState] += 3
            self.postSynaptic['M1'][self.nextState] += 2
            self.postSynaptic['M5'][self.nextState] += 2
            self.postSynaptic['MI'][self.nextState] += 4

    def I6(self, ):
            self.postSynaptic['I2L'][self.nextState] += 2
            self.postSynaptic['I2R'][self.nextState] += 2
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['M4'][self.nextState] += 1
            self.postSynaptic['M5'][self.nextState] += 2
            self.postSynaptic['NSML'][self.nextState] += 2
            self.postSynaptic['NSMR'][self.nextState] += 2

    def IL1DL(self, ):
            self.postSynaptic['IL1DR'][self.nextState] += 1
            self.postSynaptic['IL1L'][self.nextState] += 1
            self.postSynaptic['MDL01'][self.nextState] += 1
            self.postSynaptic['MDL02'][self.nextState] += 1
            self.postSynaptic['MDL04'][self.nextState] += 2
            self.postSynaptic['OLLL'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 2
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 4
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['URYDL'][self.nextState] += 1

    def IL1DR(self, ):
            self.postSynaptic['IL1DL'][self.nextState] += 1
            self.postSynaptic['IL1R'][self.nextState] += 1
            self.postSynaptic['MDR01'][self.nextState] += 4
            self.postSynaptic['MDR02'][self.nextState] += 3
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['RIPR'][self.nextState] += 5
            self.postSynaptic['RMDVR'][self.nextState] += 5
            self.postSynaptic['RMEV'][self.nextState] += 1

    def IL1L(self, ):
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['IL1DL'][self.nextState] += 2
            self.postSynaptic['IL1VL'][self.nextState] += 1
            self.postSynaptic['MDL01'][self.nextState] += 3
            self.postSynaptic['MDL03'][self.nextState] += 3
            self.postSynaptic['MDL05'][self.nextState] += 4
            self.postSynaptic['MVL01'][self.nextState] += 3
            self.postSynaptic['MVL03'][self.nextState] += 3
            self.postSynaptic['RMDDL'][self.nextState] += 5
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 3
            self.postSynaptic['RMDVL'][self.nextState] += 4
            self.postSynaptic['RMDVR'][self.nextState] += 2
            self.postSynaptic['RMER'][self.nextState] += 1

    def IL1R(self, ):
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['IL1DR'][self.nextState] += 2
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['MDR01'][self.nextState] += 3
            self.postSynaptic['MDR03'][self.nextState] += 3
            self.postSynaptic['MVR01'][self.nextState] += 3
            self.postSynaptic['MVR03'][self.nextState] += 3
            self.postSynaptic['RMDDL'][self.nextState] += 3
            self.postSynaptic['RMDDR'][self.nextState] += 2
            self.postSynaptic['RMDL'][self.nextState] += 4
            self.postSynaptic['RMDR'][self.nextState] += 2
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 4
            self.postSynaptic['RMEL'][self.nextState] += 2
            self.postSynaptic['RMHL'][self.nextState] += 1
            self.postSynaptic['URXR'][self.nextState] += 2

    def IL1VL(self, ):
            self.postSynaptic['IL1L'][self.nextState] += 2
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['MVL01'][self.nextState] += 5
            self.postSynaptic['MVL02'][self.nextState] += 4
            self.postSynaptic['RIPL'][self.nextState] += 4
            self.postSynaptic['RMDDL'][self.nextState] += 5
            self.postSynaptic['RMED'][self.nextState] += 1
            self.postSynaptic['URYVL'][self.nextState] += 1

    def IL1VR(self, ):
            self.postSynaptic['IL1R'][self.nextState] += 2
            self.postSynaptic['IL1VL'][self.nextState] += 1
            self.postSynaptic['IL2R'][self.nextState] += 1
            self.postSynaptic['IL2VR'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 5
            self.postSynaptic['MVR02'][self.nextState] += 5
            self.postSynaptic['RIPR'][self.nextState] += 6
            self.postSynaptic['RMDDR'][self.nextState] += 10
            self.postSynaptic['RMER'][self.nextState] += 1

    def IL2DL(self, ):
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['IL1DL'][self.nextState] += 7
            self.postSynaptic['OLQDL'][self.nextState] += 2
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 10
            self.postSynaptic['RMEL'][self.nextState] += 4
            self.postSynaptic['RMER'][self.nextState] += 3
            self.postSynaptic['URADL'][self.nextState] += 3

    def IL2DR(self, ):
            self.postSynaptic['CEPDR'][self.nextState] += 1
            self.postSynaptic['IL1DR'][self.nextState] += 7
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIPR'][self.nextState] += 11
            self.postSynaptic['RMED'][self.nextState] += 1
            self.postSynaptic['RMEL'][self.nextState] += 2
            self.postSynaptic['RMER'][self.nextState] += 2
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['URADR'][self.nextState] += 3

    def IL2L(self, ):
            self.postSynaptic['ADEL'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['IL1L'][self.nextState] += 1
            self.postSynaptic['OLQDL'][self.nextState] += 5
            self.postSynaptic['OLQVL'][self.nextState] += 8
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 7
            self.postSynaptic['RMDL'][self.nextState] += 3
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 2
            self.postSynaptic['RMEV'][self.nextState] += 2
            self.postSynaptic['RMGL'][self.nextState] += 1
            self.postSynaptic['URXL'][self.nextState] += 2

    def IL2R(self, ):
            self.postSynaptic['ADER'][self.nextState] += 1
            self.postSynaptic['IL1R'][self.nextState] += 1
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 2
            self.postSynaptic['OLQVR'][self.nextState] += 7
            self.postSynaptic['RIH'][self.nextState] += 6
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMEL'][self.nextState] += 2
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['URBR'][self.nextState] += 1
            self.postSynaptic['URXR'][self.nextState] += 1

    def IL2VL(self, ):
            self.postSynaptic['BAGR'][self.nextState] += 1
            self.postSynaptic['IL1VL'][self.nextState] += 7
            self.postSynaptic['IL2L'][self.nextState] += 1
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 2
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RMEL'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 4
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['URAVL'][self.nextState] += 3

    def IL2VR(self, ):
            self.postSynaptic['IL1VR'][self.nextState] += 6
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 2
            self.postSynaptic['RIH'][self.nextState] += 3
            self.postSynaptic['RIPR'][self.nextState] += 15
            self.postSynaptic['RMEL'][self.nextState] += 3
            self.postSynaptic['RMER'][self.nextState] += 2
            self.postSynaptic['RMEV'][self.nextState] += 3
            self.postSynaptic['URAVR'][self.nextState] += 4
            self.postSynaptic['URXR'][self.nextState] += 1

    def LUAL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVAR'][self.nextState] += 6
            self.postSynaptic['AVDL'][self.nextState] += 4
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['PHBL'][self.nextState] += 1
            self.postSynaptic['PLML'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 1
            self.postSynaptic['PVWL'][self.nextState] += 1

    def LUAR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 3
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['PLMR'][self.nextState] += 1
            self.postSynaptic['PQR'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 3
            self.postSynaptic['PVR'][self.nextState] += 2
            self.postSynaptic['PVWL'][self.nextState] += 1

    def M1(self, ):
            self.postSynaptic['I2L'][self.nextState] += 2
            self.postSynaptic['I2R'][self.nextState] += 2
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['I4'][self.nextState] += 1

    def M2L(self, ):
            self.postSynaptic['I1L'][self.nextState] += 3
            self.postSynaptic['I1R'][self.nextState] += 3
            self.postSynaptic['I3'][self.nextState] += 3
            self.postSynaptic['M2R'][self.nextState] += 1
            self.postSynaptic['M5'][self.nextState] += 1
            self.postSynaptic['MI'][self.nextState] += 4

    def M2R(self, ):
            self.postSynaptic['I1L'][self.nextState] += 3
            self.postSynaptic['I1R'][self.nextState] += 3
            self.postSynaptic['I3'][self.nextState] += 3
            self.postSynaptic['M3L'][self.nextState] += 1
            self.postSynaptic['M3R'][self.nextState] += 1
            self.postSynaptic['M5'][self.nextState] += 1
            self.postSynaptic['MI'][self.nextState] += 4

    def M3L(self, ):
            self.postSynaptic['I1L'][self.nextState] += 4
            self.postSynaptic['I1R'][self.nextState] += 4
            self.postSynaptic['I4'][self.nextState] += 2
            self.postSynaptic['I5'][self.nextState] += 3
            self.postSynaptic['I6'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 2
            self.postSynaptic['M3R'][self.nextState] += 1
            self.postSynaptic['MCL'][self.nextState] += 1
            self.postSynaptic['MCR'][self.nextState] += 1
            self.postSynaptic['MI'][self.nextState] += 2
            self.postSynaptic['NSML'][self.nextState] += 2
            self.postSynaptic['NSMR'][self.nextState] += 3

    def M3R(self, ):
            self.postSynaptic['I1L'][self.nextState] += 4
            self.postSynaptic['I1R'][self.nextState] += 4
            self.postSynaptic['I3'][self.nextState] += 2
            self.postSynaptic['I4'][self.nextState] += 6
            self.postSynaptic['I5'][self.nextState] += 3
            self.postSynaptic['I6'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 2
            self.postSynaptic['M3L'][self.nextState] += 1
            self.postSynaptic['MCL'][self.nextState] += 1
            self.postSynaptic['MCR'][self.nextState] += 1
            self.postSynaptic['MI'][self.nextState] += 2
            self.postSynaptic['NSML'][self.nextState] += 2
            self.postSynaptic['NSMR'][self.nextState] += 3

    def M4(self, ):
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['I5'][self.nextState] += 13
            self.postSynaptic['I6'][self.nextState] += 3
            self.postSynaptic['M2L'][self.nextState] += 1
            self.postSynaptic['M2R'][self.nextState] += 1
            self.postSynaptic['M4'][self.nextState] += 6
            self.postSynaptic['M5'][self.nextState] += 1
            self.postSynaptic['NSML'][self.nextState] += 1
            self.postSynaptic['NSMR'][self.nextState] += 1

    def M5(self, ):
            self.postSynaptic['I5'][self.nextState] += 3
            self.postSynaptic['I5'][self.nextState] += 1
            self.postSynaptic['I6'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 2
            self.postSynaptic['M2L'][self.nextState] += 2
            self.postSynaptic['M2R'][self.nextState] += 2
            self.postSynaptic['M5'][self.nextState] += 4

    def MCL(self, ):
            self.postSynaptic['I1L'][self.nextState] += 3
            self.postSynaptic['I1R'][self.nextState] += 3
            self.postSynaptic['I2L'][self.nextState] += 1
            self.postSynaptic['I2R'][self.nextState] += 1
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 2
            self.postSynaptic['M2L'][self.nextState] += 2
            self.postSynaptic['M2R'][self.nextState] += 2

    def MCR(self, ):
            self.postSynaptic['I1L'][self.nextState] += 3
            self.postSynaptic['I1R'][self.nextState] += 3
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['M1'][self.nextState] += 2
            self.postSynaptic['M2L'][self.nextState] += 2
            self.postSynaptic['M2R'][self.nextState] += 2

    def MI(self, ):
            self.postSynaptic['I1L'][self.nextState] += 1
            self.postSynaptic['I1R'][self.nextState] += 1
            self.postSynaptic['I3'][self.nextState] += 1
            self.postSynaptic['I4'][self.nextState] += 1
            self.postSynaptic['I5'][self.nextState] += 2
            self.postSynaptic['M1'][self.nextState] += 1
            self.postSynaptic['M2L'][self.nextState] += 2
            self.postSynaptic['M2R'][self.nextState] += 2
            self.postSynaptic['M3L'][self.nextState] += 1
            self.postSynaptic['M3R'][self.nextState] += 1
            self.postSynaptic['MCL'][self.nextState] += 2
            self.postSynaptic['MCR'][self.nextState] += 2

    def NSML(self, ):
            self.postSynaptic['I1L'][self.nextState] += 1
            self.postSynaptic['I1R'][self.nextState] += 2
            self.postSynaptic['I2L'][self.nextState] += 6
            self.postSynaptic['I2R'][self.nextState] += 6
            self.postSynaptic['I3'][self.nextState] += 2
            self.postSynaptic['I4'][self.nextState] += 3
            self.postSynaptic['I5'][self.nextState] += 2
            self.postSynaptic['I6'][self.nextState] += 2
            self.postSynaptic['M3L'][self.nextState] += 2
            self.postSynaptic['M3R'][self.nextState] += 2

    def NSMR(self, ):
            self.postSynaptic['I1L'][self.nextState] += 2
            self.postSynaptic['I1R'][self.nextState] += 2
            self.postSynaptic['I2L'][self.nextState] += 6
            self.postSynaptic['I2R'][self.nextState] += 6
            self.postSynaptic['I3'][self.nextState] += 2
            self.postSynaptic['I4'][self.nextState] += 3
            self.postSynaptic['I5'][self.nextState] += 2
            self.postSynaptic['I6'][self.nextState] += 2
            self.postSynaptic['M3L'][self.nextState] += 2
            self.postSynaptic['M3R'][self.nextState] += 2

    def OLLL(self, ):
            self.postSynaptic['AVER'][self.nextState] += 21
            self.postSynaptic['CEPDL'][self.nextState] += 3
            self.postSynaptic['CEPVL'][self.nextState] += 4
            self.postSynaptic['IL1DL'][self.nextState] += 1
            self.postSynaptic['IL1VL'][self.nextState] += 2
            self.postSynaptic['OLLR'][self.nextState] += 2
            self.postSynaptic['RIBL'][self.nextState] += 8
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 7
            self.postSynaptic['RMDL'][self.nextState] += 2
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['RMEL'][self.nextState] += 2
            self.postSynaptic['SMDDL'][self.nextState] += 3
            self.postSynaptic['SMDDR'][self.nextState] += 4
            self.postSynaptic['SMDVR'][self.nextState] += 4
            self.postSynaptic['URYDL'][self.nextState] += 1

    def OLLR(self, ):
            self.postSynaptic['AVEL'][self.nextState] += 16
            self.postSynaptic['CEPDR'][self.nextState] += 1
            self.postSynaptic['CEPVR'][self.nextState] += 6
            self.postSynaptic['IL1DR'][self.nextState] += 3
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['IL2R'][self.nextState] += 1
            self.postSynaptic['OLLL'][self.nextState] += 2
            self.postSynaptic['RIBR'][self.nextState] += 10
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 10
            self.postSynaptic['RMDL'][self.nextState] += 3
            self.postSynaptic['RMDVR'][self.nextState] += 3
            self.postSynaptic['RMER'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 4
            self.postSynaptic['SMDVR'][self.nextState] += 3

    def OLQDL(self, ):
            self.postSynaptic['CEPDL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 2
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 4
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 3
            self.postSynaptic['URBL'][self.nextState] += 1

    def OLQDR(self, ):
            self.postSynaptic['CEPDR'][self.nextState] += 2
            self.postSynaptic['RIBR'][self.nextState] += 2
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 3
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['RMHR'][self.nextState] += 1
            self.postSynaptic['SIBVR'][self.nextState] += 2
            self.postSynaptic['URBR'][self.nextState] += 1

    def OLQVL(self, ):
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['CEPVL'][self.nextState] += 1
            self.postSynaptic['IL1VL'][self.nextState] += 1
            self.postSynaptic['IL2VL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 4
            self.postSynaptic['SIBDL'][self.nextState] += 3
            self.postSynaptic['URBL'][self.nextState] += 1

    def OLQVR(self, ):
            self.postSynaptic['CEPVR'][self.nextState] += 1
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 2
            self.postSynaptic['RIPR'][self.nextState] += 2
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 4
            self.postSynaptic['RMER'][self.nextState] += 1
            self.postSynaptic['SIBDR'][self.nextState] += 4
            self.postSynaptic['URBR'][self.nextState] += 1

    def PDA(self, ):
            self.postSynaptic['AS11'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['DD6'][self.nextState] += 1
            self.postSynaptic['MDL21'][self.nextState] += 2
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['VD13'][self.nextState] += 3

    def PDB(self, ):
            self.postSynaptic['AS11'][self.nextState] += 2
            self.postSynaptic['MVL22'][self.nextState] += 1
            self.postSynaptic['MVR21'][self.nextState] += 1
            self.postSynaptic['RID'][self.nextState] += 2
            self.postSynaptic['VD13'][self.nextState] += 2

    def PDEL(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 6
            self.postSynaptic['DVA'][self.nextState] += 24
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PDER'][self.nextState] += 3
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVM'][self.nextState] += 2
            self.postSynaptic['PVM'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 2
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VD11'][self.nextState] += 1

    def PDER(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 16
            self.postSynaptic['DVA'][self.nextState] += 35
            self.postSynaptic['PDEL'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVM'][self.nextState] += 1
            self.postSynaptic['VA8'][self.nextState] += 1
            self.postSynaptic['VD9'][self.nextState] += 1

    def PHAL(self, ):
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 3
            self.postSynaptic['AVG'][self.nextState] += 5
            self.postSynaptic['AVHL'][self.nextState] += 1
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 2
            self.postSynaptic['PHAR'][self.nextState] += 5
            self.postSynaptic['PHAR'][self.nextState] += 2
            self.postSynaptic['PHBL'][self.nextState] += 5
            self.postSynaptic['PHBR'][self.nextState] += 5
            self.postSynaptic['PVQL'][self.nextState] += 2

    def PHAR(self, ):
            self.postSynaptic['AVG'][self.nextState] += 3
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['DA8'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['PHAL'][self.nextState] += 6
            self.postSynaptic['PHAL'][self.nextState] += 2
            self.postSynaptic['PHBL'][self.nextState] += 1
            self.postSynaptic['PHBR'][self.nextState] += 5
            self.postSynaptic['PVPL'][self.nextState] += 3
            self.postSynaptic['PVQL'][self.nextState] += 2

    def PHBL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 9
            self.postSynaptic['AVAR'][self.nextState] += 6
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['PHBR'][self.nextState] += 1
            self.postSynaptic['PHBR'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 13
            self.postSynaptic['VA12'][self.nextState] += 1

    def PHBR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 7
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVHL'][self.nextState] += 1
            self.postSynaptic['DA8'][self.nextState] += 1
            self.postSynaptic['PHBL'][self.nextState] += 1
            self.postSynaptic['PHBL'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 6
            self.postSynaptic['PVCR'][self.nextState] += 3
            self.postSynaptic['VA12'][self.nextState] += 2

    def PHCL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 7
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 6
            self.postSynaptic['LUAL'][self.nextState] += 1
            self.postSynaptic['PHCR'][self.nextState] += 1
            self.postSynaptic['PLML'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['VA12'][self.nextState] += 3

    def PHCR(self, ):
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 2
            self.postSynaptic['DVA'][self.nextState] += 8
            self.postSynaptic['LUAR'][self.nextState] += 1
            self.postSynaptic['PHCL'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 9
            self.postSynaptic['VA12'][self.nextState] += 2

    def PLML(self, ):
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['LUAL'][self.nextState] += 1
            self.postSynaptic['PHCL'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 1

    def PLMR(self, ):
            self.postSynaptic['AS6'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 4
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 4
            self.postSynaptic['DVA'][self.nextState] += 5
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['LUAR'][self.nextState] += 1
            self.postSynaptic['PDEL'][self.nextState] += 2
            self.postSynaptic['PDER'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 2

    def PLNL(self, ):
            self.postSynaptic['SAADL'][self.nextState] += 5
            self.postSynaptic['SMBVL'][self.nextState] += 6

    def PLNR(self, ):
            self.postSynaptic['SAADR'][self.nextState] += 4
            self.postSynaptic['SMBVR'][self.nextState] += 6

    def PQR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 8
            self.postSynaptic['AVAR'][self.nextState] += 11
            self.postSynaptic['AVDL'][self.nextState] += 7
            self.postSynaptic['AVDR'][self.nextState] += 6
            self.postSynaptic['AVG'][self.nextState] += 1
            self.postSynaptic['LUAR'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 4

    def PVCL(self, ):
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVAR'][self.nextState] += 4
            self.postSynaptic['AVBL'][self.nextState] += 5
            self.postSynaptic['AVBR'][self.nextState] += 12
            self.postSynaptic['AVDL'][self.nextState] += 5
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 3
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 4
            self.postSynaptic['AVJR'][self.nextState] += 2
            self.postSynaptic['DA2'][self.nextState] += 1
            self.postSynaptic['DA5'][self.nextState] += 1
            self.postSynaptic['DA6'][self.nextState] += 1
            self.postSynaptic['DB2'][self.nextState] += 3
            self.postSynaptic['DB3'][self.nextState] += 4
            self.postSynaptic['DB4'][self.nextState] += 3
            self.postSynaptic['DB5'][self.nextState] += 2
            self.postSynaptic['DB6'][self.nextState] += 2
            self.postSynaptic['DB7'][self.nextState] += 3
            self.postSynaptic['DVA'][self.nextState] += 5
            self.postSynaptic['PLML'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 7
            self.postSynaptic['RID'][self.nextState] += 5
            self.postSynaptic['RIS'][self.nextState] += 2
            self.postSynaptic['SIBVL'][self.nextState] += 2
            self.postSynaptic['VB10'][self.nextState] += 3
            self.postSynaptic['VB11'][self.nextState] += 1
            self.postSynaptic['VB3'][self.nextState] += 1
            self.postSynaptic['VB4'][self.nextState] += 1
            self.postSynaptic['VB5'][self.nextState] += 1
            self.postSynaptic['VB6'][self.nextState] += 2
            self.postSynaptic['VB8'][self.nextState] += 1
            self.postSynaptic['VB9'][self.nextState] += 2

    def PVCR(self, ):
            self.postSynaptic['AQR'][self.nextState] += 1
            self.postSynaptic['AS2'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 12
            self.postSynaptic['AVAR'][self.nextState] += 10
            self.postSynaptic['AVBL'][self.nextState] += 8
            self.postSynaptic['AVBR'][self.nextState] += 6
            self.postSynaptic['AVDL'][self.nextState] += 5
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 3
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['DB2'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 3
            self.postSynaptic['DB4'][self.nextState] += 4
            self.postSynaptic['DB5'][self.nextState] += 1
            self.postSynaptic['DB6'][self.nextState] += 2
            self.postSynaptic['DB7'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['LUAR'][self.nextState] += 1
            self.postSynaptic['PDEL'][self.nextState] += 2
            self.postSynaptic['PHCR'][self.nextState] += 1
            self.postSynaptic['PLMR'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 8
            self.postSynaptic['PVDL'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 1
            self.postSynaptic['PVWL'][self.nextState] += 2
            self.postSynaptic['PVWR'][self.nextState] += 2
            self.postSynaptic['RID'][self.nextState] += 5
            self.postSynaptic['SIBVR'][self.nextState] += 2
            self.postSynaptic['VA8'][self.nextState] += 2
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VB10'][self.nextState] += 1
            self.postSynaptic['VB4'][self.nextState] += 3
            self.postSynaptic['VB6'][self.nextState] += 2
            self.postSynaptic['VB7'][self.nextState] += 3
            self.postSynaptic['VB8'][self.nextState] += 1

    def PVDL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVAR'][self.nextState] += 6
            self.postSynaptic['DD5'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 6
            self.postSynaptic['VD10'][self.nextState] += 6

    def PVDR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVAR'][self.nextState] += 9
            self.postSynaptic['DVA'][self.nextState] += 3
            self.postSynaptic['PVCL'][self.nextState] += 13
            self.postSynaptic['PVCR'][self.nextState] += 10
            self.postSynaptic['PVDL'][self.nextState] += 1
            self.postSynaptic['VA9'][self.nextState] += 1

    def PVM(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 11
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['AVM'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 3
            self.postSynaptic['PDEL'][self.nextState] += 7
            self.postSynaptic['PDEL'][self.nextState] += 1
            self.postSynaptic['PDER'][self.nextState] += 8
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['PVR'][self.nextState] += 1

    def PVNL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 3
            self.postSynaptic['AVDL'][self.nextState] += 3
            self.postSynaptic['AVDR'][self.nextState] += 3
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['AVG'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 5
            self.postSynaptic['AVJR'][self.nextState] += 5
            self.postSynaptic['AVL'][self.nextState] += 2
            self.postSynaptic['BDUL'][self.nextState] += 1
            self.postSynaptic['BDUR'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 2
            self.postSynaptic['MVL09'][self.nextState] += 3
            self.postSynaptic['PQR'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVNR'][self.nextState] += 5
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['PVWL'][self.nextState] += 1
            self.postSynaptic['RIFL'][self.nextState] += 1

    def PVNR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 3
            self.postSynaptic['AVJL'][self.nextState] += 4
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 2
            self.postSynaptic['BDUL'][self.nextState] += 1
            self.postSynaptic['BDUR'][self.nextState] += 2
            self.postSynaptic['DD3'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 2
            self.postSynaptic['MVL12'][self.nextState] += 1
            self.postSynaptic['MVL13'][self.nextState] += 2
            self.postSynaptic['PQR'][self.nextState] += 2
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 2
            self.postSynaptic['PVWL'][self.nextState] += 2
            self.postSynaptic['VC2'][self.nextState] += 1
            self.postSynaptic['VC3'][self.nextState] += 1
            self.postSynaptic['VD12'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 1
            self.postSynaptic['VD7'][self.nextState] += 1

    def PVPL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['AQR'][self.nextState] += 8
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 5
            self.postSynaptic['AVBR'][self.nextState] += 6
            self.postSynaptic['AVDR'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 6
            self.postSynaptic['DVC'][self.nextState] += 2
            self.postSynaptic['PHAR'][self.nextState] += 3
            self.postSynaptic['PQR'][self.nextState] += 4
            self.postSynaptic['PVCR'][self.nextState] += 3
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 2
            self.postSynaptic['VD13'][self.nextState] += 2
            self.postSynaptic['VD3'][self.nextState] += 1

    def PVPR(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 1
            self.postSynaptic['AQR'][self.nextState] += 11
            self.postSynaptic['ASHR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 4
            self.postSynaptic['AVBR'][self.nextState] += 5
            self.postSynaptic['AVHL'][self.nextState] += 3
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 4
            self.postSynaptic['DD2'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 14
            self.postSynaptic['PVCL'][self.nextState] += 4
            self.postSynaptic['PVCR'][self.nextState] += 7
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 2
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RIMR'][self.nextState] += 1
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['VD4'][self.nextState] += 1
            self.postSynaptic['VD5'][self.nextState] += 1

    def PVQL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['AIAL'][self.nextState] += 3
            self.postSynaptic['ASJL'][self.nextState] += 1
            self.postSynaptic['ASKL'][self.nextState] += 4
            self.postSynaptic['ASKL'][self.nextState] += 5
            self.postSynaptic['HSNL'][self.nextState] += 2
            self.postSynaptic['PVQR'][self.nextState] += 2
            self.postSynaptic['RMGL'][self.nextState] += 1

    def PVQR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['AIAR'][self.nextState] += 7
            self.postSynaptic['ASER'][self.nextState] += 1
            self.postSynaptic['ASKR'][self.nextState] += 8
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['AWAR'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PVNL'][self.nextState] += 1
            self.postSynaptic['PVQL'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIFR'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 1

    def PVR(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['ALML'][self.nextState] += 1
            self.postSynaptic['AS6'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 4
            self.postSynaptic['AVBR'][self.nextState] += 4
            self.postSynaptic['AVJL'][self.nextState] += 3
            self.postSynaptic['AVJR'][self.nextState] += 2
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['DB2'][self.nextState] += 1
            self.postSynaptic['DB3'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 3
            self.postSynaptic['IL1DL'][self.nextState] += 1
            self.postSynaptic['IL1DR'][self.nextState] += 1
            self.postSynaptic['IL1VL'][self.nextState] += 1
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['LUAL'][self.nextState] += 1
            self.postSynaptic['LUAR'][self.nextState] += 1
            self.postSynaptic['PDEL'][self.nextState] += 1
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PLMR'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 3
            self.postSynaptic['RIPR'][self.nextState] += 3
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['URADL'][self.nextState] += 1

    def PVT(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 3
            self.postSynaptic['AIBR'][self.nextState] += 5
            self.postSynaptic['AVKL'][self.nextState] += 9
            self.postSynaptic['AVKR'][self.nextState] += 7
            self.postSynaptic['AVL'][self.nextState] += 2
            self.postSynaptic['DVC'][self.nextState] += 2
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 2
            self.postSynaptic['RIGR'][self.nextState] += 3
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['RMFL'][self.nextState] += 2
            self.postSynaptic['RMFR'][self.nextState] += 3
            self.postSynaptic['SMBDR'][self.nextState] += 1

    def PVWL(self, ):
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 2
            self.postSynaptic['PVT'][self.nextState] += 2
            self.postSynaptic['PVWR'][self.nextState] += 1
            self.postSynaptic['VA12'][self.nextState] += 1

    def PVWR(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 2
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['VA12'][self.nextState] += 1

    def RIAL(self, ):
            self.postSynaptic['CEPVL'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIVL'][self.nextState] += 2
            self.postSynaptic['RIVR'][self.nextState] += 4
            self.postSynaptic['RMDDL'][self.nextState] += 12
            self.postSynaptic['RMDDR'][self.nextState] += 7
            self.postSynaptic['RMDL'][self.nextState] += 6
            self.postSynaptic['RMDR'][self.nextState] += 6
            self.postSynaptic['RMDVL'][self.nextState] += 9
            self.postSynaptic['RMDVR'][self.nextState] += 11
            self.postSynaptic['SIADL'][self.nextState] += 2
            self.postSynaptic['SMDDL'][self.nextState] += 8
            self.postSynaptic['SMDDR'][self.nextState] += 10
            self.postSynaptic['SMDVL'][self.nextState] += 6
            self.postSynaptic['SMDVR'][self.nextState] += 11

    def RIAR(self, ):
            self.postSynaptic['CEPVR'][self.nextState] += 1
            self.postSynaptic['IL1R'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 4
            self.postSynaptic['RIVL'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 10
            self.postSynaptic['RMDDR'][self.nextState] += 11
            self.postSynaptic['RMDL'][self.nextState] += 3
            self.postSynaptic['RMDR'][self.nextState] += 8
            self.postSynaptic['RMDVL'][self.nextState] += 12
            self.postSynaptic['RMDVR'][self.nextState] += 10
            self.postSynaptic['SAADR'][self.nextState] += 1
            self.postSynaptic['SIADL'][self.nextState] += 1
            self.postSynaptic['SIADR'][self.nextState] += 1
            self.postSynaptic['SIAVL'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 7
            self.postSynaptic['SMDDR'][self.nextState] += 7
            self.postSynaptic['SMDVL'][self.nextState] += 13
            self.postSynaptic['SMDVR'][self.nextState] += 7

    def RIBL(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 2
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVDR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 5
            self.postSynaptic['BAGR'][self.nextState] += 1
            self.postSynaptic['OLQDL'][self.nextState] += 2
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 3
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 3
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['SIADL'][self.nextState] += 1
            self.postSynaptic['SIAVL'][self.nextState] += 1
            self.postSynaptic['SIBDL'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 1
            self.postSynaptic['SIBVR'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 4

    def RIBR(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 3
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['BAGL'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 2
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 2
            self.postSynaptic['RIBL'][self.nextState] += 3
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 2
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['SIADR'][self.nextState] += 1
            self.postSynaptic['SIAVR'][self.nextState] += 1
            self.postSynaptic['SIBDR'][self.nextState] += 1
            self.postSynaptic['SIBVR'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 2

    def RICL(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 6
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 2
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 1
            self.postSynaptic['RIMR'][self.nextState] += 3
            self.postSynaptic['RIVR'][self.nextState] += 1
            self.postSynaptic['RMFR'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 2
            self.postSynaptic['SMDDL'][self.nextState] += 3
            self.postSynaptic['SMDDR'][self.nextState] += 3
            self.postSynaptic['SMDVR'][self.nextState] += 1

    def RICR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 5
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 4
            self.postSynaptic['SMDDR'][self.nextState] += 3
            self.postSynaptic['SMDVL'][self.nextState] += 2
            self.postSynaptic['SMDVR'][self.nextState] += 1

    def RID(self, ):
            self.postSynaptic['ALA'][self.nextState] += 1
            self.postSynaptic['AS2'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['DA6'][self.nextState] += 3
            self.postSynaptic['DA9'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 4
            self.postSynaptic['DD2'][self.nextState] += 4
            self.postSynaptic['DD3'][self.nextState] += 3
            self.postSynaptic['MDL14'][self.nextState] += -2
            self.postSynaptic['MDL21'][self.nextState] += -3
            self.postSynaptic['PDB'][self.nextState] += 2
            self.postSynaptic['VD13'][self.nextState] += 1
            self.postSynaptic['VD5'][self.nextState] += 1

    def RIFL(self, ):
            self.postSynaptic['ALML'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 10
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVG'][self.nextState] += 1
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 2
            self.postSynaptic['PVPL'][self.nextState] += 3
            self.postSynaptic['RIML'][self.nextState] += 4
            self.postSynaptic['VD1'][self.nextState] += 1

    def RIFR(self, ):
            self.postSynaptic['ASHR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 17
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVG'][self.nextState] += 1
            self.postSynaptic['AVHL'][self.nextState] += 1
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVJR'][self.nextState] += 2
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 4
            self.postSynaptic['RIMR'][self.nextState] += 4
            self.postSynaptic['RIPR'][self.nextState] += 1

    def RIGL(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 3
            self.postSynaptic['AIZR'][self.nextState] += 1
            self.postSynaptic['ALNL'][self.nextState] += 1
            self.postSynaptic['AQR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 2
            self.postSynaptic['BAGR'][self.nextState] += 2
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['OLLL'][self.nextState] += 1
            self.postSynaptic['OLQDL'][self.nextState] += 1
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 2
            self.postSynaptic['RIGR'][self.nextState] += 3
            self.postSynaptic['RIR'][self.nextState] += 2
            self.postSynaptic['RMEL'][self.nextState] += 2
            self.postSynaptic['RMHR'][self.nextState] += 3
            self.postSynaptic['URYDL'][self.nextState] += 1
            self.postSynaptic['URYVL'][self.nextState] += 1
            self.postSynaptic['VB2'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 2

    def RIGR(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 3
            self.postSynaptic['ALNR'][self.nextState] += 1
            self.postSynaptic['AQR'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['AVKL'][self.nextState] += 4
            self.postSynaptic['AVKR'][self.nextState] += 2
            self.postSynaptic['BAGL'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 1
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 2
            self.postSynaptic['RIGL'][self.nextState] += 3
            self.postSynaptic['RIR'][self.nextState] += 1
            self.postSynaptic['RMHL'][self.nextState] += 4
            self.postSynaptic['URYDR'][self.nextState] += 1
            self.postSynaptic['URYVR'][self.nextState] += 1

    def RIH(self, ):
            self.postSynaptic['ADFR'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 4
            self.postSynaptic['AIZR'][self.nextState] += 4
            self.postSynaptic['AUAR'][self.nextState] += 1
            self.postSynaptic['BAGR'][self.nextState] += 1
            self.postSynaptic['CEPDL'][self.nextState] += 2
            self.postSynaptic['CEPDR'][self.nextState] += 2
            self.postSynaptic['CEPVL'][self.nextState] += 2
            self.postSynaptic['CEPVR'][self.nextState] += 2
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['IL2L'][self.nextState] += 2
            self.postSynaptic['IL2R'][self.nextState] += 1
            self.postSynaptic['OLQDL'][self.nextState] += 4
            self.postSynaptic['OLQDR'][self.nextState] += 2
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['OLQVR'][self.nextState] += 6
            self.postSynaptic['RIAL'][self.nextState] += 10
            self.postSynaptic['RIAR'][self.nextState] += 8
            self.postSynaptic['RIBL'][self.nextState] += 5
            self.postSynaptic['RIBR'][self.nextState] += 4
            self.postSynaptic['RIPL'][self.nextState] += 4
            self.postSynaptic['RIPR'][self.nextState] += 6
            self.postSynaptic['RMER'][self.nextState] += 2
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['URYVR'][self.nextState] += 1

    def RIML(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AIYL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 3
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 3
            self.postSynaptic['MDR05'][self.nextState] += 2
            self.postSynaptic['MVR05'][self.nextState] += 2
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMFR'][self.nextState] += 1
            self.postSynaptic['SAADR'][self.nextState] += 1
            self.postSynaptic['SAAVL'][self.nextState] += 3
            self.postSynaptic['SAAVR'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 5
            self.postSynaptic['SMDVL'][self.nextState] += 1

    def RIMR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 4
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AIYR'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 5
            self.postSynaptic['AVEL'][self.nextState] += 3
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['MDL05'][self.nextState] += 1
            self.postSynaptic['MDL07'][self.nextState] += 1
            self.postSynaptic['MVL05'][self.nextState] += 1
            self.postSynaptic['MVL07'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 2
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMFL'][self.nextState] += 1
            self.postSynaptic['RMFR'][self.nextState] += 1
            self.postSynaptic['SAAVL'][self.nextState] += 3
            self.postSynaptic['SAAVR'][self.nextState] += 3
            self.postSynaptic['SMDDL'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 4

    def RIPL(self, ):
            self.postSynaptic['OLQDL'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 1
            self.postSynaptic['RMED'][self.nextState] += 1

    def RIPR(self, ):
            self.postSynaptic['OLQDL'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 1
            self.postSynaptic['RMED'][self.nextState] += 1

    def RIR(self, ):
            self.postSynaptic['AFDR'][self.nextState] += 1
            self.postSynaptic['AIZL'][self.nextState] += 3
            self.postSynaptic['AIZR'][self.nextState] += 5
            self.postSynaptic['AUAL'][self.nextState] += 1
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['BAGL'][self.nextState] += 1
            self.postSynaptic['BAGR'][self.nextState] += 2
            self.postSynaptic['DVA'][self.nextState] += 2
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 5
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['URXL'][self.nextState] += 5
            self.postSynaptic['URXR'][self.nextState] += 1

    def RIS(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 7
            self.postSynaptic['AVER'][self.nextState] += 7
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 4
            self.postSynaptic['AVL'][self.nextState] += 2
            self.postSynaptic['CEPDR'][self.nextState] += 1
            self.postSynaptic['CEPVL'][self.nextState] += 2
            self.postSynaptic['CEPVR'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 3
            self.postSynaptic['RIBR'][self.nextState] += 5
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 5
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 2
            self.postSynaptic['RMDR'][self.nextState] += 4
            self.postSynaptic['SMDDL'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 3
            self.postSynaptic['SMDVL'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 1
            self.postSynaptic['URYVR'][self.nextState] += 1

    def RIVL(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['MVR05'][self.nextState] += -2
            self.postSynaptic['MVR06'][self.nextState] += -2
            self.postSynaptic['MVR08'][self.nextState] += -3
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIVR'][self.nextState] += 2
            self.postSynaptic['RMDL'][self.nextState] += 2
            self.postSynaptic['SAADR'][self.nextState] += 3
            self.postSynaptic['SDQR'][self.nextState] += 2
            self.postSynaptic['SIAVR'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 1

    def RIVR(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['MVL05'][self.nextState] += -2
            self.postSynaptic['MVL06'][self.nextState] += -2
            self.postSynaptic['MVL08'][self.nextState] += -2
            self.postSynaptic['MVR04'][self.nextState] += -2
            self.postSynaptic['MVR06'][self.nextState] += -2
            self.postSynaptic['RIAL'][self.nextState] += 2
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIVL'][self.nextState] += 2
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 1
            self.postSynaptic['SAADL'][self.nextState] += 2
            self.postSynaptic['SDQR'][self.nextState] += 2
            self.postSynaptic['SIAVL'][self.nextState] += 2
            self.postSynaptic['SMDDL'][self.nextState] += 2
            self.postSynaptic['SMDVR'][self.nextState] += 4

    def RMDDL(self, ):
            self.postSynaptic['MDR01'][self.nextState] += 1
            self.postSynaptic['MDR02'][self.nextState] += 1
            self.postSynaptic['MDR03'][self.nextState] += 1
            self.postSynaptic['MDR04'][self.nextState] += 1
            self.postSynaptic['MDR08'][self.nextState] += 2
            self.postSynaptic['MVR01'][self.nextState] += 1
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 7
            self.postSynaptic['SMDDL'][self.nextState] += 1

    def RMDDR(self, ):
            self.postSynaptic['MDL01'][self.nextState] += 1
            self.postSynaptic['MDL02'][self.nextState] += 1
            self.postSynaptic['MDL03'][self.nextState] += 2
            self.postSynaptic['MDL04'][self.nextState] += 1
            self.postSynaptic['MDR04'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 1
            self.postSynaptic['MVR02'][self.nextState] += 1
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 12
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['SAADR'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['URYDL'][self.nextState] += 1

    def RMDL(self, ):
            self.postSynaptic['MDL03'][self.nextState] += 1
            self.postSynaptic['MDL05'][self.nextState] += 2
            self.postSynaptic['MDR01'][self.nextState] += 1
            self.postSynaptic['MDR03'][self.nextState] += 1
            self.postSynaptic['MVL01'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 1
            self.postSynaptic['MVR03'][self.nextState] += 1
            self.postSynaptic['MVR05'][self.nextState] += 2
            self.postSynaptic['MVR07'][self.nextState] += 1
            self.postSynaptic['OLLR'][self.nextState] += 2
            self.postSynaptic['RIAL'][self.nextState] += 4
            self.postSynaptic['RIAR'][self.nextState] += 3
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 3
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 1
            self.postSynaptic['RMFL'][self.nextState] += 1

    def RMDR(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['MDL03'][self.nextState] += 1
            self.postSynaptic['MDL05'][self.nextState] += 1
            self.postSynaptic['MDR05'][self.nextState] += 1
            self.postSynaptic['MVL03'][self.nextState] += 1
            self.postSynaptic['MVL05'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 3
            self.postSynaptic['RIAR'][self.nextState] += 7
            self.postSynaptic['RIMR'][self.nextState] += 2
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 1

    def RMDVL(self, ):
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['MDR01'][self.nextState] += 1
            self.postSynaptic['MVL04'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 1
            self.postSynaptic['MVR02'][self.nextState] += 1
            self.postSynaptic['MVR03'][self.nextState] += 1
            self.postSynaptic['MVR04'][self.nextState] += 1
            self.postSynaptic['MVR05'][self.nextState] += 1
            self.postSynaptic['MVR06'][self.nextState] += 1
            self.postSynaptic['MVR08'][self.nextState] += 1
            self.postSynaptic['OLQDL'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 6
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['SAAVL'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 1

    def RMDVR(self, ):
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['MDL01'][self.nextState] += 1
            self.postSynaptic['MVL01'][self.nextState] += 1
            self.postSynaptic['MVL02'][self.nextState] += 1
            self.postSynaptic['MVL03'][self.nextState] += 1
            self.postSynaptic['MVL04'][self.nextState] += 1
            self.postSynaptic['MVL05'][self.nextState] += 1
            self.postSynaptic['MVL06'][self.nextState] += 1
            self.postSynaptic['MVL08'][self.nextState] += 1
            self.postSynaptic['MVR04'][self.nextState] += 1
            self.postSynaptic['MVR06'][self.nextState] += 1
            self.postSynaptic['MVR08'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 4
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['SAAVR'][self.nextState] += 1
            self.postSynaptic['SIBDR'][self.nextState] += 1
            self.postSynaptic['SIBVR'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 1

    def RMED(self, ):
            self.postSynaptic['IL1VL'][self.nextState] += 1
            self.postSynaptic['MVL02'][self.nextState] += -4
            self.postSynaptic['MVL04'][self.nextState] += -4
            self.postSynaptic['MVL06'][self.nextState] += -4
            self.postSynaptic['MVR02'][self.nextState] += -4
            self.postSynaptic['MVR04'][self.nextState] += -4
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIPL'][self.nextState] += 1
            self.postSynaptic['RIPR'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 2

    def RMEL(self, ):
            self.postSynaptic['MDR01'][self.nextState] += -5
            self.postSynaptic['MDR03'][self.nextState] += -5
            self.postSynaptic['MVR01'][self.nextState] += -5
            self.postSynaptic['MVR03'][self.nextState] += -5
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 1

    def RMER(self, ):
            self.postSynaptic['MDL01'][self.nextState] += -7
            self.postSynaptic['MDL03'][self.nextState] += -7
            self.postSynaptic['MVL01'][self.nextState] += -7
            self.postSynaptic['RMEV'][self.nextState] += 1

    def RMEV(self, ):
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 1
            self.postSynaptic['IL1DL'][self.nextState] += 1
            self.postSynaptic['IL1DR'][self.nextState] += 1
            self.postSynaptic['MDL02'][self.nextState] += -3
            self.postSynaptic['MDL04'][self.nextState] += -3
            self.postSynaptic['MDL06'][self.nextState] += -3
            self.postSynaptic['MDR02'][self.nextState] += -3
            self.postSynaptic['MDR04'][self.nextState] += -3
            self.postSynaptic['RMED'][self.nextState] += 2
            self.postSynaptic['RMEL'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 1

    def RMFL(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 4
            self.postSynaptic['AVKR'][self.nextState] += 4
            self.postSynaptic['MDR03'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 1
            self.postSynaptic['MVR03'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 3
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['URBR'][self.nextState] += 1

    def RMFR(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 3
            self.postSynaptic['AVKR'][self.nextState] += 3
            self.postSynaptic['RMDL'][self.nextState] += 2

    def RMGL(self, ):
            self.postSynaptic['ADAL'][self.nextState] += 1
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['ALML'][self.nextState] += 1
            self.postSynaptic['ALNL'][self.nextState] += 1
            self.postSynaptic['ASHL'][self.nextState] += 2
            self.postSynaptic['ASKL'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['AWBL'][self.nextState] += 1
            self.postSynaptic['CEPDL'][self.nextState] += 1
            self.postSynaptic['IL2L'][self.nextState] += 1
            self.postSynaptic['MDL05'][self.nextState] += 2
            self.postSynaptic['MVL05'][self.nextState] += 2
            self.postSynaptic['RID'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 3
            self.postSynaptic['RMDVL'][self.nextState] += 3
            self.postSynaptic['RMHL'][self.nextState] += 3
            self.postSynaptic['RMHR'][self.nextState] += 1
            self.postSynaptic['SIAVL'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 3
            self.postSynaptic['SIBVR'][self.nextState] += 1
            self.postSynaptic['SMBVL'][self.nextState] += 1
            self.postSynaptic['URXL'][self.nextState] += 2

    def RMGR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['AIMR'][self.nextState] += 1
            self.postSynaptic['ALNR'][self.nextState] += 1
            self.postSynaptic['ASHR'][self.nextState] += 2
            self.postSynaptic['ASKR'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 3
            self.postSynaptic['AVJL'][self.nextState] += 1
            self.postSynaptic['AWBR'][self.nextState] += 1
            self.postSynaptic['IL2R'][self.nextState] += 1
            self.postSynaptic['MDR05'][self.nextState] += 1
            self.postSynaptic['MVR05'][self.nextState] += 1
            self.postSynaptic['MVR07'][self.nextState] += 1
            self.postSynaptic['RIR'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 4
            self.postSynaptic['RMDR'][self.nextState] += 2
            self.postSynaptic['RMDVR'][self.nextState] += 5
            self.postSynaptic['RMHR'][self.nextState] += 1
            self.postSynaptic['URXR'][self.nextState] += 2

    def RMHL(self, ):
            self.postSynaptic['MDR01'][self.nextState] += 2
            self.postSynaptic['MDR03'][self.nextState] += 3
            self.postSynaptic['MVR01'][self.nextState] += 2
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 3
            self.postSynaptic['SIBVR'][self.nextState] += 1

    def RMHR(self, ):
            self.postSynaptic['MDL01'][self.nextState] += 2
            self.postSynaptic['MDL03'][self.nextState] += 2
            self.postSynaptic['MDL05'][self.nextState] += 2
            self.postSynaptic['MVL01'][self.nextState] += 2
            self.postSynaptic['RMER'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 1
            self.postSynaptic['RMGR'][self.nextState] += 1

    def SAADL(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['RIML'][self.nextState] += 3
            self.postSynaptic['RIMR'][self.nextState] += 6
            self.postSynaptic['RMGR'][self.nextState] += 1
            self.postSynaptic['SMBDL'][self.nextState] += 1

    def SAADR(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['OLLL'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 4
            self.postSynaptic['RIMR'][self.nextState] += 5
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMFL'][self.nextState] += 1
            self.postSynaptic['RMGL'][self.nextState] += 1

    def SAAVL(self, ):
            self.postSynaptic['AIBL'][self.nextState] += 1
            self.postSynaptic['ALNL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 16
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RIMR'][self.nextState] += 12
            self.postSynaptic['RMDVL'][self.nextState] += 2
            self.postSynaptic['RMFR'][self.nextState] += 2
            self.postSynaptic['SMBVR'][self.nextState] += 3
            self.postSynaptic['SMDDR'][self.nextState] += 8

    def SAAVR(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 13
            self.postSynaptic['RIML'][self.nextState] += 5
            self.postSynaptic['RIMR'][self.nextState] += 2
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['SMBVL'][self.nextState] += 2
            self.postSynaptic['SMDDL'][self.nextState] += 6

    def SABD(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 4
            self.postSynaptic['VA2'][self.nextState] += 4
            self.postSynaptic['VA3'][self.nextState] += 2
            self.postSynaptic['VA4'][self.nextState] += 1

    def SABVL(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['DA1'][self.nextState] += 2
            self.postSynaptic['DA2'][self.nextState] += 1

    def SABVR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['DA1'][self.nextState] += 3

    def SDQL(self, ):
            self.postSynaptic['ALML'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['AVEL'][self.nextState] += 1
            self.postSynaptic['FLPL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 3
            self.postSynaptic['RMFL'][self.nextState] += 1
            self.postSynaptic['SDQR'][self.nextState] += 1

    def SDQR(self, ):
            self.postSynaptic['ADLL'][self.nextState] += 1
            self.postSynaptic['AIBL'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['AVBL'][self.nextState] += 7
            self.postSynaptic['AVBR'][self.nextState] += 4
            self.postSynaptic['DVA'][self.nextState] += 3
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RIVL'][self.nextState] += 2
            self.postSynaptic['RIVR'][self.nextState] += 2
            self.postSynaptic['RMHL'][self.nextState] += 2
            self.postSynaptic['RMHR'][self.nextState] += 1
            self.postSynaptic['SDQL'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 1

    def SIADL(self, ):
            self.postSynaptic['RIBL'][self.nextState] += 1

    def SIADR(self, ):
            self.postSynaptic['RIBR'][self.nextState] += 1

    def SIAVL(self, ):
            self.postSynaptic['RIBL'][self.nextState] += 1

    def SIAVR(self, ):
            self.postSynaptic['RIBR'][self.nextState] += 1

    def SIBDL(self, ):
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 1

    def SIBDR(self, ):
            self.postSynaptic['AIML'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['SIBVR'][self.nextState] += 1

    def SIBVL(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['SDQR'][self.nextState] += 1
            self.postSynaptic['SIBDL'][self.nextState] += 1

    def SIBVR(self, ):
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RMHL'][self.nextState] += 1
            self.postSynaptic['SIBDR'][self.nextState] += 1

    def SMBDL(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 1
            self.postSynaptic['MDR01'][self.nextState] += 2
            self.postSynaptic['MDR02'][self.nextState] += 2
            self.postSynaptic['MDR03'][self.nextState] += 2
            self.postSynaptic['MDR04'][self.nextState] += 2
            self.postSynaptic['MDR06'][self.nextState] += 3
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RMED'][self.nextState] += 3
            self.postSynaptic['SAADL'][self.nextState] += 1
            self.postSynaptic['SAAVR'][self.nextState] += 1

    def SMBDR(self, ):
            self.postSynaptic['ALNL'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 2
            self.postSynaptic['MDL02'][self.nextState] += 1
            self.postSynaptic['MDL03'][self.nextState] += 1
            self.postSynaptic['MDL04'][self.nextState] += 1
            self.postSynaptic['MDL06'][self.nextState] += 2
            self.postSynaptic['MDR04'][self.nextState] += 1
            self.postSynaptic['MDR08'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RMED'][self.nextState] += 4
            self.postSynaptic['SAAVL'][self.nextState] += 3

    def SMBVL(self, ):
            self.postSynaptic['MVL01'][self.nextState] += 1
            self.postSynaptic['MVL02'][self.nextState] += 1
            self.postSynaptic['MVL03'][self.nextState] += 1
            self.postSynaptic['MVL04'][self.nextState] += 1
            self.postSynaptic['MVL05'][self.nextState] += 1
            self.postSynaptic['MVL06'][self.nextState] += 1
            self.postSynaptic['MVL08'][self.nextState] += 1
            self.postSynaptic['PLNL'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 5
            self.postSynaptic['SAADL'][self.nextState] += 3
            self.postSynaptic['SAAVR'][self.nextState] += 2

    def SMBVR(self, ):
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['AVKR'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 1
            self.postSynaptic['MVR02'][self.nextState] += 1
            self.postSynaptic['MVR03'][self.nextState] += 1
            self.postSynaptic['MVR04'][self.nextState] += 1
            self.postSynaptic['MVR06'][self.nextState] += 1
            self.postSynaptic['MVR07'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 3
            self.postSynaptic['SAADR'][self.nextState] += 4
            self.postSynaptic['SAAVL'][self.nextState] += 3

    def SMDDL(self, ):
            self.postSynaptic['MDL04'][self.nextState] += 1
            self.postSynaptic['MDL06'][self.nextState] += 1
            self.postSynaptic['MDL08'][self.nextState] += 1
            self.postSynaptic['MDR02'][self.nextState] += 1
            self.postSynaptic['MDR03'][self.nextState] += 1
            self.postSynaptic['MDR04'][self.nextState] += 1
            self.postSynaptic['MDR05'][self.nextState] += 1
            self.postSynaptic['MDR06'][self.nextState] += 1
            self.postSynaptic['MDR07'][self.nextState] += 1
            self.postSynaptic['MVL02'][self.nextState] += 1
            self.postSynaptic['MVL04'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 2

    def SMDDR(self, ):
            self.postSynaptic['MDL04'][self.nextState] += 1
            self.postSynaptic['MDL05'][self.nextState] += 1
            self.postSynaptic['MDL06'][self.nextState] += 1
            self.postSynaptic['MDL08'][self.nextState] += 1
            self.postSynaptic['MDR04'][self.nextState] += 1
            self.postSynaptic['MDR06'][self.nextState] += 1
            self.postSynaptic['MVR02'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 2
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['VD1'][self.nextState] += 1

    def SMDVL(self, ):
            self.postSynaptic['MVL03'][self.nextState] += 1
            self.postSynaptic['MVL06'][self.nextState] += 1
            self.postSynaptic['MVR02'][self.nextState] += 1
            self.postSynaptic['MVR03'][self.nextState] += 1
            self.postSynaptic['MVR04'][self.nextState] += 1
            self.postSynaptic['MVR06'][self.nextState] += 1
            self.postSynaptic['PVR'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 3
            self.postSynaptic['RIAR'][self.nextState] += 8
            self.postSynaptic['RIBR'][self.nextState] += 2
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RIVL'][self.nextState] += 2
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 4
            self.postSynaptic['SMDVR'][self.nextState] += 1

    def SMDVR(self, ):
            self.postSynaptic['MVL02'][self.nextState] += 1
            self.postSynaptic['MVL03'][self.nextState] += 1
            self.postSynaptic['MVL04'][self.nextState] += 1
            self.postSynaptic['MVR07'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 7
            self.postSynaptic['RIAR'][self.nextState] += 5
            self.postSynaptic['RIBL'][self.nextState] += 2
            self.postSynaptic['RIVR'][self.nextState] += 1
            self.postSynaptic['RIVR'][self.nextState] += 2
            self.postSynaptic['RMDDL'][self.nextState] += 1
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['SMDDL'][self.nextState] += 2
            self.postSynaptic['SMDVL'][self.nextState] += 1
            self.postSynaptic['VB1'][self.nextState] += 1

    def URADL(self, ):
            self.postSynaptic['IL1DL'][self.nextState] += 2
            self.postSynaptic['MDL02'][self.nextState] += 2
            self.postSynaptic['MDL03'][self.nextState] += 2
            self.postSynaptic['MDL04'][self.nextState] += 2
            self.postSynaptic['RIPL'][self.nextState] += 3
            self.postSynaptic['RMEL'][self.nextState] += 1

    def URADR(self, ):
            self.postSynaptic['IL1DR'][self.nextState] += 1
            self.postSynaptic['MDR01'][self.nextState] += 3
            self.postSynaptic['MDR02'][self.nextState] += 2
            self.postSynaptic['MDR03'][self.nextState] += 3
            self.postSynaptic['RIPR'][self.nextState] += 3
            self.postSynaptic['RMDVR'][self.nextState] += 1
            self.postSynaptic['RMED'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 1
            self.postSynaptic['URYDR'][self.nextState] += 1

    def URAVL(self, ):
            self.postSynaptic['MVL01'][self.nextState] += 2
            self.postSynaptic['MVL02'][self.nextState] += 2
            self.postSynaptic['MVL03'][self.nextState] += 3
            self.postSynaptic['MVL04'][self.nextState] += 2
            self.postSynaptic['RIPL'][self.nextState] += 3
            self.postSynaptic['RMEL'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 1
            self.postSynaptic['RMEV'][self.nextState] += 2

    def URAVR(self, ):
            self.postSynaptic['IL1R'][self.nextState] += 1
            self.postSynaptic['MVR01'][self.nextState] += 2
            self.postSynaptic['MVR02'][self.nextState] += 2
            self.postSynaptic['MVR03'][self.nextState] += 2
            self.postSynaptic['MVR04'][self.nextState] += 2
            self.postSynaptic['RIPR'][self.nextState] += 3
            self.postSynaptic['RMDVL'][self.nextState] += 1
            self.postSynaptic['RMER'][self.nextState] += 2
            self.postSynaptic['RMEV'][self.nextState] += 2

    def URBL(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['CEPDL'][self.nextState] += 1
            self.postSynaptic['IL1L'][self.nextState] += 1
            self.postSynaptic['OLQDL'][self.nextState] += 1
            self.postSynaptic['OLQVL'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 1
            self.postSynaptic['SIAVL'][self.nextState] += 1
            self.postSynaptic['SMBDR'][self.nextState] += 1
            self.postSynaptic['URXL'][self.nextState] += 2

    def URBR(self, ):
            self.postSynaptic['ADAR'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['CEPDR'][self.nextState] += 1
            self.postSynaptic['IL1R'][self.nextState] += 3
            self.postSynaptic['IL2R'][self.nextState] += 1
            self.postSynaptic['OLQDR'][self.nextState] += 1
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['RICR'][self.nextState] += 1
            self.postSynaptic['RMDL'][self.nextState] += 1
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMFL'][self.nextState] += 1
            self.postSynaptic['SIAVR'][self.nextState] += 2
            self.postSynaptic['SMBDL'][self.nextState] += 1
            self.postSynaptic['URXR'][self.nextState] += 4

    def URXL(self, ):
            self.postSynaptic['ASHL'][self.nextState] += 1
            self.postSynaptic['AUAL'][self.nextState] += 5
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 4
            self.postSynaptic['AVJR'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 8
            self.postSynaptic['RICL'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 3
            self.postSynaptic['RMGL'][self.nextState] += 2
            self.postSynaptic['RMGL'][self.nextState] += 1

    def URXR(self, ):
            self.postSynaptic['AUAR'][self.nextState] += 4
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['IL2R'][self.nextState] += 1
            self.postSynaptic['OLQVR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 3
            self.postSynaptic['RIGR'][self.nextState] += 2
            self.postSynaptic['RIPR'][self.nextState] += 3
            self.postSynaptic['RMDR'][self.nextState] += 1
            self.postSynaptic['RMGR'][self.nextState] += 2
            self.postSynaptic['SIAVR'][self.nextState] += 1

    def URYDL(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['RIBL'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 4
            self.postSynaptic['RMDVL'][self.nextState] += 6
            self.postSynaptic['SMDDL'][self.nextState] += 1
            self.postSynaptic['SMDDR'][self.nextState] += 1

    def URYDR(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVEL'][self.nextState] += 2
            self.postSynaptic['AVER'][self.nextState] += 2
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 3
            self.postSynaptic['RMDVR'][self.nextState] += 5
            self.postSynaptic['SMDDL'][self.nextState] += 4

    def URYVL(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVER'][self.nextState] += 5
            self.postSynaptic['IL1VL'][self.nextState] += 1
            self.postSynaptic['RIAL'][self.nextState] += 1
            self.postSynaptic['RIBL'][self.nextState] += 2
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['RIH'][self.nextState] += 1
            self.postSynaptic['RIS'][self.nextState] += 1
            self.postSynaptic['RMDDL'][self.nextState] += 4
            self.postSynaptic['RMDVR'][self.nextState] += 2
            self.postSynaptic['SIBVR'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 4

    def URYVR(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVEL'][self.nextState] += 6
            self.postSynaptic['IL1VR'][self.nextState] += 1
            self.postSynaptic['RIAR'][self.nextState] += 1
            self.postSynaptic['RIBR'][self.nextState] += 1
            self.postSynaptic['RIGR'][self.nextState] += 1
            self.postSynaptic['RMDDR'][self.nextState] += 6
            self.postSynaptic['RMDVL'][self.nextState] += 4
            self.postSynaptic['SIBDR'][self.nextState] += 1
            self.postSynaptic['SIBVL'][self.nextState] += 1
            self.postSynaptic['SMDVL'][self.nextState] += 3

    def VA1(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 3
            self.postSynaptic['DA2'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 9
            self.postSynaptic['MVL07'][self.nextState] += 3
            self.postSynaptic['MVL08'][self.nextState] += 3
            self.postSynaptic['MVR07'][self.nextState] += 3
            self.postSynaptic['MVR08'][self.nextState] += 3
            self.postSynaptic['VD1'][self.nextState] += 2

    def VA2(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['DD1'][self.nextState] += 13
            self.postSynaptic['MVL07'][self.nextState] += 5
            self.postSynaptic['MVL10'][self.nextState] += 5
            self.postSynaptic['MVR07'][self.nextState] += 5
            self.postSynaptic['MVR10'][self.nextState] += 5
            self.postSynaptic['SABD'][self.nextState] += 3
            self.postSynaptic['VA3'][self.nextState] += 2
            self.postSynaptic['VB1'][self.nextState] += 2
            self.postSynaptic['VD1'][self.nextState] += 2
            self.postSynaptic['VD1'][self.nextState] += 1
            self.postSynaptic['VD2'][self.nextState] += 11

    def VA3(self, ):
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 18
            self.postSynaptic['DD2'][self.nextState] += 11
            self.postSynaptic['MVL09'][self.nextState] += 5
            self.postSynaptic['MVL10'][self.nextState] += 5
            self.postSynaptic['MVL12'][self.nextState] += 5
            self.postSynaptic['MVR09'][self.nextState] += 5
            self.postSynaptic['MVR10'][self.nextState] += 5
            self.postSynaptic['MVR12'][self.nextState] += 5
            self.postSynaptic['SABD'][self.nextState] += 2
            self.postSynaptic['VA4'][self.nextState] += 1
            self.postSynaptic['VD2'][self.nextState] += 3
            self.postSynaptic['VD3'][self.nextState] += 3

    def VA4(self, ):
            self.postSynaptic['AS2'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['AVDL'][self.nextState] += 1
            self.postSynaptic['DA5'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 21
            self.postSynaptic['MVL11'][self.nextState] += 6
            self.postSynaptic['MVL12'][self.nextState] += 6
            self.postSynaptic['MVR11'][self.nextState] += 6
            self.postSynaptic['MVR12'][self.nextState] += 6
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['VB3'][self.nextState] += 2
            self.postSynaptic['VD4'][self.nextState] += 3
            
    def VA5(self, ):
            self.postSynaptic['AS3'][self.nextState] += 2
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 3
            self.postSynaptic['DA5'][self.nextState] += 2
            self.postSynaptic['DD2'][self.nextState] += 5
            self.postSynaptic['DD3'][self.nextState] += 13
            self.postSynaptic['MVL11'][self.nextState] += 5
            self.postSynaptic['MVL14'][self.nextState] += 5
            self.postSynaptic['MVR11'][self.nextState] += 5
            self.postSynaptic['MVR14'][self.nextState] += 5
            self.postSynaptic['VD5'][self.nextState] += 2

    def VA6(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 6
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['DD3'][self.nextState] += 24
            self.postSynaptic['MVL13'][self.nextState] += 5
            self.postSynaptic['MVL14'][self.nextState] += 5
            self.postSynaptic['MVR13'][self.nextState] += 5
            self.postSynaptic['MVR14'][self.nextState] += 5
            self.postSynaptic['VB5'][self.nextState] += 2
            self.postSynaptic['VD5'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 2

    def VA7(self, ):
            self.postSynaptic['AS5'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 4
            self.postSynaptic['DD3'][self.nextState] += 3
            self.postSynaptic['DD4'][self.nextState] += 12
            self.postSynaptic['MVL13'][self.nextState] += 4
            self.postSynaptic['MVL15'][self.nextState] += 4
            self.postSynaptic['MVL16'][self.nextState] += 4
            self.postSynaptic['MVR13'][self.nextState] += 4
            self.postSynaptic['MVR15'][self.nextState] += 4
            self.postSynaptic['MVR16'][self.nextState] += 4
            self.postSynaptic['MVULVA'][self.nextState] += 4
            self.postSynaptic['VB3'][self.nextState] += 1
            self.postSynaptic['VD7'][self.nextState] += 9

    def VA8(self, ):
            self.postSynaptic['AS6'][self.nextState] += 1
            self.postSynaptic['AVAL'][self.nextState] += 10
            self.postSynaptic['AVAR'][self.nextState] += 4
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DD4'][self.nextState] += 21
            self.postSynaptic['MVL15'][self.nextState] += 6
            self.postSynaptic['MVL16'][self.nextState] += 6
            self.postSynaptic['MVR15'][self.nextState] += 6
            self.postSynaptic['MVR16'][self.nextState] += 6
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 2
            self.postSynaptic['VA8'][self.nextState] += 1
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VB6'][self.nextState] += 1
            self.postSynaptic['VB8'][self.nextState] += 1
            self.postSynaptic['VB8'][self.nextState] += 3
            self.postSynaptic['VB9'][self.nextState] += 3
            self.postSynaptic['VD7'][self.nextState] += 5
            self.postSynaptic['VD8'][self.nextState] += 5
            self.postSynaptic['VD8'][self.nextState] += 1

    def VA9(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DD4'][self.nextState] += 3
            self.postSynaptic['DD5'][self.nextState] += 15
            self.postSynaptic['DVB'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['MVL15'][self.nextState] += 5
            self.postSynaptic['MVL18'][self.nextState] += 5
            self.postSynaptic['MVR15'][self.nextState] += 5
            self.postSynaptic['MVR18'][self.nextState] += 5
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['VB8'][self.nextState] += 6
            self.postSynaptic['VB8'][self.nextState] += 1
            self.postSynaptic['VB9'][self.nextState] += 4
            self.postSynaptic['VD7'][self.nextState] += 1
            self.postSynaptic['VD9'][self.nextState] += 10

    def VA10(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['MVL17'][self.nextState] += 5
            self.postSynaptic['MVL18'][self.nextState] += 5
            self.postSynaptic['MVR17'][self.nextState] += 5
            self.postSynaptic['MVR18'][self.nextState] += 5

    def VA11(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['AVAR'][self.nextState] += 7
            self.postSynaptic['DD6'][self.nextState] += 10
            self.postSynaptic['MVL19'][self.nextState] += 5
            self.postSynaptic['MVL20'][self.nextState] += 5
            self.postSynaptic['MVR19'][self.nextState] += 5
            self.postSynaptic['MVR20'][self.nextState] += 5
            self.postSynaptic['PVNR'][self.nextState] += 2
            self.postSynaptic['VB10'][self.nextState] += 1
            self.postSynaptic['VD12'][self.nextState] += 4

    def VA12(self, ):
            self.postSynaptic['AS11'][self.nextState] += 2
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['DA8'][self.nextState] += 3
            self.postSynaptic['DA9'][self.nextState] += 5
            self.postSynaptic['DB7'][self.nextState] += 4
            self.postSynaptic['DD6'][self.nextState] += 2
            self.postSynaptic['LUAL'][self.nextState] += 2
            self.postSynaptic['MVL21'][self.nextState] += 5
            self.postSynaptic['MVL22'][self.nextState] += 5
            self.postSynaptic['MVL23'][self.nextState] += 5
            self.postSynaptic['MVR21'][self.nextState] += 5
            self.postSynaptic['MVR22'][self.nextState] += 5
            self.postSynaptic['MVR23'][self.nextState] += 5
            self.postSynaptic['MVR24'][self.nextState] += 5
            self.postSynaptic['PHCL'][self.nextState] += 1
            self.postSynaptic['PHCR'][self.nextState] += 1
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['PVCR'][self.nextState] += 3
            self.postSynaptic['VA11'][self.nextState] += 1
            self.postSynaptic['VB11'][self.nextState] += 1
            self.postSynaptic['VD12'][self.nextState] += 3
            self.postSynaptic['VD13'][self.nextState] += 11

    def VB1(self, ):
            self.postSynaptic['AIBR'][self.nextState] += 1
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 4
            self.postSynaptic['DB2'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 1
            self.postSynaptic['DVA'][self.nextState] += 1
            self.postSynaptic['MVL07'][self.nextState] += 1
            self.postSynaptic['MVL08'][self.nextState] += 1
            self.postSynaptic['MVR07'][self.nextState] += 1
            self.postSynaptic['MVR08'][self.nextState] += 1
            self.postSynaptic['RIML'][self.nextState] += 2
            self.postSynaptic['RMFL'][self.nextState] += 2
            self.postSynaptic['SAADL'][self.nextState] += 9
            self.postSynaptic['SAADR'][self.nextState] += 2
            self.postSynaptic['SABD'][self.nextState] += 1
            self.postSynaptic['SMDVR'][self.nextState] += 1
            self.postSynaptic['VA1'][self.nextState] += 3
            self.postSynaptic['VA3'][self.nextState] += 1
            self.postSynaptic['VB2'][self.nextState] += 4
            self.postSynaptic['VD1'][self.nextState] += 3
            self.postSynaptic['VD2'][self.nextState] += 1

    def VB2(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 3
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 20
            self.postSynaptic['DD2'][self.nextState] += 1
            self.postSynaptic['MVL07'][self.nextState] += 4
            self.postSynaptic['MVL09'][self.nextState] += 4
            self.postSynaptic['MVL10'][self.nextState] += 4
            self.postSynaptic['MVL12'][self.nextState] += 4
            self.postSynaptic['MVR07'][self.nextState] += 4
            self.postSynaptic['MVR09'][self.nextState] += 4
            self.postSynaptic['MVR10'][self.nextState] += 4
            self.postSynaptic['MVR12'][self.nextState] += 4
            self.postSynaptic['RIGL'][self.nextState] += 1
            self.postSynaptic['VA2'][self.nextState] += 1
            self.postSynaptic['VB1'][self.nextState] += 4
            self.postSynaptic['VB3'][self.nextState] += 1
            self.postSynaptic['VB5'][self.nextState] += 1
            self.postSynaptic['VB7'][self.nextState] += 2
            self.postSynaptic['VC2'][self.nextState] += 1
            self.postSynaptic['VD2'][self.nextState] += 9
            self.postSynaptic['VD3'][self.nextState] += 3

    def VB3(self, ):
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 37
            self.postSynaptic['MVL11'][self.nextState] += 6
            self.postSynaptic['MVL12'][self.nextState] += 6
            self.postSynaptic['MVL14'][self.nextState] += 6
            self.postSynaptic['MVR11'][self.nextState] += 6
            self.postSynaptic['MVR12'][self.nextState] += 6
            self.postSynaptic['MVR14'][self.nextState] += 6
            self.postSynaptic['VA4'][self.nextState] += 1
            self.postSynaptic['VA7'][self.nextState] += 1
            self.postSynaptic['VB2'][self.nextState] += 1

    def VB4(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DB1'][self.nextState] += 1
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DD2'][self.nextState] += 6
            self.postSynaptic['DD3'][self.nextState] += 16
            self.postSynaptic['MVL11'][self.nextState] += 5
            self.postSynaptic['MVL14'][self.nextState] += 5
            self.postSynaptic['MVR11'][self.nextState] += 5
            self.postSynaptic['MVR14'][self.nextState] += 5
            self.postSynaptic['VB5'][self.nextState] += 1

    def VB5(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['DD3'][self.nextState] += 27
            self.postSynaptic['MVL13'][self.nextState] += 6
            self.postSynaptic['MVL14'][self.nextState] += 6
            self.postSynaptic['MVR13'][self.nextState] += 6
            self.postSynaptic['MVR14'][self.nextState] += 6
            self.postSynaptic['VB2'][self.nextState] += 1
            self.postSynaptic['VB4'][self.nextState] += 1
            self.postSynaptic['VB6'][self.nextState] += 8

    def VB6(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['DA4'][self.nextState] += 1
            self.postSynaptic['DD4'][self.nextState] += 30
            self.postSynaptic['MVL15'][self.nextState] += 6
            self.postSynaptic['MVL16'][self.nextState] += 6
            self.postSynaptic['MVR15'][self.nextState] += 6
            self.postSynaptic['MVR16'][self.nextState] += 6
            self.postSynaptic['MVULVA'][self.nextState] += 6
            self.postSynaptic['VA8'][self.nextState] += 1
            self.postSynaptic['VB5'][self.nextState] += 1
            self.postSynaptic['VB7'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 1
            self.postSynaptic['VD7'][self.nextState] += 8

    def VB7(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 2
            self.postSynaptic['DD4'][self.nextState] += 2
            self.postSynaptic['MVL15'][self.nextState] += 5
            self.postSynaptic['MVR15'][self.nextState] += 5
            self.postSynaptic['VB2'][self.nextState] += 2

    def VB8(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 7
            self.postSynaptic['AVBR'][self.nextState] += 3
            self.postSynaptic['DD5'][self.nextState] += 30
            self.postSynaptic['MVL17'][self.nextState] += 5
            self.postSynaptic['MVL18'][self.nextState] += 5
            self.postSynaptic['MVL20'][self.nextState] += 5
            self.postSynaptic['MVR17'][self.nextState] += 5
            self.postSynaptic['MVR18'][self.nextState] += 5
            self.postSynaptic['MVR20'][self.nextState] += 5
            self.postSynaptic['VA8'][self.nextState] += 3
            self.postSynaptic['VA9'][self.nextState] += 9
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VB9'][self.nextState] += 6
            self.postSynaptic['VD10'][self.nextState] += 1
            self.postSynaptic['VD9'][self.nextState] += 10

    def VB9(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 5
            self.postSynaptic['AVAR'][self.nextState] += 4
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVBR'][self.nextState] += 6
            self.postSynaptic['DD5'][self.nextState] += 8
            self.postSynaptic['DVB'][self.nextState] += 1
            self.postSynaptic['MVL17'][self.nextState] += 6
            self.postSynaptic['MVL20'][self.nextState] += 6
            self.postSynaptic['MVR17'][self.nextState] += 6
            self.postSynaptic['MVR20'][self.nextState] += 6
            self.postSynaptic['PVCL'][self.nextState] += 2
            self.postSynaptic['VA8'][self.nextState] += 3
            self.postSynaptic['VA9'][self.nextState] += 4
            self.postSynaptic['VB8'][self.nextState] += 1
            self.postSynaptic['VB8'][self.nextState] += 3
            self.postSynaptic['VD10'][self.nextState] += 5

    def VB10(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['AVKL'][self.nextState] += 1
            self.postSynaptic['DD6'][self.nextState] += 9
            self.postSynaptic['MVL19'][self.nextState] += 5
            self.postSynaptic['MVL20'][self.nextState] += 5
            self.postSynaptic['MVR19'][self.nextState] += 5
            self.postSynaptic['MVR20'][self.nextState] += 5
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['VD11'][self.nextState] += 1
            self.postSynaptic['VD12'][self.nextState] += 2

    def VB11(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 2
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DD6'][self.nextState] += 7
            self.postSynaptic['MVL21'][self.nextState] += 5
            self.postSynaptic['MVL22'][self.nextState] += 5
            self.postSynaptic['MVL23'][self.nextState] += 5
            self.postSynaptic['MVR21'][self.nextState] += 5
            self.postSynaptic['MVR22'][self.nextState] += 5
            self.postSynaptic['MVR23'][self.nextState] += 5
            self.postSynaptic['MVR24'][self.nextState] += 5
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['VA12'][self.nextState] += 2

    def VC1(self, ):
            self.postSynaptic['AVL'][self.nextState] += 2
            self.postSynaptic['DD1'][self.nextState] += 7
            self.postSynaptic['DD2'][self.nextState] += 6
            self.postSynaptic['DD3'][self.nextState] += 6
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['MVULVA'][self.nextState] += 6
            self.postSynaptic['PVT'][self.nextState] += 2
            self.postSynaptic['VC2'][self.nextState] += 9
            self.postSynaptic['VC3'][self.nextState] += 3
            self.postSynaptic['VD1'][self.nextState] += 5
            self.postSynaptic['VD2'][self.nextState] += 1
            self.postSynaptic['VD3'][self.nextState] += 1
            self.postSynaptic['VD4'][self.nextState] += 2
            self.postSynaptic['VD5'][self.nextState] += 5
            self.postSynaptic['VD6'][self.nextState] += 1

    def VC2(self, ):
            self.postSynaptic['DB4'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 6
            self.postSynaptic['DD2'][self.nextState] += 4
            self.postSynaptic['DD3'][self.nextState] += 9
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['MVULVA'][self.nextState] += 10
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 2
            self.postSynaptic['VC1'][self.nextState] += 10
            self.postSynaptic['VC3'][self.nextState] += 6
            self.postSynaptic['VD1'][self.nextState] += 2
            self.postSynaptic['VD2'][self.nextState] += 2
            self.postSynaptic['VD4'][self.nextState] += 5
            self.postSynaptic['VD5'][self.nextState] += 5
            self.postSynaptic['VD6'][self.nextState] += 1

    def VC3(self, ):
            self.postSynaptic['AVL'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 2
            self.postSynaptic['DD2'][self.nextState] += 4
            self.postSynaptic['DD3'][self.nextState] += 5
            self.postSynaptic['DD4'][self.nextState] += 13
            self.postSynaptic['DVC'][self.nextState] += 1
            self.postSynaptic['HSNR'][self.nextState] += 1
            self.postSynaptic['MVULVA'][self.nextState] += 11
            self.postSynaptic['PVNR'][self.nextState] += 1
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['PVQR'][self.nextState] += 4
            self.postSynaptic['VC1'][self.nextState] += 4
            self.postSynaptic['VC2'][self.nextState] += 3
            self.postSynaptic['VC4'][self.nextState] += 1
            self.postSynaptic['VC5'][self.nextState] += 2
            self.postSynaptic['VD1'][self.nextState] += 1
            self.postSynaptic['VD2'][self.nextState] += 1
            self.postSynaptic['VD3'][self.nextState] += 1
            self.postSynaptic['VD4'][self.nextState] += 2
            self.postSynaptic['VD5'][self.nextState] += 4
            self.postSynaptic['VD6'][self.nextState] += 4
            self.postSynaptic['VD7'][self.nextState] += 5

    def VC4(self, ):
            self.postSynaptic['AVBL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['AVHR'][self.nextState] += 1
            self.postSynaptic['MVULVA'][self.nextState] += 7
            self.postSynaptic['VC1'][self.nextState] += 1
            self.postSynaptic['VC3'][self.nextState] += 5
            self.postSynaptic['VC5'][self.nextState] += 2

    def VC5(self, ):
            self.postSynaptic['AVFL'][self.nextState] += 1
            self.postSynaptic['AVFR'][self.nextState] += 1
            self.postSynaptic['DVC'][self.nextState] += 2
            self.postSynaptic['HSNL'][self.nextState] += 1
            self.postSynaptic['MVULVA'][self.nextState] += 2
            self.postSynaptic['OLLR'][self.nextState] += 1
            self.postSynaptic['PVT'][self.nextState] += 1
            self.postSynaptic['URBL'][self.nextState] += 3
            self.postSynaptic['VC3'][self.nextState] += 3
            self.postSynaptic['VC4'][self.nextState] += 2

    def VC6(self, ):
            self.postSynaptic['MVULVA'][self.nextState] += 1
            
    def VD1(self, ):
            self.postSynaptic['DD1'][self.nextState] += 5
            self.postSynaptic['DVC'][self.nextState] += 5
            self.postSynaptic['MVL05'][self.nextState] += -5
            self.postSynaptic['MVL08'][self.nextState] += -5
            self.postSynaptic['MVR05'][self.nextState] += -5
            self.postSynaptic['MVR08'][self.nextState] += -5
            self.postSynaptic['RIFL'][self.nextState] += 1
            self.postSynaptic['RIGL'][self.nextState] += 2
            self.postSynaptic['SMDDR'][self.nextState] += 1
            self.postSynaptic['VA1'][self.nextState] += 2
            self.postSynaptic['VA2'][self.nextState] += 1
            self.postSynaptic['VC1'][self.nextState] += 1
            self.postSynaptic['VD2'][self.nextState] += 7

    def VD2(self, ):
            self.postSynaptic['AS1'][self.nextState] += 1
            self.postSynaptic['DD1'][self.nextState] += 3
            self.postSynaptic['MVL07'][self.nextState] += -7
            self.postSynaptic['MVL10'][self.nextState] += -7
            self.postSynaptic['MVR07'][self.nextState] += -7
            self.postSynaptic['MVR10'][self.nextState] += -7
            self.postSynaptic['VA2'][self.nextState] += 9
            self.postSynaptic['VB2'][self.nextState] += 3
            self.postSynaptic['VD1'][self.nextState] += 7
            self.postSynaptic['VD3'][self.nextState] += 2

    def VD3(self, ):
            self.postSynaptic['MVL09'][self.nextState] += -7
            self.postSynaptic['MVL12'][self.nextState] += -9
            self.postSynaptic['MVR09'][self.nextState] += -7
            self.postSynaptic['MVR12'][self.nextState] += -7
            self.postSynaptic['PVPL'][self.nextState] += 1
            self.postSynaptic['VA3'][self.nextState] += 2
            self.postSynaptic['VB2'][self.nextState] += 2
            self.postSynaptic['VD2'][self.nextState] += 2
            self.postSynaptic['VD4'][self.nextState] += 1

    def VD4(self, ):
            self.postSynaptic['DD2'][self.nextState] += 2
            self.postSynaptic['MVL11'][self.nextState] += -9
            self.postSynaptic['MVL12'][self.nextState] += -9
            self.postSynaptic['MVR11'][self.nextState] += -9
            self.postSynaptic['MVR12'][self.nextState] += -9
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['VD3'][self.nextState] += 1
            self.postSynaptic['VD5'][self.nextState] += 1

    def VD5(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 1
            self.postSynaptic['MVL14'][self.nextState] += -17
            self.postSynaptic['MVR14'][self.nextState] += -17
            self.postSynaptic['PVPR'][self.nextState] += 1
            self.postSynaptic['VA5'][self.nextState] += 2
            self.postSynaptic['VB4'][self.nextState] += 2
            self.postSynaptic['VD4'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 2

    def VD6(self, ):
            self.postSynaptic['AVAL'][self.nextState] += 1
            self.postSynaptic['MVL13'][self.nextState] += -7
            self.postSynaptic['MVL14'][self.nextState] += -7
            self.postSynaptic['MVL16'][self.nextState] += -7
            self.postSynaptic['MVR13'][self.nextState] += -7
            self.postSynaptic['MVR14'][self.nextState] += -7
            self.postSynaptic['MVR16'][self.nextState] += -7
            self.postSynaptic['VA6'][self.nextState] += 1
            self.postSynaptic['VB5'][self.nextState] += 2
            self.postSynaptic['VD5'][self.nextState] += 2
            self.postSynaptic['VD7'][self.nextState] += 1

    def VD7(self, ):
            self.postSynaptic['MVL15'][self.nextState] += -7
            self.postSynaptic['MVL16'][self.nextState] += -7
            self.postSynaptic['MVR15'][self.nextState] += -7
            self.postSynaptic['MVR16'][self.nextState] += -7
            self.postSynaptic['MVULVA'][self.nextState] += -15
            self.postSynaptic['VA9'][self.nextState] += 1
            self.postSynaptic['VD6'][self.nextState] += 1

    def VD8(self, ):
            self.postSynaptic['DD4'][self.nextState] += 2
            self.postSynaptic['MVL15'][self.nextState] += -18
            self.postSynaptic['MVR15'][self.nextState] += -18
            self.postSynaptic['VA8'][self.nextState] += 5

    def VD9(self, ):
            self.postSynaptic['MVL17'][self.nextState] += -10
            self.postSynaptic['MVL18'][self.nextState] += -10
            self.postSynaptic['MVR17'][self.nextState] += -10
            self.postSynaptic['MVR18'][self.nextState] += -10
            self.postSynaptic['PDER'][self.nextState] += 1
            self.postSynaptic['VD10'][self.nextState] += 5

    def VD10(self, ):
            self.postSynaptic['AVBR'][self.nextState] += 1
            self.postSynaptic['DD5'][self.nextState] += 2
            self.postSynaptic['DVC'][self.nextState] += 4
            self.postSynaptic['MVL17'][self.nextState] += -9
            self.postSynaptic['MVL20'][self.nextState] += -9
            self.postSynaptic['MVR17'][self.nextState] += -9
            self.postSynaptic['MVR20'][self.nextState] += -9
            self.postSynaptic['VB9'][self.nextState] += 2
            self.postSynaptic['VD9'][self.nextState] += 5

    def VD11(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['MVL19'][self.nextState] += -9
            self.postSynaptic['MVL20'][self.nextState] += -9
            self.postSynaptic['MVR19'][self.nextState] += -9
            self.postSynaptic['MVR20'][self.nextState] += -9
            self.postSynaptic['VA11'][self.nextState] += 1
            self.postSynaptic['VB10'][self.nextState] += 1

    def VD12(self, ):
            self.postSynaptic['MVL19'][self.nextState] += -5
            self.postSynaptic['MVL21'][self.nextState] += -5
            self.postSynaptic['MVR19'][self.nextState] += -5
            self.postSynaptic['MVR22'][self.nextState] += -5
            self.postSynaptic['VA11'][self.nextState] += 3
            self.postSynaptic['VA12'][self.nextState] += 2
            self.postSynaptic['VB10'][self.nextState] += 1
            self.postSynaptic['VB11'][self.nextState] += 1

    def VD13(self, ):
            self.postSynaptic['AVAR'][self.nextState] += 2
            self.postSynaptic['MVL21'][self.nextState] += -9
            self.postSynaptic['MVL22'][self.nextState] += -9
            self.postSynaptic['MVL23'][self.nextState] += -9
            self.postSynaptic['MVR21'][self.nextState] += -9
            self.postSynaptic['MVR22'][self.nextState] += -9
            self.postSynaptic['MVR23'][self.nextState] += -9
            self.postSynaptic['MVR24'][self.nextState] += -9
            self.postSynaptic['PVCL'][self.nextState] += 1
            self.postSynaptic['PVCR'][self.nextState] += 1
            self.postSynaptic['PVPL'][self.nextState] += 2
            self.postSynaptic['VA12'][self.nextState] += 1

    def createpostSynaptic(self, ):
            # The self.postSynaptic dictionary maintains the accumulated values for
            # each neuron and muscle. The Accumulated values are initialized to Zero
            self.postSynaptic['ADAL'] = [0,0]
            self.postSynaptic['ADAR'] = [0,0]
            self.postSynaptic['ADEL'] = [0,0]
            self.postSynaptic['ADER'] = [0,0]
            self.postSynaptic['ADFL'] = [0,0]
            self.postSynaptic['ADFR'] = [0,0]
            self.postSynaptic['ADLL'] = [0,0]
            self.postSynaptic['ADLR'] = [0,0]
            self.postSynaptic['AFDL'] = [0,0]
            self.postSynaptic['AFDR'] = [0,0]
            self.postSynaptic['AIAL'] = [0,0]
            self.postSynaptic['AIAR'] = [0,0]
            self.postSynaptic['AIBL'] = [0,0]
            self.postSynaptic['AIBR'] = [0,0]
            self.postSynaptic['AIML'] = [0,0]
            self.postSynaptic['AIMR'] = [0,0]
            self.postSynaptic['AINL'] = [0,0]
            self.postSynaptic['AINR'] = [0,0]
            self.postSynaptic['AIYL'] = [0,0]
            self.postSynaptic['AIYR'] = [0,0]
            self.postSynaptic['AIZL'] = [0,0]
            self.postSynaptic['AIZR'] = [0,0]
            self.postSynaptic['ALA'] = [0,0]
            self.postSynaptic['ALML'] = [0,0]
            self.postSynaptic['ALMR'] = [0,0]
            self.postSynaptic['ALNL'] = [0,0]
            self.postSynaptic['ALNR'] = [0,0]
            self.postSynaptic['AQR'] = [0,0]
            self.postSynaptic['AS1'] = [0,0]
            self.postSynaptic['AS10'] = [0,0]
            self.postSynaptic['AS11'] = [0,0]
            self.postSynaptic['AS2'] = [0,0]
            self.postSynaptic['AS3'] = [0,0]
            self.postSynaptic['AS4'] = [0,0]
            self.postSynaptic['AS5'] = [0,0]
            self.postSynaptic['AS6'] = [0,0]
            self.postSynaptic['AS7'] = [0,0]
            self.postSynaptic['AS8'] = [0,0]
            self.postSynaptic['AS9'] = [0,0]
            self.postSynaptic['ASEL'] = [0,0]
            self.postSynaptic['ASER'] = [0,0]
            self.postSynaptic['ASGL'] = [0,0]
            self.postSynaptic['ASGR'] = [0,0]
            self.postSynaptic['ASHL'] = [0,0]
            self.postSynaptic['ASHR'] = [0,0]
            self.postSynaptic['ASIL'] = [0,0]
            self.postSynaptic['ASIR'] = [0,0]
            self.postSynaptic['ASJL'] = [0,0]
            self.postSynaptic['ASJR'] = [0,0]
            self.postSynaptic['ASKL'] = [0,0]
            self.postSynaptic['ASKR'] = [0,0]
            self.postSynaptic['AUAL'] = [0,0]
            self.postSynaptic['AUAR'] = [0,0]
            self.postSynaptic['AVAL'] = [0,0]
            self.postSynaptic['AVAR'] = [0,0]
            self.postSynaptic['AVBL'] = [0,0]
            self.postSynaptic['AVBR'] = [0,0]
            self.postSynaptic['AVDL'] = [0,0]
            self.postSynaptic['AVDR'] = [0,0]
            self.postSynaptic['AVEL'] = [0,0]
            self.postSynaptic['AVER'] = [0,0]
            self.postSynaptic['AVFL'] = [0,0]
            self.postSynaptic['AVFR'] = [0,0]
            self.postSynaptic['AVG'] = [0,0]
            self.postSynaptic['AVHL'] = [0,0]
            self.postSynaptic['AVHR'] = [0,0]
            self.postSynaptic['AVJL'] = [0,0]
            self.postSynaptic['AVJR'] = [0,0]
            self.postSynaptic['AVKL'] = [0,0]
            self.postSynaptic['AVKR'] = [0,0]
            self.postSynaptic['AVL'] = [0,0]
            self.postSynaptic['AVM'] = [0,0]
            self.postSynaptic['AWAL'] = [0,0]
            self.postSynaptic['AWAR'] = [0,0]
            self.postSynaptic['AWBL'] = [0,0]
            self.postSynaptic['AWBR'] = [0,0]
            self.postSynaptic['AWCL'] = [0,0]
            self.postSynaptic['AWCR'] = [0,0]
            self.postSynaptic['BAGL'] = [0,0]
            self.postSynaptic['BAGR'] = [0,0]
            self.postSynaptic['BDUL'] = [0,0]
            self.postSynaptic['BDUR'] = [0,0]
            self.postSynaptic['CEPDL'] = [0,0]
            self.postSynaptic['CEPDR'] = [0,0]
            self.postSynaptic['CEPVL'] = [0,0]
            self.postSynaptic['CEPVR'] = [0,0]
            self.postSynaptic['DA1'] = [0,0]
            self.postSynaptic['DA2'] = [0,0]
            self.postSynaptic['DA3'] = [0,0]
            self.postSynaptic['DA4'] = [0,0]
            self.postSynaptic['DA5'] = [0,0]
            self.postSynaptic['DA6'] = [0,0]
            self.postSynaptic['DA7'] = [0,0]
            self.postSynaptic['DA8'] = [0,0]
            self.postSynaptic['DA9'] = [0,0]
            self.postSynaptic['DB1'] = [0,0]
            self.postSynaptic['DB2'] = [0,0]
            self.postSynaptic['DB3'] = [0,0]
            self.postSynaptic['DB4'] = [0,0]
            self.postSynaptic['DB5'] = [0,0]
            self.postSynaptic['DB6'] = [0,0]
            self.postSynaptic['DB7'] = [0,0]
            self.postSynaptic['DD1'] = [0,0]
            self.postSynaptic['DD2'] = [0,0]
            self.postSynaptic['DD3'] = [0,0]
            self.postSynaptic['DD4'] = [0,0]
            self.postSynaptic['DD5'] = [0,0]
            self.postSynaptic['DD6'] = [0,0]
            self.postSynaptic['DVA'] = [0,0]
            self.postSynaptic['DVB'] = [0,0]
            self.postSynaptic['DVC'] = [0,0]
            self.postSynaptic['FLPL'] = [0,0]
            self.postSynaptic['FLPR'] = [0,0]
            self.postSynaptic['HSNL'] = [0,0]
            self.postSynaptic['HSNR'] = [0,0]
            self.postSynaptic['I1L'] = [0,0]
            self.postSynaptic['I1R'] = [0,0]
            self.postSynaptic['I2L'] = [0,0]
            self.postSynaptic['I2R'] = [0,0]
            self.postSynaptic['I3'] = [0,0]
            self.postSynaptic['I4'] = [0,0]
            self.postSynaptic['I5'] = [0,0]
            self.postSynaptic['I6'] = [0,0]
            self.postSynaptic['IL1DL'] = [0,0]
            self.postSynaptic['IL1DR'] = [0,0]
            self.postSynaptic['IL1L'] = [0,0]
            self.postSynaptic['IL1R'] = [0,0]
            self.postSynaptic['IL1VL'] = [0,0]
            self.postSynaptic['IL1VR'] = [0,0]
            self.postSynaptic['IL2L'] = [0,0]
            self.postSynaptic['IL2R'] = [0,0]
            self.postSynaptic['IL2DL'] = [0,0]
            self.postSynaptic['IL2DR'] = [0,0]
            self.postSynaptic['IL2VL'] = [0,0]
            self.postSynaptic['IL2VR'] = [0,0]
            self.postSynaptic['LUAL'] = [0,0]
            self.postSynaptic['LUAR'] = [0,0]
            self.postSynaptic['M1'] = [0,0]
            self.postSynaptic['M2L'] = [0,0]
            self.postSynaptic['M2R'] = [0,0]
            self.postSynaptic['M3L'] = [0,0]
            self.postSynaptic['M3R'] = [0,0]
            self.postSynaptic['M4'] = [0,0]
            self.postSynaptic['M5'] = [0,0]
            self.postSynaptic['MANAL'] = [0,0]
            self.postSynaptic['MCL'] = [0,0]
            self.postSynaptic['MCR'] = [0,0]
            self.postSynaptic['MDL01'] = [0,0]
            self.postSynaptic['MDL02'] = [0,0]
            self.postSynaptic['MDL03'] = [0,0]
            self.postSynaptic['MDL04'] = [0,0]
            self.postSynaptic['MDL05'] = [0,0]
            self.postSynaptic['MDL06'] = [0,0]
            self.postSynaptic['MDL07'] = [0,0]
            self.postSynaptic['MDL08'] = [0,0]
            self.postSynaptic['MDL09'] = [0,0]
            self.postSynaptic['MDL10'] = [0,0]
            self.postSynaptic['MDL11'] = [0,0]
            self.postSynaptic['MDL12'] = [0,0]
            self.postSynaptic['MDL13'] = [0,0]
            self.postSynaptic['MDL14'] = [0,0]
            self.postSynaptic['MDL15'] = [0,0]
            self.postSynaptic['MDL16'] = [0,0]
            self.postSynaptic['MDL17'] = [0,0]
            self.postSynaptic['MDL18'] = [0,0]
            self.postSynaptic['MDL19'] = [0,0]
            self.postSynaptic['MDL20'] = [0,0]
            self.postSynaptic['MDL21'] = [0,0]
            self.postSynaptic['MDL22'] = [0,0]
            self.postSynaptic['MDL23'] = [0,0]
            self.postSynaptic['MDL24'] = [0,0]
            self.postSynaptic['MDR01'] = [0,0]
            self.postSynaptic['MDR02'] = [0,0]
            self.postSynaptic['MDR03'] = [0,0]
            self.postSynaptic['MDR04'] = [0,0]
            self.postSynaptic['MDR05'] = [0,0]
            self.postSynaptic['MDR06'] = [0,0]
            self.postSynaptic['MDR07'] = [0,0]
            self.postSynaptic['MDR08'] = [0,0]
            self.postSynaptic['MDR09'] = [0,0]
            self.postSynaptic['MDR10'] = [0,0]
            self.postSynaptic['MDR11'] = [0,0]
            self.postSynaptic['MDR12'] = [0,0]
            self.postSynaptic['MDR13'] = [0,0]
            self.postSynaptic['MDR14'] = [0,0]
            self.postSynaptic['MDR15'] = [0,0]
            self.postSynaptic['MDR16'] = [0,0]
            self.postSynaptic['MDR17'] = [0,0]
            self.postSynaptic['MDR18'] = [0,0]
            self.postSynaptic['MDR19'] = [0,0]
            self.postSynaptic['MDR20'] = [0,0]
            self.postSynaptic['MDR21'] = [0,0]
            self.postSynaptic['MDR22'] = [0,0]
            self.postSynaptic['MDR23'] = [0,0]
            self.postSynaptic['MDR24'] = [0,0]
            self.postSynaptic['MI'] = [0,0]
            self.postSynaptic['MVL01'] = [0,0]
            self.postSynaptic['MVL02'] = [0,0]
            self.postSynaptic['MVL03'] = [0,0]
            self.postSynaptic['MVL04'] = [0,0]
            self.postSynaptic['MVL05'] = [0,0]
            self.postSynaptic['MVL06'] = [0,0]
            self.postSynaptic['MVL07'] = [0,0]
            self.postSynaptic['MVL08'] = [0,0]
            self.postSynaptic['MVL09'] = [0,0]
            self.postSynaptic['MVL10'] = [0,0]
            self.postSynaptic['MVL11'] = [0,0]
            self.postSynaptic['MVL12'] = [0,0]
            self.postSynaptic['MVL13'] = [0,0]
            self.postSynaptic['MVL14'] = [0,0]
            self.postSynaptic['MVL15'] = [0,0]
            self.postSynaptic['MVL16'] = [0,0]
            self.postSynaptic['MVL17'] = [0,0]
            self.postSynaptic['MVL18'] = [0,0]
            self.postSynaptic['MVL19'] = [0,0]
            self.postSynaptic['MVL20'] = [0,0]
            self.postSynaptic['MVL21'] = [0,0]
            self.postSynaptic['MVL22'] = [0,0]
            self.postSynaptic['MVL23'] = [0,0]
            self.postSynaptic['MVR01'] = [0,0]
            self.postSynaptic['MVR02'] = [0,0]
            self.postSynaptic['MVR03'] = [0,0]
            self.postSynaptic['MVR04'] = [0,0]
            self.postSynaptic['MVR05'] = [0,0]
            self.postSynaptic['MVR06'] = [0,0]
            self.postSynaptic['MVR07'] = [0,0]
            self.postSynaptic['MVR08'] = [0,0]
            self.postSynaptic['MVR09'] = [0,0]
            self.postSynaptic['MVR10'] = [0,0]
            self.postSynaptic['MVR11'] = [0,0]
            self.postSynaptic['MVR12'] = [0,0]
            self.postSynaptic['MVR13'] = [0,0]
            self.postSynaptic['MVR14'] = [0,0]
            self.postSynaptic['MVR15'] = [0,0]
            self.postSynaptic['MVR16'] = [0,0]
            self.postSynaptic['MVR17'] = [0,0]
            self.postSynaptic['MVR18'] = [0,0]
            self.postSynaptic['MVR19'] = [0,0]
            self.postSynaptic['MVR20'] = [0,0]
            self.postSynaptic['MVR21'] = [0,0]
            self.postSynaptic['MVR22'] = [0,0]
            self.postSynaptic['MVR23'] = [0,0]
            self.postSynaptic['MVR24'] = [0,0]
            self.postSynaptic['MVULVA'] = [0,0]
            self.postSynaptic['NSML'] = [0,0]
            self.postSynaptic['NSMR'] = [0,0]
            self.postSynaptic['OLLL'] = [0,0]
            self.postSynaptic['OLLR'] = [0,0]
            self.postSynaptic['OLQDL'] = [0,0]
            self.postSynaptic['OLQDR'] = [0,0]
            self.postSynaptic['OLQVL'] = [0,0]
            self.postSynaptic['OLQVR'] = [0,0]
            self.postSynaptic['PDA'] = [0,0]
            self.postSynaptic['PDB'] = [0,0]
            self.postSynaptic['PDEL'] = [0,0]
            self.postSynaptic['PDER'] = [0,0]
            self.postSynaptic['PHAL'] = [0,0]
            self.postSynaptic['PHAR'] = [0,0]
            self.postSynaptic['PHBL'] = [0,0]
            self.postSynaptic['PHBR'] = [0,0]
            self.postSynaptic['PHCL'] = [0,0]
            self.postSynaptic['PHCR'] = [0,0]
            self.postSynaptic['PLML'] = [0,0]
            self.postSynaptic['PLMR'] = [0,0]
            self.postSynaptic['PLNL'] = [0,0]
            self.postSynaptic['PLNR'] = [0,0]
            self.postSynaptic['PQR'] = [0,0]
            self.postSynaptic['PVCL'] = [0,0]
            self.postSynaptic['PVCR'] = [0,0]
            self.postSynaptic['PVDL'] = [0,0]
            self.postSynaptic['PVDR'] = [0,0]
            self.postSynaptic['PVM'] = [0,0]
            self.postSynaptic['PVNL'] = [0,0]
            self.postSynaptic['PVNR'] = [0,0]
            self.postSynaptic['PVPL'] = [0,0]
            self.postSynaptic['PVPR'] = [0,0]
            self.postSynaptic['PVQL'] = [0,0]
            self.postSynaptic['PVQR'] = [0,0]
            self.postSynaptic['PVR'] = [0,0]
            self.postSynaptic['PVT'] = [0,0]
            self.postSynaptic['PVWL'] = [0,0]
            self.postSynaptic['PVWR'] = [0,0]
            self.postSynaptic['RIAL'] = [0,0]
            self.postSynaptic['RIAR'] = [0,0]
            self.postSynaptic['RIBL'] = [0,0]
            self.postSynaptic['RIBR'] = [0,0]
            self.postSynaptic['RICL'] = [0,0]
            self.postSynaptic['RICR'] = [0,0]
            self.postSynaptic['RID'] = [0,0]
            self.postSynaptic['RIFL'] = [0,0]
            self.postSynaptic['RIFR'] = [0,0]
            self.postSynaptic['RIGL'] = [0,0]
            self.postSynaptic['RIGR'] = [0,0]
            self.postSynaptic['RIH'] = [0,0]
            self.postSynaptic['RIML'] = [0,0]
            self.postSynaptic['RIMR'] = [0,0]
            self.postSynaptic['RIPL'] = [0,0]
            self.postSynaptic['RIPR'] = [0,0]
            self.postSynaptic['RIR'] = [0,0]
            self.postSynaptic['RIS'] = [0,0]
            self.postSynaptic['RIVL'] = [0,0]
            self.postSynaptic['RIVR'] = [0,0]
            self.postSynaptic['RMDDL'] = [0,0]
            self.postSynaptic['RMDDR'] = [0,0]
            self.postSynaptic['RMDL'] = [0,0]
            self.postSynaptic['RMDR'] = [0,0]
            self.postSynaptic['RMDVL'] = [0,0]
            self.postSynaptic['RMDVR'] = [0,0]
            self.postSynaptic['RMED'] = [0,0]
            self.postSynaptic['RMEL'] = [0,0]
            self.postSynaptic['RMER'] = [0,0]
            self.postSynaptic['RMEV'] = [0,0]
            self.postSynaptic['RMFL'] = [0,0]
            self.postSynaptic['RMFR'] = [0,0]
            self.postSynaptic['RMGL'] = [0,0]
            self.postSynaptic['RMGR'] = [0,0]
            self.postSynaptic['RMHL'] = [0,0]
            self.postSynaptic['RMHR'] = [0,0]
            self.postSynaptic['SAADL'] = [0,0]
            self.postSynaptic['SAADR'] = [0,0]
            self.postSynaptic['SAAVL'] = [0,0]
            self.postSynaptic['SAAVR'] = [0,0]
            self.postSynaptic['SABD'] = [0,0]
            self.postSynaptic['SABVL'] = [0,0]
            self.postSynaptic['SABVR'] = [0,0]
            self.postSynaptic['SDQL'] = [0,0]
            self.postSynaptic['SDQR'] = [0,0]
            self.postSynaptic['SIADL'] = [0,0]
            self.postSynaptic['SIADR'] = [0,0]
            self.postSynaptic['SIAVL'] = [0,0]
            self.postSynaptic['SIAVR'] = [0,0]
            self.postSynaptic['SIBDL'] = [0,0]
            self.postSynaptic['SIBDR'] = [0,0]
            self.postSynaptic['SIBVL'] = [0,0]
            self.postSynaptic['SIBVR'] = [0,0]
            self.postSynaptic['SMBDL'] = [0,0]
            self.postSynaptic['SMBDR'] = [0,0]
            self.postSynaptic['SMBVL'] = [0,0]
            self.postSynaptic['SMBVR'] = [0,0]
            self.postSynaptic['SMDDL'] = [0,0]
            self.postSynaptic['SMDDR'] = [0,0]
            self.postSynaptic['SMDVL'] = [0,0]
            self.postSynaptic['SMDVR'] = [0,0]
            self.postSynaptic['URADL'] = [0,0]
            self.postSynaptic['URADR'] = [0,0]
            self.postSynaptic['URAVL'] = [0,0]
            self.postSynaptic['URAVR'] = [0,0]
            self.postSynaptic['URBL'] = [0,0]
            self.postSynaptic['URBR'] = [0,0]
            self.postSynaptic['URXL'] = [0,0]
            self.postSynaptic['URXR'] = [0,0]
            self.postSynaptic['URYDL'] = [0,0]
            self.postSynaptic['URYDR'] = [0,0]
            self.postSynaptic['URYVL'] = [0,0]
            self.postSynaptic['URYVR'] = [0,0]
            self.postSynaptic['VA1'] = [0,0]
            self.postSynaptic['VA10'] = [0,0]
            self.postSynaptic['VA11'] = [0,0]
            self.postSynaptic['VA12'] = [0,0]
            self.postSynaptic['VA2'] = [0,0]
            self.postSynaptic['VA3'] = [0,0]
            self.postSynaptic['VA4'] = [0,0]
            self.postSynaptic['VA5'] = [0,0]
            self.postSynaptic['VA6'] = [0,0]
            self.postSynaptic['VA7'] = [0,0]
            self.postSynaptic['VA8'] = [0,0]
            self.postSynaptic['VA9'] = [0,0]
            self.postSynaptic['VB1'] = [0,0]
            self.postSynaptic['VB10'] = [0,0]
            self.postSynaptic['VB11'] = [0,0]
            self.postSynaptic['VB2'] = [0,0]
            self.postSynaptic['VB3'] = [0,0]
            self.postSynaptic['VB4'] = [0,0]
            self.postSynaptic['VB5'] = [0,0]
            self.postSynaptic['VB6'] = [0,0]
            self.postSynaptic['VB7'] = [0,0]
            self.postSynaptic['VB8'] = [0,0]
            self.postSynaptic['VB9'] = [0,0]
            self.postSynaptic['VC1'] = [0,0]
            self.postSynaptic['VC2'] = [0,0]
            self.postSynaptic['VC3'] = [0,0]
            self.postSynaptic['VC4'] = [0,0]
            self.postSynaptic['VC5'] = [0,0]
            self.postSynaptic['VC6'] = [0,0]
            self.postSynaptic['VD1'] = [0,0]
            self.postSynaptic['VD10'] = [0,0]
            self.postSynaptic['VD11'] = [0,0]
            self.postSynaptic['VD12'] = [0,0]
            self.postSynaptic['VD13'] = [0,0]
            self.postSynaptic['VD2'] = [0,0]
            self.postSynaptic['VD3'] = [0,0]
            self.postSynaptic['VD4'] = [0,0]
            self.postSynaptic['VD5'] = [0,0]
            self.postSynaptic['VD6'] = [0,0]
            self.postSynaptic['VD7'] = [0,0]
            self.postSynaptic['VD8'] = [0,0]
            self.postSynaptic['VD9'] = [0,0]

    def motorcontrol(self, ):

            # accumulate left and right muscles and the accumulated values are
            # used to move the left and right motors of the robot

            for muscle in self.muscleList: # if this doesn't work, do muscle in self.postSynaptic
                    if muscle in self.mLeft:
                            self.accumleft += self.postSynaptic[muscle][self.nextState] # vs thisState??? 

                            #print muscle, "Before", self.postSynaptic[muscle][thisState], self.accumleft
                            self.postSynaptic[muscle][self.nextState] = 0
                            #print muscle, "After", self.postSynaptic[muscle][thisState], self.accumleft

                    elif muscle in self.mRight:
                            self.accumright += self.postSynaptic[muscle][self.nextState] # vs thisState??? 

                            #self.postSynaptic[muscle][thisState] = 0
                            self.postSynaptic[muscle][self.nextState] = 0

            # We turn the wheels according to the motor weight accumulation
            new_speed = abs(self.accumleft) + abs(self.accumright)
            if new_speed > 150:
                    new_speed = 150
            elif new_speed < 75:
                    new_speed = 75
            if self.verbosity > 1:
                    print("Left: ", self.accumleft, "Right:", self.accumright, "Speed: ", new_speed)
            
            if not self.disembodied:
                    self.set_speed(new_speed)
                    if self.accumleft == 0 and self.accumright == 0:
                            self.stop()
                    elif self.accumright <= 0 and self.accumleft < 0:
                            self.set_speed(150)
                            turnratio = float(self.accumright) / float(self.accumleft)
                            # print "Turn Ratio: ", turnratio
                            if turnratio <= 0.6:
                                    self.left_rot()
                            elif turnratio >= 2:
                                    self.right_rot()
                            self.bwd()
                    elif self.accumright <= 0 and self.accumleft >= 0:
                            self.right_rot()
                    elif self.accumright >= 0 and self.accumleft <= 0:
                            self.left_rot()
                    elif self.accumright >= 0 and self.accumleft > 0:
                            turnratio = float(self.accumright) / float(self.accumleft)
                            # print "Turn Ratio: ", turnratio
                            if turnratio <= 0.6:
                                    self.left_rot()
                            elif turnratio >= 2:
                                    self.right_rot()
                            self.fwd()
                    else:
                            self.stop()

            self.accumleft = 0
            self.accumright = 0
            #time.sleep(0.5)

    def dendriteAccumulate(self, dneuron):
            f = eval('self.' + dneuron)
            f()

    def fireNeuron(self, fneuron):
            # The threshold has been exceeded and we fire the neurite
            if fneuron != "MVULVA":
                    f = eval('self.' + fneuron)
                    f()
                    # self.postSynaptic[fneuron][thisState] = 0
                    self.postSynaptic[fneuron][self.nextState] = 0

    def runconnectome(self, ):
            """Each time a set of neuron is stimulated, this method will execute
            The weigted values are accumulated in the self.postSynaptic array
            Once the accumulation is read, we see what neurons are greater
            then the threshold and fire the neuron or muscle that has exceeded
            the threshold.
            """
            for ps in self.postSynaptic:
                    if ps[:3] not in self.muscles and abs(self.postSynaptic[ps][self.thisState]) > self.threshold:
                            self.fireNeuron(ps)
            self.motorcontrol()
            for ps in self.postSynaptic:
                    # if self.postSynaptic[ps][thisState] != 0:
                    #         print ps
                    #         print "Before Clone: ", self.postSynaptic[ps][thisState]

                    # fired neurons keep getting reset to previous weight
                    # wtf deepcopy -- So, the concern is that the deepcopy doesnt
                    # scale up to larger neural networks?? 
                    self.postSynaptic[ps][self.thisState] = copy.deepcopy(self.postSynaptic[ps][self.nextState]) 

                    # this deep copy is not in the functioning version currently.
                    # print "After Clone: ", self.postSynaptic[ps][thisState]

            self.thisState, self.nextState = self.nextState, self.thisState

    # Create the dictionary 
    def __init__(self):
        self.createpostSynaptic()
        if not self.disembodied:
                self.set_speed(120)




    tfood = 0

    def step(self, dist=18):

        # Do we need to switch states at the end of each loop? No, this is done inside the runconnectome()
        # function, called inside each loop.
        if dist>0 and dist<30:
    #             if verbosity > 0:
    #                     print("OBSTACLE (Nose Touch)", dist)
                self.dendriteAccumulate("FLPR")
                self.dendriteAccumulate("FLPL")
                self.dendriteAccumulate("ASHL")
                self.dendriteAccumulate("ASHR")
                self.dendriteAccumulate("IL1VL")
                self.dendriteAccumulate("IL1VR")
                self.dendriteAccumulate("OLQDL")
                self.dendriteAccumulate("OLQDR")
                self.dendriteAccumulate("OLQVR")
                self.dendriteAccumulate("OLQVL")
                self.runconnectome()
        else:
                if self.tfood < 2:
    #                     if verbosity > 0:
    #                             print("FOOD")
                        self.dendriteAccumulate("ADFL")
                        self.dendriteAccumulate("ADFR")
                        self.dendriteAccumulate("ASGR")
                        self.dendriteAccumulate("ASGL")
                        self.dendriteAccumulate("ASIL")
                        self.dendriteAccumulate("ASIR")
                        self.dendriteAccumulate("ASJR")
                        self.dendriteAccumulate("ASJL")
                        self.runconnectome()
                        time.sleep(0.5)
                self.tfood += 0.5
                if (self.tfood > 20):
                        self.tfood = 0
        return self.action


def main():
    """Here is where you would put in a method to stimulate the neurons
    We stimulate chemosensory neurons constantly unless nose touch
    (sonar) is stimulated and then we fire nose touch neurites.
    """
    worm = Worm()
    while True:
        print(worm.step())

if __name__ == '__main__':
    main()
