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
    # [New Status Lock]: Mark whether Blender’s built-in navigation system has actually been activated
    _navigation_started = False
    
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
        disable_camera = addon_prefs.disable_camera_navigation
        navigation_mode = addon_prefs.navigation_mode

        space_type = context.space_data.type

        if space_type == "VIEW_3D":
            if bpy.context.region_data.is_perspective:
                self._ortho = False

        # 1. Exit and closing logic
        if self._finished:
            def reset_cursor():
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

            return {"CANCELLED"}

        # 2. Core: timing listener control
        if space_type == "VIEW_3D" or (space_type == "NODE_EDITOR" and enable_nodes):
            
            # case: Timer event (core delayed startup trigger)
            if event.type == "TIMER":
                if self._count <= addon_prefs.time:
                    self._count += 0.1  # Corresponding timer 0.1s step size
            
            # case: Player releases right mouse button before threshold time -> short click to call menu
            if event.type == "RIGHTMOUSE":
                if event.value == "RELEASE":
                    context.window.cursor_modal_restore()
                    if self._count < addon_prefs.time:
                        self._callMenu = True
                    self.cancel(context)
                    self._finished = True
                    
                    # if release occurs before navigation has started
                    return {"PASS_THROUGH"}
            
            # [Delayed Trigger Core]: When holding time exceeds threshold, and navigation has not been started
            if self._count >= addon_prefs.time and not self._navigation_started:
                self._navigation_started = True # Lock, to prevent repeated calls
                
                if space_type == "VIEW_3D":
                    view = context.space_data.region_3d.view_perspective
                    if not (view == "CAMERA" and disable_camera):
                        try:
                            # Only now transfer the event to Walk or Orbit!
                            if navigation_mode == "ORBIT":
                                bpy.ops.view3d.rotate("INVOKE_DEFAULT")
                            else:
                                bpy.ops.view3d.walk("INVOKE_DEFAULT")
                            print("[RMN] Long press successfully activated Walk/Orbit navigation")

                            context.window.cursor_modal_restore()
                        except RuntimeError:
                            self.report({"ERROR"}, "Cannot Navigate an Object with Constraints")
                elif space_type == "NODE_EDITOR" and enable_nodes:
                    bpy.ops.view2d.pan("INVOKE_DEFAULT")
                    
                self.cancel(context)
                # FINISH pollutes undo records
                return {"CANCELLED"}
            # Core: When the Walk/Orbit operator is activated above, we must feed subsequent mouse drag events
            # through PASS_THROUGH, otherwise the Walk mode cannot take over mouse movement.
            return {"PASS_THROUGH"}

    def callMenu(self, context):
        wm = context.window_manager
        blender_keyconfig = wm.keyconfigs["Blender"]
        select_mouse = blender_keyconfig.preferences.select_mouse
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
        self.view_x = event.mouse_x
        self.view_y = event.mouse_y
        return self.execute(context)

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        enable_nodes = addon_prefs.enable_for_node_editors
        space_type = context.space_data.type

        if space_type == "VIEW_3D":
            wm = context.window_manager
            # Start high-frequency timer (check long-press status every 0.1 seconds)
            self._timer = wm.event_timer_add(0.1, window=context.window)
            wm.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        elif space_type == "NODE_EDITOR" and enable_nodes:
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.01, window=context.window)
            wm.modal_handler_add(self)
            return {"RUNNING_MODAL"}

        elif space_type == "IMAGE_EDITOR":
            bpy.ops.wm.call_panel(name="VIEW3D_PT_paint_texture_context_menu")
            return {"FINISHED"}
            
        return {"CANCELLED"}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class RMN_OT_toggle_cam_navigation(Operator):
    """Turn Mouse Navigation of Camera On and Off"""
    bl_idname = "rmn.toggle_cam_navigation"
    bl_label = "Toggle Mouse Camera Navigation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        addon_prefs.disable_camera_navigation = not addon_prefs.disable_camera_navigation
        return {"FINISHED"}
