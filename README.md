# sphEraser
 Specialized module to erase geometry from models in Slicer 3D's VR extension

 
## Instructions
### Preparations (do once)
1. Install Steam and Steam VR, and setup VR traccking space.
2. Install latest verison of Slicer 3D's (tested with 5.4.0).
3. Install [OpenVR2Key](https://github.com/BOLL7708/OpenVR2Key) (tool for mapping VR controller input to keys).
4. Overwrite default.json in the OpenVR2Key/config/ folder.
5. Install Slicer 3D's VR extension, via Slicer 3D's extension manager.
21. Add the sphEraser-main folder (or wherever you clone/download this repo) to "Additional modules paths" under Settings>Modules.
22. Restart 3D Slicer.

### Every time
1. Check boxes "Controller Transform" and "HMD transform" in the VR module setttings.
4. Make sure that the VR extension works, by checking "Connect to hardware" and "Enable rendering"
5. Make sure that a Transform named VirtualReality.RightController has been created and is visible.
6. Stop VR, by unchecking "Enable Rendering".
7. Load microCT volume.
8. Create segmentation from volume.
9. Create segmentation model from segmentation. (Right click > "Export visible segments ...")
10. Delete or hide Volume and segment. (For a smoother VR experience.)



