import logging
import os
from typing import Annotated, Optional

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import *
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)
import numpy as np
from vtk.util import numpy_support

from slicer import vtkMRMLModelNode, vtkMRMLTransformNode

import qt

#
# sphere
#



class sphEraser(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "SphEraser"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Jens Nirme (InfraVis)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)
        
        


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.




#
# sphereParameterNode
#

@parameterNodeWrapper
class sphEraserParameterNode:
    """
    The parameters needed by module.

    inputModel - The model to erase from
    radius - Size of eraser
    """
    inputModel: vtkMRMLModelNode
    radius: Annotated[float, WithinRange(5, 1500)] = 25
    #invertSelection: bool
    

#
# sphEraserWidget
#

class sphEraserWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """
    
    sphereCreated = False

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/sphEraser.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = sphEraserLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)
        self.ui.createSphereButton.connect('clicked(bool)', self.onCreateSphereButton)
        # self.ui.invertSelectionButton.stateChanged.connect(self.onInvertSelChange)
        

        self.ui.applyButton.enabled = False
        

        

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())


    def setParameterNode(self, inputParameterNode: Optional[sphEraserParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputModel and self._parameterNode.radius and self.sphereCreated:
            self.ui.applyButton.toolTip = "Compute output volume"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input model"
            self.ui.applyButton.enabled = False
    
    def onApplyButton(self) -> None:
        """
        Run processing when user clicks "Apply" button.
        """
        
        
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputSelector.currentNode(),
                               self.ui.radiusSliderWidget.value)
            '''
            # Compute inverted output (if needed)
            if self.ui.invertedOutputSelector.currentNode():
                # If additional output volume is selected then result with inverted threshold is written there
                self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
                                   self.ui.radiusSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)
            '''
    
    
    
    def onCreateSphereButton(self) -> None:
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.initSphere()
            
            self.ui.createSphereButton.enabled = False
            
            self.ui.applyButton.enabled = True
            
            self.ui.radiusSliderWidget.connect('valueChanged(double)', self.onRadiusChange)
            
            
            shortcut1 = qt.QShortcut(slicer.util.mainWindow())
            shortcut1.setKey(qt.QKeySequence('right'))
        
            shortcut2 = qt.QShortcut(slicer.util.mainWindow())
            shortcut2.setKey(qt.QKeySequence('left'))
            
            shortcut3 = qt.QShortcut(slicer.util.mainWindow())
            shortcut3.setKey(qt.QKeySequence('p'))
        
            shortcut1.connect('activated()', lambda: self.incrRadius())
            shortcut2.connect('activated()', lambda: self.decrRadius())
            shortcut3.connect('activated()', lambda: self.onApplyButton())
            
            self.sphereCreated = True
            
    
    def onRadiusChange(self, radius):
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            self.logic.changeRadius(radius)
            
    def incrRadius(self):
        
        radius = self.ui.radiusSliderWidget.value
            
        #if (radius > 5):
            
        radius = radius**1.025 #power
        self.ui.radiusSliderWidget.setValue(radius)
        self.logic.changeRadius(radius)
            
    def decrRadius(self):
        
        radius = self.ui.radiusSliderWidget.value
                
        radius = radius**0.975 #power
        self.ui.radiusSliderWidget.setValue(radius)
        self.logic.changeRadius(radius)
        
    def onInvertSelChange(self, checkState):
        if checkState == qt.Qt.Checked:
            print("This checkbox was checked")
            self.logic.setIncSel(True)
        elif checkState == qt.Qt.Unchecked:
            print("This checkbox was unchecked")
            self.logic.setIncSel(False)

#
# sphEraserLogic
#

class sphEraserLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    invertSelection = False

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        self.sphereModel = None
        ScriptedLoadableModuleLogic.__init__(self)
                
        

    def getParameterNode(self):
        return sphEraserParameterNode(super().getParameterNode())

    def initSphere(self):
        
        try:
            self.hand 	=  slicer.util.getNode('hand')
        except MRMLNodeNotFoundException:
            print("Hand transform not found, creating")
            hand = slicer.vtkMRMLTransformNode()
            hand.SetName('hand')
            slicer.mrmlScene.AddNode(hand)
            self.hand 	=  slicer.util.getNode('hand')
        
        
        contrlTransf = slicer.util.getNode('VirtualReality.RightController')
        self.hand.SetAndObserveTransformNodeID(contrlTransf.GetID())
            
          
        eraSphere = vtk.vtkSphereSource()
        
        eraSphere.Update()
        eraSphere.SetThetaResolution(32)
        eraSphere.SetPhiResolution(32)
        
        self.sphereModel = slicer.modules.models.logic().AddModel(eraSphere.GetOutputPort())
        self.sphereModel.GetDisplayNode().SetColor(1,0,0)
        self.sphereModel.GetDisplayNode().SetOpacity(0.25)
        self.sphereModel.SetName("eraserSphere")
        
        


        self.sphereModel.SetAndObserveTransformNodeID(self.hand.GetID())
        
        self.changeRadius(25)



    def changeRadius(self, radius):
        #print(eraSphere)

        
        if (self.sphereModel != None):
            eraSphere = self.sphereModel.GetMeshConnection().GetProducer () 
            eraSphere.SetRadius(radius)

            transformMatrix = vtk.vtkMatrix4x4()
            transformMatrix.SetElement(2,3, radius-5)
            self.hand.SetMatrixTransformToParent(transformMatrix)

    '''
    def setIncSel(self, invSel):
        invertSelection = invSel
        if invSel:
            self.sphereModel.GetDisplayNode().SetColor(0,1,0)
        else:
            self.sphereModel.GetDisplayNode().SetColor(1,0,0)
    '''
    def process(self,
                inputModel: vtkMRMLModelNode,
                radius: float):


        if not inputModel:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')
    
        loc = vtk.vtkStaticPointLocator ()
        loc.SetDataSet(inputModel.GetPolyData())
        loc.BuildLocator()
        
        result=vtk.vtkIdList()

        eraSphere = self.sphereModel.GetMeshConnection().GetProducer() 
        
        r = eraSphere.GetRadius()
        posSphere = [0.0,0.0,0.0]
        self.sphereModel.TransformPointToWorld([0.0,0.0,0.0], posSphere)
        
        pos = [0.0,0.0,0.0]
        inputModel.TransformPointFromWorld(posSphere, pos)
        
        loc.FindPointsWithinRadius(r,pos,result)
        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.1f} seconds')

        #result_array = result.Release()
        
        result_array = vtk.vtkIdTypeArray()
        #print(result_array)
        for i in range(result.GetNumberOfIds()):
            result_array.InsertNextValue(result.GetId(i))
        
        
        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.1f} seconds')
        

        remover=vtk.vtkRemovePolyData()
        remover.AddInputConnection(inputModel.GetPolyDataConnection())
        
        remover.SetPointIds(result_array)
        remover.Update()
        
        bounds = [pos[0]-r,pos[0]+r,pos[1]-r,pos[1]+r,pos[2]-r,pos[2]+r]
        print(bounds)
        
        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputConnection(remover.GetOutputPort())
        #clean.OperateOnBounds(bounds,bounds) #https://vtk.org/doc/nightly/html/classvtkCleanPolyData.html#a2adf007c37818215caa254377336cb56
        cleaner.PointMergingOff()
        cleaner.Update()
        
        inputModel.SetPolyDataConnection(cleaner.GetOutputPort())
        inputModel.Modified()
        
        #loc.Delete()
        #result.delete()
        #result_array.Delete()
        #remover.Delete()
        
        
        '''
        
    
        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)
        '''
        
        stopTime = time.time()
        print(f'Processing completed in {stopTime-startTime:.01f} seconds')


#
# sphEraserTest
#

class sphEraserTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_sphEraser1()

    def test_sphEraser1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

       
        self.delayDisplay('Test passed')
