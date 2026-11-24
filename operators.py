import bpy
from bpy.types import Operator


class RMN_OT_right_mouse_navigation(Operator):
    """Open a menu on right-click, or navigate on right-click drag"""

    bl_idname = "rmn.right_mouse_navigation"
    bl_label = "Right Mouse Navigation"
    bl_options = {"REGISTER", "UNDO"}

    _timer = None
    _finished = False
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
        addon_prefs = context.preferences.addons[__package__].preferences

        # Finish after the native navigation operator has handled the release.
        if self._finished:
            self.cancel(context)
            if addon_prefs.reset_cursor_on_exit:
                area = context.area
                context.window.cursor_warp(
                    area.x + area.width // 2, area.y + area.height // 2
                )

            if self._back_to_ortho and context.region_data.is_perspective:
                bpy.ops.view3d.view_persportho()

            return {"FINISHED", "PASS_THROUGH"}

        if event.type == "RIGHTMOUSE" and event.value == "RELEASE":
            self._finished = True
        elif event.type == "ESC":
            # Node panning exits on Escape release; 3D navigation exits on press.
            escape_value = (
                "RELEASE" if context.space_data.type == "NODE_EDITOR" else "PRESS"
            )
            if event.value == escape_value:
                self._finished = True

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
        if event.value == "CLICK":
            self.callMenu(context)
            return {"FINISHED"}
        if event.value == "CLICK_DRAG":
            return self.execute(context)
        return {"CANCELLED"}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        enable_nodes = addon_prefs.enable_for_node_editors
        disable_camera = addon_prefs.disable_camera_navigation
        navigation_mode = addon_prefs.navigation_mode

        space_type = context.space_data.type
        self._timer = None
        self._finished = False
        self._back_to_ortho = False

        if space_type == "VIEW_3D":
            view = context.space_data.region_3d.view_perspective
            if not (view == "CAMERA" and disable_camera):
                self._back_to_ortho = (
                    view == "ORTHO" and addon_prefs.return_to_ortho_on_exit
                )
                try:
                    if navigation_mode == "ORBIT":
                        result = bpy.ops.view3d.rotate("INVOKE_DEFAULT")
                    else:
                        result = bpy.ops.view3d.walk("INVOKE_DEFAULT")
                except RuntimeError:
                    self.report({"ERROR"}, "Cannot Navigate an Object with Constraints")
                    return {"CANCELLED"}
            else:
                return {"CANCELLED"}

        elif space_type == "NODE_EDITOR" and enable_nodes:
            result = bpy.ops.view2d.pan("INVOKE_DEFAULT")

        elif space_type == "IMAGE_EDITOR":
            bpy.ops.wm.call_panel(name="VIEW3D_PT_paint_texture_context_menu")
            return {"FINISHED"}
        else:
            return {"CANCELLED"}

        if "RUNNING_MODAL" not in result:
            return result

        # This timer only ensures cleanup after navigation; it never gates input.
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None


class RMN_OT_toggle_cam_navigation(Operator):
    """Turn Mouse Navigation of Camera On and Off"""

    bl_idname = "rmn.toggle_cam_navigation"
    bl_label = "Toggle Mouse Camera Navigation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon_prefs = context.preferences.addons[__package__].preferences
        addon_prefs.disable_camera_navigation = not addon_prefs.disable_camera_navigation
        return {"FINISHED"}
