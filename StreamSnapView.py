import bpy
from bpy_extras import view3d_utils
from mathutils import Vector
import rna_keymap_ui

bl_info = {
"name": "Stream Rotation Snap View",
"location": "View3D > Add > Mesh > Stream Rotation Snap View",
"description": "___",
"author": "Vladislav Kindushov",
"version": (0,1),
"blender": (2, 7, 8),
"category": "3D View"}

def getView(self, context, event):
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
	#view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	return rv3d.view_rotation * Vector((0.0, 0.0, -1.0))

def findView(self, context, event):
	vector = getView(self, context, event)
	if vector == Vector((0.0, -1.0, 0.0)):
		bpy.ops.view3d.viewnumpad(type='BACK', align_active=False)
	elif vector == Vector((0.0, 1.0, 0.0)):
		bpy.ops.view3d.viewnumpad(type='FRONT', align_active=False)
	elif vector == Vector((1.0, 0.0, 0.0)):
		bpy.ops.view3d.viewnumpad(type='RIGHT', align_active=False)
	elif vector == Vector((-1.0, 0.0, 0.0)):
		bpy.ops.view3d.viewnumpad(type='LEFT', align_active=False)
	elif vector == Vector((0.0, 0.0, 1.0)):
		bpy.ops.view3d.viewnumpad(type='TOP', align_active=False)
	elif vector == Vector((0.0, 0.0, -1.0)):
		bpy.ops.view3d.viewnumpad(type='BOTTOM', align_active=False)

def ExcludeAxis(self, context, vector):
	x = vector[0]
	y = vector[1]
	z = vector[2]

	if abs(x) > abs(y) and abs(x) > abs(z):
		return 'x', x
	elif abs(y) > abs(x) and abs(y) > abs(z):
		return 'y', y
	elif abs(z) > abs(x) and abs(z) > abs(y):
		return 'z', z

def findView2(self, context, axis, ax):
	if axis == 'x':
		if ax < 0:
			bpy.ops.view3d.viewnumpad(type='RIGHT', align_active=False)
		else:
			bpy.ops.view3d.viewnumpad(type='LEFT', align_active=False)
	elif axis == 'y':
		if ax < 0:
			bpy.ops.view3d.viewnumpad(type='BACK', align_active=False)
		else:
			bpy.ops.view3d.viewnumpad(type='FRONT', align_active=False)
	elif axis == 'z':
		if ax < 0:
			bpy.ops.view3d.viewnumpad(type='TOP', align_active=False)
		else:
			bpy.ops.view3d.viewnumpad(type='BOTTOM', align_active=False)


class StreamViewSnap(bpy.types.Operator):
	bl_idname = "view3d.stream_snap_view"
	bl_label = "Snap View Ortho"

	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			context.window_manager.modal_handler_add(self)
			bpy.ops.view3d.rotate('INVOKE_DEFAULT')
			
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

	def modal(self, context, event):
		if event.value == 'RELEASE':
			if event.shift:
				vector = getView(self, context, event)
				name, value = ExcludeAxis(self, context, vector)
				findView2(self, context, name, value)
			
				return {'FINISHED'}

		return {'PASS_THROUGH'}
		return {'RUNNING_MODAL'}



def register():
	bpy.utils.register_module(__name__)

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps["3D View"]
		for kmi in km.keymap_items:
			if kmi.idname == 'view3d.rotate':
				km.keymap_items.remove(kmi)
		km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
		kmi = km.keymap_items.new('view3d.stream_snap_view', 'LEFTMOUSE', 'PRESS', alt=True)



def unregister():
	bpy.utils.unregister_module(__name__)

	# hotkey cleanup
	#remove_hotkey()

	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps["3D View"]
		for kmi in km.keymap_items:
			if kmi.idname == 'view3d.stream_snap_view':
				km.keymap_items.remove(kmi)


if __name__ == "__main__":
	register()
