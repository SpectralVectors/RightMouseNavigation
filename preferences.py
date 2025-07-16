import bpy
from bpy.props import (
    BoolProperty,
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


def update_node_keymap(self, context):
    wm = context.window_manager
    active_kc = wm.keyconfigs.active
    for key in active_kc.keymaps["Node Editor"].keymap_items:
        if key.idname == "wm.call_menu" and key.type == "RIGHTMOUSE":
            key.active = not key.active

    addon_kc = wm.keyconfigs.addon
    for key in addon_kc.keymaps["Node Editor"].keymap_items:
        if key.idname == "rmn.right_mouse_navigation" and key.type == "RIGHTMOUSE":
            key.active = not key.active


class RightMouseNavigationPreferences(AddonPreferences):
    bl_idname = __package__

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

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.label(text="Menu / Movement", icon="DRIVER_DISTANCE")
        box.prop(self, "time")
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
        box.prop(self, "disable_camera_navigation")
        box.prop(self, "show_cam_lock_ui")

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
        active_kc = wm.keyconfigs.active

        addon_keymaps = []

        walk_km = active_kc.keymaps["View3D Walk Modal"]

        for key in walk_km.keymap_items:
            addon_keymaps.append((walk_km, key))

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
