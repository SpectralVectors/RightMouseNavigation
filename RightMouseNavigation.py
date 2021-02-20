import bpy, ctypes, math

bl_info = {
    'name': 'Right Mouse Navigation',
    'category': 'View 3D',
    'author': 'Spectral Vectors',
    'version': (0, 1, 0),
    'blender': (2, 90, 0),
    'location': '3D Viewport',
    "description": "Enables Right Mouse Viewport Navigation"
    }

class RightMouseNavigationPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

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

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class BLUI_OT_right_mouse_navigation(bpy.types.Operator):
    """Timer that decides whether to display a menu after Right Click"""
    bl_idname = "blui.right_mouse_navigation"
    bl_label = "Right Mouse Navigation"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _count = 0
    _move_distance = 0
    MOUSE_RIGHTUP = 0x0010
    MOUSE_MOVE = 0x0001
    _finished = False
    _callMenu = False

    def modal(self, context, event):
        
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        # The _finished Boolean acts as a flag to exit the modal loop, 
        # it is not made True until after the cancel function is called
        if self._finished == True:
            # Reset blender window cursor to previous position
            context.window.cursor_warp(self.view_x, self.view_y)
            # Reset Windows OS cursor to previous position
            ctypes.windll.user32.SetCursorPos(self.mouse_x, self.mouse_y)
            if self._callMenu == True:
                self.callMenu(context)
            return {'CANCELLED'}
            
        if context.space_data.type == 'VIEW_3D':
            # Calculate mousemove distance before it reaches threshold
            if event.type == "MOUSEMOVE" and self._move_distance < addon_prefs.distancepreference:
                xDelta = event.mouse_x - event.mouse_prev_x
                yDelta = event.mouse_y - event.mouse_prev_y
                deltaDistance = math.sqrt(xDelta*xDelta + yDelta*yDelta)
                self._move_distance += deltaDistance

            if event.type in {'RIGHTMOUSE'}:
                if event.value in {'RELEASE'}:
                    # This fakes a Right Mouse Up event using Ctypes
                    ctypes.windll.user32.mouse_event(self.MOUSE_RIGHTUP)
                    # This brings back our mouse cursor to use with the menu
                    context.window.cursor_modal_restore()
                    # If the length of time you've been holding down 
                    # Right Mouse and Mouse move distance is longer than the threshold value, 
                    # then set flag to call a context menu
                    if self._move_distance < addon_prefs.distancepreference and self._count < addon_prefs.timepreference:
                        # context.window.cursor_warp(self.view_x, self.view_y)
                        self._callMenu = True
                    self.cancel(context)
                    # We now set the flag to true to exit the modal operator on the next loop through
                    self._finished = True
                    return {'PASS_THROUGH'}

            if event.type == 'TIMER':
                if self._count <= addon_prefs.timepreference:
                    self._count += 0.01
            return {'PASS_THROUGH'}

    def callMenu(self, context):
        # try to call a context menu, and if that fails, call a context panel.
        # Most of Blender's context menus can be called with the code in the 
        # 'try: except:' section, but there are a few modes that don't follow 
        # the same conventions, these are accounted for here
        if context.mode == 'EDIT_ARMATURE':
            bpy.ops.wm.call_menu(
                name="VIEW3D_MT_" + context.mode.lower()[5:].strip() + "_context_menu"
                )
            return{'PASS_THROUGH'}
        if context.mode == 'EDIT_SURFACE':
            bpy.ops.wm.call_menu(
                name="VIEW3D_MT_" + context.mode.lower()
                )
            return{'PASS_THROUGH'}
        if context.mode == 'EDIT_TEXT':
            bpy.ops.wm.call_menu(
                name="VIEW3D_MT_edit_font_context_menu"
                )
            return{'PASS_THROUGH'}
        else:
            try:
                bpy.ops.wm.call_menu(
                    name="VIEW3D_MT_" + context.mode.lower() + "_context_menu"
                    )
            except:
                bpy.ops.wm.call_panel(
                    name="VIEW3D_PT_" + context.mode.lower() + "_context_menu"
                    )

    def invoke(self, context, event):
        # Store Windows OS cursor position
        cursor = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
        self.mouse_x = cursor.x
        self.mouse_y = cursor.y
        # Store Blender cursor position
        self.view_x = event.mouse_x
        self.view_y = event.mouse_y
        return self.execute(context)

    def execute(self, context):
        # Execute is the first thing called in our operator, so we start by
        # calling Blender's built-in Walk Navigation
        if context.space_data.type == 'VIEW_3D':
            bpy.ops.view3d.walk('INVOKE_DEFAULT')
            wm = context.window_manager
            # Adding the timer and starting the loop
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        elif context.space_data.type == 'IMAGE_EDITOR':
            bpy.ops.wm.call_panel(
                name="VIEW3D_PT_" + context.mode.lower() + "_context_menu"
                )
            return {'FINISHED'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

addon_keymaps = []

def register():

    register_keymaps()
    bpy.utils.register_class(RightMouseNavigationPreferences)
    bpy.utils.register_class(BLUI_OT_right_mouse_navigation)
    

def register_keymaps():
    keyconfig = bpy.context.window_manager.keyconfigs
    areas = 'Window', 'Text', 'Object Mode', '3D View'

    if not all(i in keyconfig.active.keymaps for i in areas):
        bpy.app.timers.register(register_keymaps, first_interval=0.1)

    else:
        
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        
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
            for key in wm.keyconfigs.user.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_menu"
                    and key.type == "RIGHTMOUSE"
                    and key.active
                ):
                    key.active = False

        # These Modes call panels instead of menus
        # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"
        for i in panelmodes:
            for key in wm.keyconfigs.user.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_panel"
                    and key.type == "RIGHTMOUSE"
                    and key.active
                ):
                    key.active = False

        # Changing the Walk Modal Map        
        for key in wm.keyconfigs.user.keymaps["View3D Walk Modal"].keymap_items:
            if (
                key.propvalue == "CANCEL"
                and key.type == "RIGHTMOUSE"
                and key.active
            ):
                key.active = False
        for key in wm.keyconfigs.user.keymaps["View3D Walk Modal"].keymap_items:
            if (
                key.propvalue == "CONFIRM"
                and key.type == "LEFTMOUSE"
                and key.active
            ):
                key.type = "RIGHTMOUSE"
                key.value = "RELEASE"
        pass


