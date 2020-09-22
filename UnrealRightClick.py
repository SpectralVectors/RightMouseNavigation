import bpy, ctypes


class UnrealRightClick(bpy.types.Operator):
    """Timer that decides whether to display a menu after Right Click"""
    bl_idname = "blui.unreal_right_click"
    bl_label = "Unreal Right Click"

    _timer = None
    _count = 0
    _threshold = 0.3
    MOUSE_RIGHTUP = 0x0010

    def modal(self, context, event):
        if context.space_data.type == 'VIEW_3D':
                if event.type in {'RIGHTMOUSE'}:   
                    if event.value in {'RELEASE'}:
                        self.cancel(context)
                        return {'CANCELLED'}

                if event.type == 'TIMER':
                    self._count += 0.01
                return {'PASS_THROUGH'}

    def execute(self, context):
        bpy.ops.view3d.walk('INVOKE_REGION_WIN') 
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        ctypes.windll.user32.mouse_event(self.MOUSE_RIGHTUP)
        
        context.window.cursor_modal_set('DEFAULT')
       
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        if self._count < self._threshold:
            
            if bpy.context.mode == 'SCULPT':
                 bpy.ops.wm.call_panel(name="VIEW3D_PT_"+context.mode.lower()
                +"_context_menu")
            elif bpy.context.mode == 'PAINT_VERTEX':
                 bpy.ops.wm.call_panel(name="VIEW3D_PT_"+context.mode.lower()
                +"_context_menu")
            elif bpy.context.mode == 'PAINT_WEIGHT':
                 bpy.ops.wm.call_panel(name="VIEW3D_PT_"+context.mode.lower()
                +"_context_menu")
            elif bpy.context.mode == 'PAINT_TEXTURE':
                 bpy.ops.wm.call_panel(name="VIEW3D_PT_"+context.mode.lower()
                +"_context_menu")
            elif bpy.context.mode == 'EDIT_MESH' or 'OBJECT':
                bpy.ops.wm.call_menu(name="VIEW3D_MT_"+context.mode.lower()
                +"_context_menu")
                
            
def register():
    bpy.utils.register_class(UnrealRightClick)


def unregister():
    bpy.utils.unregister_class(UnrealRightClick)


if __name__ == "__main__":
    register()
