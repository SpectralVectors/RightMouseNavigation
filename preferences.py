import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
)
from bpy.types import AddonPreferences

menumodes = []
panelmodes = []


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
    wm = context.window_manager
    active_keyconfig = wm.keyconfigs.active
    blender_keyconfig = wm.keyconfigs["Blender"]
    user_keyconfig = wm.keyconfigs["Blender user"]

    try:
        self.rebind_3dview_keymap(active_keyconfig, self.rmb_pan_rotate)
    except KeyError:
        self.rebind_3dview_keymap(blender_keyconfig, self.rmb_pan_rotate)
    except KeyError:
        self.rebind_3dview_keymap(user_keyconfig, self.rmb_pan_rotate)


def update_rebind_switch_nav_rotate(self, context):    
    wm = context.window_manager
    active_keyconfig = wm.keyconfigs.active
    addon_keyconfig = wm.keyconfigs.addon
    blender_keyconfig = wm.keyconfigs["Blender"]
    user_keyconfig = wm.keyconfigs["Blender user"]

    try:
        self.rebind_switch_nav_rotate(active_keyconfig, addon_keyconfig, self.rmb_rotate_switch)
    except KeyError:
        self.rebind_switch_nav_rotate(blender_keyconfig, addon_keyconfig, self.rmb_rotate_switch)
    except KeyError:
        self.rebind_switch_nav_rotate(user_keyconfig, addon_keyconfig, self.rmb_rotate_switch)


