# sphEraser
 Specialized module to erase geometry from models in Slicer 3D's VR extension

 
## Instructions
### Preparations (do once)
1. Install Steam and Steam VR, and setup VR traccking space.
2. Install latest verison of Slicer 3D (tested with 5.7.0).
3. Install [OpenVR2Key](https://github.com/BOLL7708/OpenVR2Key) (tool for mapping VR controller input to keys).
4. Overwrite default.json in the OpenVR2Key/config/ folder.
5. Install Slicer 3D's VR extension, via Slicer 3D's extension manager.
21. Add the sphEraser-main folder (or wherever you clone/download this repo) to "Additional modules paths" under Settings>Modules.
22. Restart 3D Slicer.

### Every time
1. Check boxes "Controller Transform" and "HMD transform" in the VR module setttings.
4. Make sure that the VR extension works, by checking "Connect to hardware" and "Enable rendering"
5. Make sure that a node (only one) named VirtualReality.RightController has been created and is visible.
6. Stop VR, by unchecking "Enable Rendering".
7. Load microCT volume.
8. Create segmentation from volume.
9. Create segmentation model from segmentation. (Right click > "Export visible segments ...")
10. Delete or hide Volume and segment. (For a smoother VR experience.)
11. Open the sphEraser module settings, under Modules > Examples.
12. Select the segmentation model with the "Input volume" dropdown, and press the "Initialize spherical eraser" button.
13. 13. Center segmentation model in Slicer's 3D view.
14. Enable rendering, put on VR headset and hold the right controller.
15. Navigate by pressing forward/back on the controllers trackpad to move in the direction the controller is pointing. [See the VR extension for further info](https://github.com/KitwareMedical/SlicerVirtualReality), other navigation methods should be available with two controllers.
16. Left/right on trackpad changes the size of the red sphere.
17. Place and resize the sphere to cover any geometry you wish to erase, and press the menu button above the trackpad.
