import bpy


def update_node_keymap(self, context):
    wm = context.window_manager
    kc = wm.keyconfigs.user
    for key in kc.keymaps['Node Editor'].keymap_items:
        if (
            key.idname == "wm.call_menu"
            and key.type == "RIGHTMOUSE"
        ):
            key.active = not key.active

        if (
            key.idname == "blui.right_mouse_navigation"
            and key.type == "RIGHTMOUSE"
        ):
            key.active = not key.active


class RightMouseNavigationPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    time: bpy.props.FloatProperty(
        name="Time Threshold",
        description="How long you have hold right mouse to open menu",
        default=0.3,
        min=0.1,
        max=2
    )

    distance: bpy.props.FloatProperty(
        name="Distance Threshold",
        description="How far you have to move the mouse to trigger navigation",
        default=20,
        min=1,
        max=200
    )

    reset_cursor_on_exit: bpy.props.BoolProperty(
        name="Reset Cursor on Exit",
        description="After exiting navigation, this determines if the cursor resets to where RMB was clicked (if checked) or stays in the center (if unchecked)",
        default=True
    )

    enable_for_node_editors: bpy.props.BoolProperty(
        name="Enable for Node Editors",
        description="Right Mouse will pan the view / open the Node Add/Search Menu",
        default=False,
        update=update_node_keymap,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Menu / Movement", icon='DRIVER_DISTANCE')
        row = box.row()
        row.prop(self, 'time')
        row.prop(self, 'distance')

        row = layout.row()
        box = row.box()
        box.label(text="Cursor", icon='ORIENTATION_CURSOR')
        box.prop(self, 'reset_cursor_on_exit')
        box = row.box()
        box.label(text='Node Editor', icon='NODETREE')
        box.prop(self, 'enable_for_node_editors')