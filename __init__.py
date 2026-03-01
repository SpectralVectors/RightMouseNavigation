import bpy

from .operators import (
    RMN_OT_right_mouse_navigation,
    RMN_OT_toggle_cam_navigation,
)
from .preferences import RightMouseNavigationPreferences
from bpy.app.handlers import persistent

addon_keymaps = []
menumodes = [
    "Object Mode",
    "Mesh",
    "Curve",
    "Armature",
    "Metaball",
    "Lattice",
    "Font",
    "Pose",
]
panelmodes = [
    "Vertex Paint",
    "Weight Paint",
    "Image Paint",
    "Sculpt",
]
classes = [
    RightMouseNavigationPreferences,
    RMN_OT_right_mouse_navigation,
    RMN_OT_toggle_cam_navigation,
]


def register_keymaps(menumodes, panelmodes, keyconfig):    
    # These Modes all call standard menus
    # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
    # "Font", "Pose"
    for i in menumodes:
        for key in keyconfig.keymaps[i].keymap_items:
            if (
                # key.idname == "wm.call_menu"
                key.type == "RIGHTMOUSE"
                and key.active
            ):
                key.active = False

    # These Modes call panels instead of menus
    # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"
    for i in panelmodes:
        for key in keyconfig.keymaps[i].keymap_items:
            if key.idname == "wm.call_panel" and key.type == "RIGHTMOUSE" and key.active:
                key.active = False

    # Changing the Walk Modal Map
    for key in keyconfig.keymaps["View3D Walk Modal"].keymap_items:
        if key.propvalue == "CANCEL" and key.type == "RIGHTMOUSE" and key.active:
            key.active = False
    for key in keyconfig.keymaps["View3D Walk Modal"].keymap_items:
        if key.propvalue == "CONFIRM" and key.type == "LEFTMOUSE" and key.active:
            key.type = "RIGHTMOUSE"
            key.value = "RELEASE"


def unregister_keymaps(menumodes, panelmodes, keyconfig):    
    # Reactivating menus
    # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
    # "Font", "Pose"
    for i in menumodes:
        for key in keyconfig.keymaps[i].keymap_items:
            if key.idname == "wm.call_menu" and key.type == "RIGHTMOUSE":
                key.active = True
                key.value = "PRESS"

    # Reactivating panels
    # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"
    for i in panelmodes:
        for key in keyconfig.keymaps[i].keymap_items:
            if key.idname == "wm.call_panel" and key.type == "RIGHTMOUSE":
                key.active = True
                key.value = "PRESS"

    # Changing the Walk Modal Map back
    for key in keyconfig.keymaps["View3D Walk Modal"].keymap_items:
        if key.propvalue == "CANCEL" and key.type == "RIGHTMOUSE":
            key.active = True
    for key in keyconfig.keymaps["View3D Walk Modal"].keymap_items:
        if key.propvalue == "CONFIRM" and key.type == "RIGHTMOUSE":
            key.type = "LEFTMOUSE"
            key.value = "PRESS"


def rebind_rmb(scene):
    # Preferences can only be checked after register
    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    addon_prefs.menumodes = menumodes
    addon_prefs.panelmodes = panelmodes
    addon_prefs.rebind_3dview_keymap(bpy.context, addon_prefs.rmb_pan_rotate)
    addon_prefs.rebind_switch_nav_rotate(bpy.context, addon_prefs.rmb_rotate_switch)
        
        
def register():
    bpy.app.handlers.load_post.append(rebind_rmb)
    
    for cls in classes:
        bpy.utils.register_class(cls)
            
    if not bpy.app.background:
        wm = bpy.context.window_manager
        addon_kc = wm.keyconfigs.addon

        km = addon_kc.keymaps.new(
            name="3D View",
            space_type="VIEW_3D",
        )
        kmi = km.keymap_items.new(
            "rmn.right_mouse_navigation",
            "RIGHTMOUSE",
            "PRESS",
        )
        kmi.active = True

        km2 = addon_kc.keymaps.new(
            name="Node Editor",
            space_type="NODE_EDITOR",
        )
        kmi2 = km2.keymap_items.new(
            "rmn.right_mouse_navigation",
            "RIGHTMOUSE",
            "PRESS",
        )
        kmi2.active = False

        addon_keymaps.append((km, kmi))
        addon_keymaps.append((km2, kmi2))

        active_keyconfig = wm.keyconfigs.active
        blender_keyconfig = wm.keyconfigs["Blender"]
        user_keyconfig = wm.keyconfigs["Blender user"]

        try:
            register_keymaps(
                menumodes=menumodes,
                panelmodes=panelmodes,
                keyconfig=active_keyconfig,
            )
        except:
            register_keymaps(
                menumodes=menumodes,
                panelmodes=panelmodes,
                keyconfig=blender_keyconfig,
            )
        finally:
            register_keymaps(
                menumodes=menumodes,
                panelmodes=panelmodes,
                keyconfig=user_keyconfig,
            )


def unregister():
    bpy.app.handlers.load_post.remove(rebind_rmb)

    addon_prefs = bpy.context.preferences.addons[__package__].preferences
    addon_prefs.rebind_switch_nav_rotate(bpy.context, False)
    addon_prefs.rebind_3dview_keymap(bpy.context, False)
        
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    if not bpy.app.background:

        wm = bpy.context.window_manager

        active_keyconfig = wm.keyconfigs.active
        blender_keyconfig = wm.keyconfigs["Blender"]
        user_keyconfig = wm.keyconfigs["Blender user"]

        try:
            unregister_keymaps(
                menumodes=menumodes,
                panelmodes=panelmodes,
                keyconfig=active_keyconfig,
            )
        except:
            unregister_keymaps(
                menumodes=menumodes,
                panelmodes=panelmodes,
                keyconfig=blender_keyconfig,
            )
        finally:
            unregister_keymaps(
                menumodes=menumodes,
                panelmodes=panelmodes,
                keyconfig=user_keyconfig,
            )
        
        addon_kc = wm.keyconfigs.addon
        # Remove only the keymap items that this addon registered
        for km, kmi_orig in addon_keymaps:
            try:
                km.keymap_items.remove(kmi_orig)
            except Exception as e:
                print(
                    f"[Right Mouse Navigation] Could not remove keymap item {getattr(kmi_orig, 'idname', 'unknown')} from {km.name}: {e}"
                )
        addon_keymaps.clear()
        
        
if __name__ == "__main__":
    register()
