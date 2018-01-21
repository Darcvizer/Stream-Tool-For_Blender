import bpy
from bpy.types import Operator, Macro
from bpy_extras import view3d_utils
from mathutils import Vector
import rna_keymap_ui
from bpy.props import (
		EnumProperty,
		)

bl_info = {
	"name": "view snap",
	"location": "View3D > view snap",
	"description": "Snap View",
	"author": "Vladislav Kindushov",
	"version": (0, 3),
	"blender": (2, 7, 3),
	"category": "View3D",
}
PREFS = None

def getView(self, context, event):
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
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

class q(bpy.types.Operator):
	"""Border Occlusion selection """
	bl_idname = "view3d.q"
	bl_label = "q"

	def invoke(self, context, event):
		
		if PREFS.Mode == 'blender':
			if event.ctrl:
				vector = getView(self, context, event)
				name, value = ExcludeAxis(self, context, vector)
				findView2(self, context, name, value)
		elif PREFS.Mode == 'maya':
			if event.shift:
				vector = getView(self, context, event)
				name, value = ExcludeAxis(self, context, vector)
				findView2(self, context, name, value)
		elif PREFS.Mode == '3ds max':
			if event.shift:
				vector = getView(self, context, event)
				name, value = ExcludeAxis(self, context, vector)
				findView2(self, context, name, value)
		
		#if event.shift:

		return {'FINISHED'}
class z(bpy.types.Operator):
	bl_idname = "view3d.z"
	bl_label = "z"
	
	def invoke(self, context, event):
		if event.shift:
			ViewMacro.define('VIEW3D_OT_q')
		return {'FINISHED'}
		
	

class ViewMacro(Macro):
	bl_idname = 'view3d.view_snap'
	bl_label = 'view_snap'
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		ViewMacro.define('VIEW3D_OT_rotate')
		return {'FINISHED'}

	
	
	
def use_cashes(self, context):
	self.caches_valid = True

class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	Mode = EnumProperty(
		items=[('blender', "Blender", "Press ctrl after middle mouse button "),
			   ('maya', "Maya", "Press shift after left mouse button "),
			   ('3ds max', "3DS Max", "Press shift after middle mouse button")],
		name="Rotate mode",
		default='blender',
		update=use_cashes
	)
	caches_valid = True
	def draw(self, context):
		layout = self.layout
		layout.prop(self, "Mode")



def register():
	
	bpy.utils.register_module(__name__)
	
	ViewMacro.define('VIEW3D_OT_rotate')
	ViewMacro.define('VIEW3D_OT_z')

	
	global PREFS
	PREFS = bpy.context.user_preferences.addons[__name__].preferences

	kc = bpy.context.window_manager.keyconfigs.active
	if kc:
		km = kc.keymaps["3D View"]
		for kmi in km.keymap_items:
			if kmi.idname == 'view3d.rotate':
				kmi.idname = 'view3d.view_snap'
				break



def unregister():
	bpy.utils.unregister_module(__name__)
	kc = bpy.context.window_manager.keyconfigs.active
	if kc:
		km = kc.keymaps["3D View"]
		for kmi in km.keymap_items:
			if kmi.idname == 'view3d.view_snap':
				kmi.idname = 'view3d.rotate'


if __name__ == "__main__":
	register()
