import bpy, ctypes

bl_info = {
    'name': 'Unreal Right Click',
    'category': 'View 3D',
    'author': 'Spectral Vectors',
    'version': (0, 0, 1),
    'blender': (2, 90, 0),
    'location': '3D Viewport',
    "description": "Enables Unreal Engine Viewport Navigation"
}

class BLUI_OT_unreal_right_click(bpy.types.Operator):
    """Timer that decides whether to display a menu after Right Click"""
    bl_idname = "blui.unreal_right_click"
    bl_label = "Unreal Right Click"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _count = 0
    _threshold = 0.3
    MOUSE_RIGHTUP = 0x0010
    _finished = False

    def modal(self, context, event):
        # The _finished Boolean acts as a flag to exit the modal loop, it is not made True until after the cancel function is called
        if self._finished == True:
            return{'CANCELLED'}
        if context.space_data.type == 'VIEW_3D':
                if event.type in {'RIGHTMOUSE'}: 
                    if event.value in {'RELEASE'}:
                        # This fakes a Right Mouse Up event using Ctypes
                        ctypes.windll.user32.mouse_event(self.MOUSE_RIGHTUP)
                        # This brings back our mouse cursor to use with the menu
                        context.window.cursor_modal_restore()
                        # If the length of time you've been holding down Right Mouse is longer than the threshold value, then try to call a context menu, and if that fails, call a context panel
                        if self._count < self._threshold:
                            # Most of Blender's context menus can be called with
                            # the code in the 'try: except:' section, but there
                            # are a few modes that don't follow the same
                            # conventions, these are accounted for here
                            if context.mode == 'EDIT_ARMATURE':
                                bpy.ops.wm.call_menu(name="VIEW3D_MT_"+context.mode.lower()[5:].strip()+"_context_menu")
                                return{'PASS_THROUGH'}
                            if context.mode == 'EDIT_SURFACE':
                                bpy.ops.wm.call_menu(name="VIEW3D_MT_"+context.mode.lower())
                                return{'PASS_THROUGH'}
                            if context.mode == 'EDIT_TEXT':
                                bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_font_context_menu")
                                return{'PASS_THROUGH'}
                            else:
                                try:
                                    bpy.ops.wm.call_menu(name="VIEW3D_MT_"+context.mode.lower()+"_context_menu")
                                except:
                                    bpy.ops.wm.call_panel(name="VIEW3D_PT_"+context.mode.lower()+"_context_menu")
                        self.cancel(context)
                        # We now set the flag to true to exit the modal operator on the next loop through
                        self._finished = True
                        return {'PASS_THROUGH'}

                if event.type == 'TIMER':
                    self._count += 0.01
                return {'PASS_THROUGH'}

    def execute(self, context):
        # Execute is the first thing called in our operator, so we start by
        # calling Blender's built-in Walk Navigation
        bpy.ops.view3d.walk('INVOKE_DEFAULT')
        wm = context.window_manager
        # Adding the timer and starting the loop
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)     
            
def register():
    bpy.utils.register_class(BLUI_OT_unreal_right_click)


def unregister():
    bpy.utils.unregister_class(BLUI_OT_unreal_right_click)


if __name__ == "__main__":
    register()
