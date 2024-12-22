import bpy
from bpy.types import Operator


class RMN_OT_right_mouse_navigation(Operator):
    """Timer that decides whether to display a menu after Right Click"""

    bl_idname = "rmn.right_mouse_navigation"
    bl_label = "Right Mouse Navigation"
    bl_options = {"REGISTER", "UNDO"}

    _timer = None
    _count = 0
    MOUSE_RIGHTUP = 0x0010
    _finished = False
    _callMenu = False
    _ortho = False
    _back_to_ortho = False
    menu_by_mode = {
        "OBJECT": "VIEW3D_MT_object_context_menu",
        "EDIT_MESH": "VIEW3D_MT_edit_mesh_context_menu",
        "EDIT_SURFACE": "VIEW3D_MT_edit_surface",
        "EDIT_TEXT": "VIEW3D_MT_edit_font_context_menu",
        "EDIT_ARMATURE": "VIEW3D_MT_edit_armature",
        "EDIT_CURVE": "VIEW3D_MT_edit_curve_context_menu",
        "EDIT_METABALL": "VIEW3D_MT_edit_metaball_context_menu",
        "EDIT_LATTICE": "VIEW3D_MT_edit_lattice_context_menu",
        "POSE": "VIEW3D_MT_pose_context_menu",
        "PAINT_VERTEX": "VIEW3D_PT_paint_vertex_context_menu",
        "PAINT_WEIGHT": "VIEW3D_PT_paint_weight_context_menu",
        "PAINT_TEXTURE": "VIEW3D_PT_paint_texture_context_menu",
        "SCULPT": "VIEW3D_PT_sculpt_context_menu",
    }

    def modal(self, context, event):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        enable_nodes = addon_prefs.enable_for_node_editors

        space_type = context.space_data.type

        if space_type == "VIEW_3D":
            # Check if the Viewport is Perspective or Orthographic
            if bpy.context.region_data.is_perspective:
                self._ortho = False
            else:
                self._back_to_ortho = addon_prefs.return_to_ortho_on_exit

        # The _finished Boolean acts as a flag to exit the modal loop,
        # it is not made True until after the cancel function is called
        if self._finished:

            def reset_cursor():
                # Reset blender window cursor to previous position
                area = context.area
                x = area.x
                y = area.y
                x += int(area.width / 2)
                y += int(area.height / 2)
                bpy.context.window.cursor_warp(x, y)

            if self._callMenu:
                # Always reset the cursor if menu is called, as that implies a canceled navigation
                if addon_prefs.reset_cursor_on_exit and not space_type == "NODE_EDITOR":
                    reset_cursor()
                self.callMenu(context)
            else:
                # Exit of a full navigation. Only reset the cursor if the preference is enabled
                if addon_prefs.reset_cursor_on_exit:
                    reset_cursor()

            if self._back_to_ortho:
                bpy.ops.view3d.view_persportho()

            return {"CANCELLED"}

        if space_type == "VIEW_3D" or space_type == "NODE_EDITOR" and enable_nodes:
            if event.type in {"RIGHTMOUSE"}:
                if event.value in {"RELEASE"}:
                    # This brings back our mouse cursor to use with the menu
                    context.window.cursor_modal_restore()
                    # If the length of time you've been holding down
                    # Right Mouse and Mouse move distance is longer than the threshold value,
                    # then set flag to call a context menu
                    if self._count < addon_prefs.time:
                        self._callMenu = True
                    self.cancel(context)
                    # We now set the flag to true to exit the modal operator on the next loop
                    self._finished = True
                    return {"PASS_THROUGH"}

            if event.type == "TIMER":
                if self._count <= addon_prefs.time:
                    self._count += 0.1
            return {"PASS_THROUGH"}

    def callMenu(self, context):
        select_mouse = context.window_manager.keyconfigs.active.preferences.select_mouse
        space_type = context.space_data.type

        if select_mouse == "LEFT":
            if space_type == "NODE_EDITOR":
                node_tree = context.space_data.node_tree
                if node_tree:
                    if node_tree.nodes.active is not None and node_tree.nodes.active.select:
                        bpy.ops.wm.call_menu(name="NODE_MT_context_menu")
                    else:
                        bpy.ops.wm.search_single_menu("INVOKE_DEFAULT", menu_idname="NODE_MT_add")
            else:
                try:
                    bpy.ops.wm.call_menu(name=self.menu_by_mode[context.mode])
                except RuntimeError:
                    bpy.ops.wm.call_panel(name=self.menu_by_mode[context.mode])
        else:
            if space_type == "VIEW_3D":
                bpy.ops.view3d.select("INVOKE_DEFAULT")

    def invoke(self, context, event):
        # Store Blender cursor position
        self.view_x = event.mouse_x
        self.view_y = event.mouse_y
        return self.execute(context)

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        enable_nodes = addon_prefs.enable_for_node_editors

        space_type = context.space_data.type

        # Execute is the first thing called in our operator, so we start by
        # calling Blender's built-in Walk Navigation
        if space_type == "VIEW_3D":
            bpy.ops.view3d.walk("INVOKE_DEFAULT")
            # Adding the timer and starting the loop
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        elif space_type == "NODE_EDITOR" and enable_nodes:
            bpy.ops.view2d.pan("INVOKE_DEFAULT")
            wm = context.window_manager
            # Adding the timer and starting the loop
            self._timer = wm.event_timer_add(0.01, window=context.window)
            wm.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        elif space_type == "IMAGE_EDITOR":
            bpy.ops.wm.call_panel(name="VIEW3D_PT_paint_texture_context_menu")
            return {"FINISHED"}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
