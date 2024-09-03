import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
)
from bpy.types import AddonPreferences


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

    enable_for_node_editors: BoolProperty(
        name="Enable for Node Editors",
        description="Right Mouse will pan the view / open the Node Add/Search Menu",
        default=False,
        update=update_node_keymap,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Menu / Movement", icon="DRIVER_DISTANCE")
        box.prop(self, "time")

        row = layout.row()
        box = row.box()
        box.label(text="Cursor", icon="ORIENTATION_CURSOR")
        box.prop(self, "reset_cursor_on_exit")
        box = row.box()
        box.label(text="Node Editor", icon="NODETREE")
        box.prop(self, "enable_for_node_editors")