class RightMouseNavigationPreferences(AddonPreferences):
    bl_idname = __package__

    navigation_mode: EnumProperty(
        name="Navigation Mode",
        description="Choose how right-click drag navigates the viewport",
        items=[
            (
                "WALK",
                "Walk",
                "First-person walk navigation (default Blender behavior)",
            ),
            (
                "ORBIT",
                "Orbit",
                "Orbit around view center (like middle-mouse-button)",
            ),
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
        description="Switches Camera Navigation controls to Right Mouse Button. Context Menus will be set to Click when these options are toggled.",
        default=False,
        update=update_rebind_3dview_keymap,
    )

    rmb_rotate_switch: BoolProperty(
        name="Use Alt to enter Right Mouse Navigation with WASD",
        description="Switches RMB Navigation and drag Rotation controls with Alt modifier.",
        default=False,
        update=update_rebind_switch_nav_rotate,
    )

    def rebind_3dview_keymap(self, keyconfig, isActive):
        if isActive:
            for key in keyconfig.keymaps["3D View"].keymap_items:
                if key.idname == "view3d.cursor3d" and key.type == "RIGHTMOUSE":
                    key.type = "MIDDLEMOUSE"
                    key.value = "CLICK"
                    key.shift = True
                if key.idname == "view3d.rotate" and key.type == "MIDDLEMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.alt = True
                if key.idname == "view3d.move" and key.type == "MIDDLEMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                if key.idname == "view3d.zoom" and key.type == "MIDDLEMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.ctrl = True
                if key.idname == "view3d.dolly" and key.type == "MIDDLEMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                    key.ctrl = True
                if (
                    key.idname == "view3d.select_lasso"
                    and key.type == "RIGHTMOUSE"
                    and key.ctrl == True
                ):
                    key.type = "MIDDLEMOUSE"
                    key.value = "CLICK_DRAG"
                    key.ctrl = True
                if (
                    key.idname == "view3d.select_lasso"
                    and key.type == "RIGHTMOUSE"
                    and key.ctrl == True
                    and key.shift == True
                ):
                    key.type = "MIDDLEMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                    key.ctrl = True
                if key.idname == "transform.translate" and key.type == "RIGHTMOUSE":
                    key.type = "MIDDLEMOUSE"
        else:
            for key in keyconfig.keymaps["3D View"].keymap_items:
                if key.idname == "view3d.cursor3d" and key.type == "MIDDLEMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK"
                    key.shift = True
                if key.idname == "view3d.rotate" and key.type == "RIGHTMOUSE":
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.alt = False
                if key.idname == "view3d.move" and key.type == "RIGHTMOUSE":
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.shift = True
                if key.idname == "view3d.zoom" and key.type == "RIGHTMOUSE":
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.ctrl = True
                if key.idname == "view3d.dolly" and key.type == "RIGHTMOUSE":
                    key.type = "MIDDLEMOUSE"
                    key.value = "PRESS"
                    key.shift = True
                    key.ctrl = True
                if (
                    key.idname == "view3d.select_lasso"
                    and key.type == "MIDDLEMOUSE"
                    and key.ctrl == True
                ):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.ctrl = True
                if (
                    key.idname == "view3d.select_lasso"
                    and key.type == "MIDDLEMOUSE"
                    and key.ctrl == True
                    and key.shift == True
                ):
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.shift = True
                    key.ctrl = True
                if key.idname == "transform.translate" and key.type == "MIDDLEMOUSE":
                    key.type = "RIGHTMOUSE"

    def rebind_switch_nav_rotate(self, keyconfig, addon_kc, isActive):
        if isActive:
            for key in addon_kc.keymaps["3D View"].keymap_items:
                if key.idname == "rmn.right_mouse_navigation":
                    key.type = "RIGHTMOUSE"
                    key.value = "PRESS"
                    key.alt = True
            for key in keyconfig.keymaps["3D View"].keymap_items:
                if key.idname == "view3d.rotate" and key.type == "RIGHTMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.alt = False
            for i in menumodes:
                for key in keyconfig.keymaps[i].keymap_items:
                    if key.idname == "wm.call_menu" and key.type == "RIGHTMOUSE":
                        key.active = True
                        key.value = "CLICK"
            for i in panelmodes:
                for key in keyconfig.keymaps[i].keymap_items:
                    if key.idname == "wm.call_panel" and key.type == "RIGHTMOUSE" and key.active:
                        key.active = False
                        key.value = "CLICK"
        else:
            for key in addon_kc.keymaps["3D View"].keymap_items:
                if key.idname == "rmn.right_mouse_navigation":
                    key.type = "RIGHTMOUSE"
                    key.value = "PRESS"
                    key.alt = False
            for key in keyconfig.keymaps["3D View"].keymap_items:
                if key.idname == "view3d.rotate" and key.type == "RIGHTMOUSE":
                    key.type = "RIGHTMOUSE"
                    key.value = "CLICK_DRAG"
                    key.alt = True
            for i in menumodes:
                for key in keyconfig.keymaps[i].keymap_items:
                    if key.idname == "wm.call_menu" and key.type == "RIGHTMOUSE":
                        key.active = False
                        key.value = "PRESS"
            for i in panelmodes:
                for key in keyconfig.keymaps[i].keymap_items:
                    if key.idname == "wm.call_panel" and key.type == "RIGHTMOUSE":
                        key.active = True
                        key.value = "PRESS"

    def draw(self, context):
        layout = self.layout

        # Navigation Mode & Menu / Movement Boxes
        row = layout.row()
        box = row.box()
        box.label(text="Navigation Mode", icon="ORIENTATION_GIMBAL")
        box.prop(self, "navigation_mode", text="")
        box = row.box()
        box.label(text="Menu / Movement", icon="DRIVER_DISTANCE")
        box.prop(self, "time")

        # Cursor & View Boxes
        row = layout.row()
        box = row.box()
        box.label(text="Cursor", icon="ORIENTATION_CURSOR")
        box.prop(self, "reset_cursor_on_exit")
        box = row.box()
        box.label(text="View", icon="VIEW3D")
        box.prop(self, "return_to_ortho_on_exit")

        # Camera Box
        row = layout.row()
        box = row.box()
        box.label(text="Camera", icon="CAMERA_DATA")
        row = box.row()
        row.prop(self, "disable_camera_navigation")
        row.prop(self, "show_cam_lock_ui")

        # Node Editor Box
        row = layout.row()
        box = row.box()
        box.label(text="Node Editor", icon="NODETREE")
        box.prop(self, "enable_for_node_editors")

        # RMB MMB Box
        box = layout.box()

        header, panel = box.panel(idname="panzoom", default_closed=True)
        header.label(text="Pan, Zoom, Rotate", icon="VIEW3D")

        if panel:
            row = panel.row()
            row.prop(self, "rmb_pan_rotate", text="Swap MMB & RMB Navigation Controls")
            row.prop(self, "rmb_rotate_switch", text="Require Alt for Walk/Fly Navigation")

            # Split the layout at 30%
            split = panel.split(factor=0.3)
            split.active = self.rmb_pan_rotate

            # One side of split for titles
            title = split.column()
            title.alignment = "RIGHT"

            row = title.row()
            row.alignment = "LEFT"
            row.label(text="Right Mouse", icon="MOUSE_RMB")

            # RMB
            title.label(text="Navigation Mode:")
            title.label(text="Rotate 3D View:")
            title.label(text="Pan 3D View:")
            title.label(text="Zoom 3D View:")
            title.label(text="Dolly Zoom 3D View:")

            row = title.row()
            row.alignment = "LEFT"
            row.label(text="Middle Mouse", icon="MOUSE_MMB")

            # MMB
            title.label(text="Set 3D Cursor:")
            title.label(text="Transform Translate:")
            title.label(text="Lasso Selection:")
            title.label(text="Lasso Deselection:")

            # The other side of the split holds content
            content = split.column()

            row = content.row()
            row.label(text="")

            # RMB
            row = content.row(align=True)
            row.label(text="", icon="EVENT_W")
            row.label(text="", icon="EVENT_A")
            row.label(text="", icon="EVENT_S")
            row.label(text="", icon="EVENT_D")
            row.label(text="", icon="ADD")
            if self.rmb_rotate_switch:
                row.label(text="", icon="EVENT_ALT")
                row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_RMB_DRAG")
            label = row.row()
            label.active = False
            text = (
                "(WASD + Right Mouse)"
                if not self.rmb_rotate_switch
                else "(WASD + Alt + Right Mouse)"
            )
            label.label(text=text)

            row = content.row(align=True)
            if not self.rmb_rotate_switch:
                row.label(text="", icon="EVENT_ALT")
                row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_RMB_DRAG")
            label = row.row()
            label.active = False
            text = "(Alt + Right Mouse)" if not self.rmb_rotate_switch else "(Right Mouse)"
            label.label(text=text)

            row = content.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_RMB_DRAG")
            label = row.row()
            label.active = False
            label.label(text="(Shift + Right Mouse)")

            row = content.row(align=True)
            row.label(text="", icon="EVENT_CTRL")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_RMB_DRAG")
            label = row.row()
            label.active = False
            label.label(text="(Ctrl + Right Mouse)")

            row = content.row(align=True)
            row.label(text="", icon="EVENT_CTRL")
            row.label(text="", icon="ADD")
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_RMB_DRAG")
            label = row.row()
            label.active = False
            label.label(text="(Ctrl + Shift + Right Mouse)")

            row = content.row()
            row.label(text="")
            # MMB
            row = content.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_MMB")
            label = row.row()
            label.active = False
            label.label(text="(Shift + Middle Mouse)")

            row = content.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_MMB_DRAG")
            label = row.row()
            label.active = False
            label.label(text="(Shift + Middle Mouse)")

            row = content.row(align=True)
            row.label(text="", icon="EVENT_CTRL")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_MMB_DRAG")
            label = row.row()
            label.active = False
            label.label(text="(Ctrl + Middle Mouse)")

            row = content.row(align=True)
            row.label(text="", icon="EVENT_SHIFT")
            row.label(text="", icon="ADD")
            row.label(text="", icon="EVENT_CTRL")
            row.label(text="", icon="ADD")
            row.label(text="", icon="MOUSE_MMB_DRAG")
            label = row.row()
            label.active = False
            label.label(text="(Shift + Ctrl + Right Mouse)")

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

        # Navigation Keymap Box
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
