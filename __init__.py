import bpy

from .operators import (
    RMN_OT_right_mouse_navigation,
    RMN_OT_toggle_cam_navigation,
)
from .preferences import RightMouseNavigationPreferences

addon_keymaps = []
classes = [
    RightMouseNavigationPreferences,
    RMN_OT_right_mouse_navigation,
    RMN_OT_toggle_cam_navigation,
]


def register():
    if not bpy.app.background:
        for cls in classes:
            bpy.utils.register_class(cls)

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

        active_kc = wm.keyconfigs.active

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

        # These Modes all call standard menus
        # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
        # "Font", "Pose"
        for i in menumodes:
            for key in active_kc.keymaps[i].keymap_items:
                if (
                    # key.idname == "wm.call_menu"
                    key.type == "RIGHTMOUSE"
                    and key.active
                ):
                    key.active = False

        # These Modes call panels instead of menus
        # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"
        for i in panelmodes:
            for key in active_kc.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_panel"
                    and key.type == "RIGHTMOUSE"
                    and key.active
                ):
                    key.active = False

        # Changing the Walk Modal Map
        for key in active_kc.keymaps["View3D Walk Modal"].keymap_items:
            if key.propvalue == "CANCEL" and key.type == "RIGHTMOUSE" and key.active:
                key.active = False
        for key in active_kc.keymaps["View3D Walk Modal"].keymap_items:
            if key.propvalue == "CONFIRM" and key.type == "LEFTMOUSE" and key.active:
                key.type = "RIGHTMOUSE"
                key.value = "RELEASE"


def unregister():
    if not bpy.app.background:
        for cls in classes:
            bpy.utils.unregister_class(cls)

        wm = bpy.context.window_manager
        active_kc = wm.keyconfigs.active
        addon_kc = wm.keyconfigs.addon

        menumodes = [
            "Object Mode",
            "Mesh",
            "Curve",
            "Armature",
            "Metaball",
            "Lattice",
            "Font",
            "Pose",
            "Node Editor",
        ]
        panelmodes = [
            "Vertex Paint",
            "Weight Paint",
            "Image Paint",
            "Sculpt",
        ]

        # Reactivating menus
        # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
        # "Font", "Pose"
        for i in menumodes:
            for key in active_kc.keymaps[i].keymap_items:
                if key.idname == "wm.call_menu" and key.type == "RIGHTMOUSE":
                    key.active = True

        # Reactivating panels
        # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"
        for i in panelmodes:
            for key in active_kc.keymaps[i].keymap_items:
                if key.idname == "wm.call_panel" and key.type == "RIGHTMOUSE":
                    key.active = True

        # Changing the Walk Modal Map back
        for key in active_kc.keymaps["View3D Walk Modal"].keymap_items:
            if key.propvalue == "CANCEL" and key.type == "RIGHTMOUSE":
                key.active = True
        for key in active_kc.keymaps["View3D Walk Modal"].keymap_items:
            if key.propvalue == "CONFIRM" and key.type == "RIGHTMOUSE":
                key.type = "LEFTMOUSE"
                key.value = "PRESS"

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
