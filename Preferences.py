import bpy

class RightMouseNavigationPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    timepreference: bpy.props.FloatProperty(
        name="Time Threshold",
        description="How long you have hold right mouse to open menu",
        default=0.3,
        min=0.1,
        max=2
    )

    distancepreference: bpy.props.FloatProperty(
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

    def draw(self, context):
        layout = self.layout

        layout.label(text="Menu Trigger Preferences")
        layout.prop(self, 'timepreference')
        layout.prop(self, 'distancepreference')

        layout.label(text="Cursor Preferences")
        layout.prop(self, 'reset_cursor_on_exit')