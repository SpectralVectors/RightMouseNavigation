# RightMouseNavigation
![RightMouseNavigation Logo](/RightMouseNavigationLogo.png)
Enables Unreal Engine-style Right Mouse Viewport Navigation and Blueprint-like Node workflow.

Maps Blender's Walk/Fly Navigation to the Right Mouse Button in addition to the standard context menus in the 3D Viewport.

It also (optionally) maps the Node Editor's Pan View and Add/Search Node Menu to the Right Mouse Button.

[![Install and Use](https://img.youtube.com/vi/wIEsuaaS-Hw/0.jpg)](https://www.youtube.com/watch?v=wIEsuaaS-Hw)

## How to Install
Download __RightMouseNavigation.zip__ from the __Releases__ section on the right, then install by:
- opening __Blender__
- selecting __Edit__ > __Preferences__ > __Addons__ > __Install__ 
- select __RightMouseNavigation.zip__
- click __Install Addon__

## How to Use
### 3D Viewport
- Right Mouse Hold + WASD to Navigate 3D Viewport
- Right Mouse Click to open Context Menus
- Mouse Wheel to adjust Viewport Move Speed (while Right Mouse is held)

### Node Editor (when enabled)
- Right Mouse Hold + Drag to Pan the Node Editor
- Right Mouse Click to open Add/Search Menu

### Preferences
You can adjust the threshold for when you navigate/open menus by adjusting the time the mouse button is held, or distance the cursor travels in __Edit__ > __Preferences__ > __Addons__ > __View 3D: Right Mouse Navigation__ by clicking the dropdown arrow and tweaking the values there.

Additionally, in the settings, you can change the cursor resetting behavior. By default, the cursor will snap back to the location where you initally clicked Right Mouse Button, after navigation exits. If you would rather the cursor stay in the center (where the navigation crosshair is) after navigation, you can disable the setting. 

You can enable/disable Node Editor mode in the Preferences.

## Acknowledgements and Thanks

Big thanks to __Biaru__ and __NathanC__ for their contributions to the code!

## Code Walkthrough
(old)
[![Code Walkthrough](https://img.youtube.com/vi/pSrqSz2PcY8/0.jpg)](https://www.youtube.com/watch?v=pSrqSz2PcY8)