def unregister():
    
    bpy.utils.unregister_class(BLUI_OT_right_mouse_navigation)
    bpy.utils.unregister_class(RightMouseNavigationPreferences)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
            wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    menumodes = ["Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice", "Font", "Pose"]
    panelmodes = ["Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"]
    
    # Reactivating menus
    # "Object Mode", "Mesh", "Curve", "Armature", "Metaball", "Lattice",
    # "Font", "Pose"
    for i in menumodes:
            for key in wm.keyconfigs.user.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_menu"
                    and key.type == "RIGHTMOUSE"
                ):
                    key.active = True

    # Reactivating panels
    # "Vertex Paint", "Weight Paint", "Image Paint", "Sculpt"    
    for i in panelmodes:
            for key in wm.keyconfigs.user.keymaps[i].keymap_items:
                if (
                    key.idname == "wm.call_panel"
                    and key.type == "RIGHTMOUSE"
                ):
                    key.active = True

    # Changing the Walk Modal Map back     
    for key in wm.keyconfigs.user.keymaps["View3D Walk Modal"].keymap_items:
        if (
            key.propvalue == "CANCEL"
            and key.type == "RIGHTMOUSE"
        ):
            key.active = True
    for key in wm.keyconfigs.user.keymaps["View3D Walk Modal"].keymap_items:
        if (
            key.propvalue == "CONFIRM"
            and key.type == "RIGHTMOUSE"
        ):
            key.type = "LEFTMOUSE"
            key.value = "PRESS"

if __name__ == "__main__":
    register()