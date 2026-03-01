import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from bpy.types import AddonPreferences


def draw_cam_lock(self, context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    cam_nav = addon_prefs.disable_camera_navigation

    layout = self.layout

    row = layout.row(align=True)
    row.alert = cam_nav
    col = row.column()
    col.scale_x = 1.3
    icon = "VIEW_UNLOCKED" if cam_nav else "VIEW_LOCKED"
    row.operator(text="", operator="rmn.toggle_cam_navigation", icon=icon)

    row = row.row(align=True)
    row.label(text="", icon="CAMERA_DATA")
    row.label(text="", icon="MOUSE_MOVE")


def cam_lock_update(self, context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.show_cam_lock_ui:
        bpy.types.VIEW3D_HT_tool_header.prepend(draw_cam_lock)
    else:
        bpy.types.VIEW3D_HT_tool_header.remove(draw_cam_lock)


def node_keymap(keyconfig):
    for key in keyconfig.keymaps["Node Editor"].keymap_items:
        if key.idname == "wm.call_menu" and key.type == "RIGHTMOUSE":
            key.active = not key.active


def update_node_keymap(self, context):
    wm = context.window_manager
    active_keyconfig = wm.keyconfigs.active
    blender_keyconfig = wm.keyconfigs["Blender"]
    user_keyconfig = wm.keyconfigs["Blender user"]

    try:
        node_keymap(active_keyconfig)
    except:
        node_keymap(blender_keyconfig)
    finally:
        node_keymap(user_keyconfig)

    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    # addon_kc = wm.keyconfigs.addon

    for key in user_keyconfig.keymaps["Node Editor"].keymap_items:
        if key.idname == "rmn.right_mouse_navigation" and key.type == "RIGHTMOUSE":
            key.active = addon_prefs.enable_for_node_editors


def update_rebind_3dview_keymap(self, context):
    self.rebind_3dview_keymap(context, self.rmb_pan_rotate)


def update_rebind_switch_nav_rotate(self, context):
    self.rebind_switch_nav_rotate(context, self.rmb_rotate_switch)

    
class RightMouseNavigationPreferences(AddonPreferences):
    bl_idname = __package__

    navigation_mode: EnumProperty(
        name="Navigation Mode",
        description="Choose how right-click drag navigates the viewport",
        items=[
            ("WALK", "Walk", "First-person walk navigation (default Blender behavior)"),
            ("ORBIT", "Orbit", "Orbit around view center (like middle-mouse-button)"),
        ],
        default="WALK",
    )

    time: FloatProperty(
        name="Time Threshold",
        description="How long you have hold right mouse to open menu",
        default=1.0,
        min=0.1,
        max=10,
    )

    reset_cursor_on_exit: BoolProperty(
        name="Reset Cursor on Exit",
        description="After exiting navigation, this determines if the cursor stays "
        "where RMB was clicked (if unchecked) or resets to the center (if checked)",
        default=False,
    )

    return_to_ortho_on_exit: BoolProperty(
        name="Return to Orthographic on Exit",
        description="After exiting navigation, this determines if the Viewport "
        "returns to Orthographic view (if checked) or remains in Perspective view (if unchecked)",
        default=True,
    )

    enable_for_node_editors: BoolProperty(
        name="Enable for Node Editors",
        description="Right Mouse will pan the view / open the Node Add/Search Menu",
        default=False,
        update=update_node_keymap,
    )

    disable_camera_navigation: BoolProperty(
        name="Disable Navigation for Camera View",
        description="Enable if you only want to navigate your scene, and not affect Camera Transform",
        default=False,
    )

    show_cam_lock_ui: BoolProperty(
        name="Show Camera Navigation Lock button",
        description="Displays the Camera Navigation Lock button in the 3D Viewport",
        default=False,
        update=cam_lock_update,
    )
    
    rmb_pan_rotate: BoolProperty(
        name="Switch MMB and RMB Drag Camera Navigation",
        description="Switches Camera Navigation controls to Right Mouse Button.",
        default=False,
        update=update_rebind_3dview_keymap,
    )

    rmb_rotate_switch: BoolProperty(
        name="Use Alt to enter Right Mouse Navigation with WASD",
        description="Switches RMB Navigation and drag Rotation controls with Alt modifier.",
        default=False,
        update=update_rebind_switch_nav_rotate,
    )
    
    
    def rebind_3dview_keymap(self, context, isActive):
        wm = context.window_manager
        active_kc = wm.keyconfigs.active
        addon_kc = wm.keyconfigs.addon
        
        if (isActive):
            for key in active_kc.keymaps["3D View"].keymap_items:
                if (key.idname == "view3d.cursor3d" and key.type == "RIGHTMOUSE"):
                    key.type = "MIDDLEMOUSE"
                    key.value = "CLICK"
                    key.shift = True
                if (key.idname == "view3d.rotate" and key.type == "MIDDLEMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.alt = True
                if (key.idname == "view3d.move" and key.type == "MIDDLEMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                if (key.idname == "view3d.zoom" and key.type == "MIDDLEMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.ctrl = True
                if (key.idname == "view3d.dolly" and key.type == "MIDDLEMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                    key.ctrl = True
                if (key.idname == "view3d.select_lasso" and key.type == "RIGHTMOUSE" and key.ctrl == True):
                    key.type = "MIDDLEMOUSE"
                    key.value = "CLICK_DRAG"
                    key.ctrl = True
                if (key.idname == "view3d.select_lasso" and key.type == "RIGHTMOUSE" and key.ctrl == True and key.shift == True):
                    key.type = "MIDDLEMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                    key.ctrl = True
                if (key.idname == "transform.translate" and key.type == "RIGHTMOUSE"):
                    key.type = "MIDDLEMOUSE"
        else:
            for key in active_kc.keymaps["3D View"].keymap_items:
                if (key.idname == "view3d.cursor3d" and key.type == "MIDDLEMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK"
                    key.shift = True
                if (key.idname == "view3d.rotate" and key.type == "RIGHTMOUSE"):
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.alt = False
                if (key.idname == "view3d.move" and key.type == "RIGHTMOUSE"):
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.shift = True
                if (key.idname == "view3d.zoom" and key.type == "RIGHTMOUSE"):
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.ctrl = True
                if (key.idname == "view3d.dolly" and key.type == "RIGHTMOUSE"):
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.shift = True
                    key.ctrl = True
                if (key.idname == "view3d.select_lasso" and key.type == "MIDDLEMOUSE" and key.ctrl == True):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.ctrl = True
                if (key.idname == "view3d.select_lasso" and key.type == "MIDDLEMOUSE" and key.ctrl == True and key.shift == True):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                    key.ctrl = True
                if (key.idname == "transform.translate" and key.type == "MIDDLEMOUSE"):
                    key.type = "RIGHTMOUSE"


    def rebind_switch_nav_rotate(self, context, isActive):
        wm = context.window_manager
        active_kc = wm.keyconfigs.active
        addon_kc = wm.keyconfigs.addon
        
        if (isActive):
            for key in addon_kc.keymaps["3D View"].keymap_items:
                if (key.idname == "rmn.right_mouse_navigation"):
                    key.type = "RIGHTMOUSE"
                    key.value = "PRESS"
                    key.alt = True
            for key in active_kc.keymaps["3D View"].keymap_items:
                if (key.idname == "view3d.rotate" and key.type == "RIGHTMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.alt = False

        else:
            for key in addon_kc.keymaps["3D View"].keymap_items:
                if (key.idname == "rmn.right_mouse_navigation"):
                    key.type = "RIGHTMOUSE"
                    key.value = "PRESS"
                    key.alt = False
            for key in active_kc.keymaps["3D View"].keymap_items:
                if (key.idname == "view3d.rotate" and key.type == "RIGHTMOUSE"):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.alt = True
        
        
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.label(text="Navigation", icon="ORIENTATION_GIMBAL")
        box.prop(self, "navigation_mode", text="Mode")
        box = row.box()
        box.label(text="Menu / Movement", icon="DRIVER_DISTANCE")
        box.prop(self, "time")

        row = layout.row()
        box = row.box()
        box.label(text="Node Editor", icon="NODETREE")
        box.prop(self, "enable_for_node_editors")

        row = layout.row()
        box = row.box()
        box.label(text="Cursor", icon="ORIENTATION_CURSOR")
        box.prop(self, "reset_cursor_on_exit")
        box = row.box()
        box.label(text="View", icon="VIEW3D")
        box.prop(self, "return_to_ortho_on_exit")

        row = layout.row()
        box = row.box()
        box.label(text="Camera", icon="CAMERA_DATA")
        row = box.row()
        row.prop(self, "disable_camera_navigation")
        row.prop(self, "show_cam_lock_ui")

        row = layout.row()
        box = row.box()
        box.label(text="Right Mouse Button Pan, Zoom, and Rotate", icon="VIEW3D")
        box.label(text="RMB Menus will be set to Click when these options are toggled.")
        box.prop(self, "rmb_pan_rotate")
        if self.rmb_pan_rotate:
            box.label(text="Hold RMB then WASD for Navigation Mode")
            box.label(text="Shift + Drag RMB to Pan 3D View")
            box.label(text="Ctrl + Drag RMB to Zoom 3D View")
            box.label(text="Ctrl + Shift + Drag RMB to Dolly Zoom 3D View")
            box.label(text="Alt + Drag RMB to Rotate 3D View")
            box.label(text="Other controls swapped")
            box.label(text="Shift + Click MMB to Set 3D Cursor")
            box.label(text="Shift + Drag MMB to Transform Translate")
            box.label(text="Ctrl + Drag MMB to Lasso Selection")
            box.label(text="Shift + Ctrl + Drag MMB to Lasso Deselection")
        box.prop(self, "rmb_rotate_switch")
        if self.rmb_rotate_switch:
            box.label(text="Drag + RMB will now Rotate 3D View")
            box.label(text="Alt + RMB then WASD for Navigation Mode")
                                
        # Keymap Customization
        import rna_keymap_ui

        nav_names = [
            "FORWARD",
            "FORWARD_STOP",
            "BACKWARD",
            "BACKWARD_STOP",
            "LEFT",
            "LEFT_STOP",
            "RIGHT",
            "RIGHT_STOP",
            "UP",
            "UP_STOP",
            "DOWN",
            "DOWN_STOP",
            "LOCAL_UP",
            "LOCAL_UP_STOP",
            "LOCAL_DOWN",
            "LOCAL_DOWN_STOP",
        ]

        wm = bpy.context.window_manager
        active_keyconfig = wm.keyconfigs.active
        blender_keyconfig = wm.keyconfigs["Blender"]
        user_keyconfig = wm.keyconfigs["Blender user"]

        addon_keymaps = []

        def walk_keymaps(keyconfig):
            walk_km = keyconfig.keymaps["View3D Walk Modal"]

            for key in walk_km.keymap_items:
                addon_keymaps.append((walk_km, key))

        try:
            walk_keymaps(active_keyconfig)
        except:
            walk_keymaps(blender_keyconfig)
        finally:
            walk_keymaps(user_keyconfig)

        header, panel = layout.panel(idname="keymap", default_closed=True)
        header.label(text="Navigation Keymap")

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        old_km_name = ""
        get_kmi_l = []
        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname:
                    if kmi_add.name == kmi_con.name and kmi_con.propvalue in nav_names:
                        get_kmi_l.append((km, kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        if panel:
            col = panel.column(align=True)
            for km, kmi in get_kmi_l:
                if not km.name == old_km_name:
                    col.label(text=str(km.name), icon="DOT")
                col.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                col.separator()
                old_km_name = km.name
