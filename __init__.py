bl_info = {
    'name': 'Right Mouse Navigation',
    'category': 'View 3D',
    'author': 'Spectral Vectors',
    'version': (0, 1, 8),
    'blender': (2, 90, 0),
    'location': '3D Viewport',
    "description": "Enables Right Mouse Viewport Navigation"
    }

import bpy

from .RightMouseNavigation import BLUI_OT_right_mouse_navigation
from .Preferences import RightMouseNavigationPreferences        


addon_keymaps = []


def register():
    if not bpy.app.background:
        bpy.utils.register_class(RightMouseNavigationPreferences)
        bpy.utils.register_class(BLUI_OT_right_mouse_navigation)

        register_keymaps()    

def register_keymaps():
    keyconfig = bpy.context.window_manager.keyconfigs
    areas = 'Window', 'Text', 'Object Mode', '3D View'

    if not all(i in keyconfig.active.keymaps for i in areas):
        bpy.app.timers.register(register_keymaps, first_interval=0.1)

    else:
        
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        
        km = kc.keymaps.new(
            name="3D View",
            space_type='VIEW_3D',
            region_type='WINDOW'
            )
        kmi = km.keymap_items.new(
            "blui.right_mouse_navigation",
            'RIGHTMOUSE',
            'PRESS'
            )                          
        kmi.active = True
        addon_keymaps.append((km, kmi))

        menumodes = ["Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice", "Font", "Pose"]
        panelmodes = ["Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"]
        
        # These Modes all call standard menus
        # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
        # "Font", "Pose"
        for i in menumodes:
            for key in kc.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_menu"
                    and key.type == "RIGHTMOUSE"
                    and key.active
                ):
                    key.active = False

        # These Modes call panels instead of menus
        # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"
        for i in panelmodes:
            for key in kc.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_panel"
                    and key.type == "RIGHTMOUSE"
                    and key.active
                ):
                    key.active = False

        # Changing the Walk Modal Map        
        for key in kc.keymaps["View3D Walk Modal"].keymap_items:
            if (
                key.propvalue == "CANCEL"
                and key.type == "RIGHTMOUSE"
                and key.active
            ):
                key.active = False
        for key in kc.keymaps["View3D Walk Modal"].keymap_items:
            if (
                key.propvalue == "CONFIRM"
                and key.type == "LEFTMOUSE"
                and key.active
            ):
                key.type = "RIGHTMOUSE"
                key.value = "RELEASE"
        pass


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_class(BLUI_OT_right_mouse_navigation)
        bpy.utils.unregister_class(RightMouseNavigationPreferences)

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        addon_keymaps.clear()

        menumodes = ["Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice", "Font", "Pose"]
        panelmodes = ["Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"]
        
        # Reactivating menus
        # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
        # "Font", "Pose"
        for i in menumodes:
            for key in kc.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_menu"
                    and key.type == "RIGHTMOUSE"
                ):
                    key.active = True

        # Reactivating panels
        # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"    
        for i in panelmodes:
            for key in kc.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_panel"
                    and key.type == "RIGHTMOUSE"
                ):
                    key.active = True

        # Changing the Walk Modal Map back     
        for key in kc.keymaps["View3D Walk Modal"].keymap_items:
            if (
                key.propvalue == "CANCEL"
                and key.type == "RIGHTMOUSE"
            ):
                key.active = True
        for key in kc.keymaps["View3D Walk Modal"].keymap_items:
            if (
                key.propvalue == "CONFIRM"
                and key.type == "RIGHTMOUSE"
            ):
                key.type = "LEFTMOUSE"
                key.value = "PRESS"

if __name__ == "__package__":
    register()