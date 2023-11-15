import bpy, ctypes, math, sys

class BLUI_OT_right_mouse_navigation(bpy.types.Operator):
    """Timer that decides whether to display a menu after Right Click"""
    bl_idname = "blui.right_mouse_navigation"
    bl_label = "Right Mouse Navigation"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _count = 0
    _move_distance = 0
    MOUSE_RIGHTUP = 0x0010
    _finished = False
    _callMenu = False
    _ortho = False
    _back_to_ortho = False
    menu_by_mode = {
        'OBJECT': 'VIEW3D_MT_object_context_menu',
        'EDIT_MESH': 'VIEW3D_MT_edit_mesh_context_menu',
        'EDIT_SURFACE': 'VIEW3D_MT_edit_surface',
        'EDIT_TEXT': 'VIEW3D_MT_edit_font_context_menu',
        'EDIT_ARMATURE': 'VIEW3D_MT_edit_armature',
        'EDIT_CURVE': 'VIEW3D_MT_edit_curve_context_menu',
        'EDIT_METABALL': 'VIEW3D_MT_edit_metaball_context_menu',
        'EDIT_LATTICE': 'VIEW3D_MT_edit_lattice_context_menu',
        'POSE': 'VIEW3D_MT_pose_context_menu',
        'PAINT_VERTEX': 'VIEW3D_PT_paint_vertex_context_menu',
        'PAINT_WEIGHT': 'VIEW3D_PT_paint_weight_context_menu',
        'PAINT_TEXTURE': 'VIEW3D_PT_paint_texture_context_menu',
        'SCULPT': 'VIEW3D_PT_sculpt_context_menu'}

    def modal(self, context, event):

        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        if context.space_data.type == 'VIEW_3D':
            # Check if the Viewport is Perspective or Orthographic
            if bpy.context.region_data.is_perspective:
                self._ortho = False
            else:
                self._back_to_ortho = True

        # The _finished Boolean acts as a flag to exit the modal loop, 
        # it is not made True until after the cancel function is called
        if self._finished:

            def reset_cursor():
                # Reset blender window cursor to previous position
                context.window.cursor_warp(self.view_x, self.view_y)

            if self._callMenu:
                # Always reset the cursor if menu is called, as that implies a canceled navigation
                reset_cursor()
                self.callMenu(context)
            else:
                # Exit of a full navigation. Only reset the cursor if the preference (default False) is enabled
                if addon_prefs.reset_cursor_on_exit:
                    reset_cursor()

            if self._back_to_ortho:
                bpy.ops.view3d.view_persportho()

            return {'CANCELLED'}

        if context.space_data.type == 'VIEW_3D' or addon_prefs.enable_for_node_editors and context.space_data.type == 'NODE_EDITOR':
            # Calculate mousemove distance before it reaches threshold
            if event.type == "MOUSEMOVE" and self._move_distance < addon_prefs.distance:
                xDelta = event.mouse_x - event.mouse_prev_x
                yDelta = event.mouse_y - event.mouse_prev_y
                deltaDistance = math.sqrt(xDelta*xDelta + yDelta*yDelta)
                self._move_distance += deltaDistance

            if event.type in {'RIGHTMOUSE'}:
                if event.value in {'RELEASE'}:
                    if sys.platform == 'win32':
                        # This fakes a Right Mouse Up event using Ctypes
                        ctypes.windll.user32.mouse_event(self.MOUSE_RIGHTUP)
                    # This brings back our mouse cursor to use with the menu
                    context.window.cursor_modal_restore()
                    # If the length of time you've been holding down 
                    # Right Mouse and Mouse move distance is longer than the threshold value, 
                    # then set flag to call a context menu
                    if self._move_distance < addon_prefs.distance and self._count < addon_prefs.time:
                        self._callMenu = True
                    self.cancel(context)
                    # We now set the flag to true to exit the modal operator on the next loop through
                    self._finished = True
                    return {'PASS_THROUGH'}

            if event.type == 'TIMER':
                if self._count <= addon_prefs.time:
                    self._count += 0.01
            return {'PASS_THROUGH'}

    def callMenu(self, context):
        if context.space_data.type == 'NODE_EDITOR':
            if context.space_data.node_tree:
                    bpy.ops.wm.search_menu('INVOKE_DEFAULT')
        else:
            try:
                bpy.ops.wm.call_menu(name=self.menu_by_mode[context.mode])
            except:
                bpy.ops.wm.call_panel(name=self.menu_by_mode[context.mode])

    def invoke(self, context, event):
        # Store Blender cursor position
        self.view_x = event.mouse_x
        self.view_y = event.mouse_y
        return self.execute(context)

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        # Execute is the first thing called in our operator, so we start by
        # calling Blender's built-in Walk Navigation
        if context.space_data.type == 'VIEW_3D':
            bpy.ops.view3d.walk('INVOKE_DEFAULT')
            # Adding the timer and starting the loop
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}

        elif addon_prefs.enable_for_node_editors and context.space_data.type == 'NODE_EDITOR':
            bpy.ops.view2d.pan('INVOKE_DEFAULT')

            wm = context.window_manager
            # Adding the timer and starting the loop
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        
        elif context.space_data.type == 'IMAGE_EDITOR':
            bpy.ops.wm.call_panel(name="VIEW3D_PT_paint_texture_context_menu")
            return {'FINISHED'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)