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

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'timepreference')
        row.prop(self, 'distancepreference')