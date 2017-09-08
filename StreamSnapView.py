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
			self.lock = False
			self.coord = None
			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

	def modal(self, context, event):

		if self.lock == False:
			self.lock = True
			#
			bpy.ops.view3d.rotate('INVOKE_DEFAULT')
			return {'RUNNING_MODAL'}
		if event.shift:# and event.value == 'PRESS':
			#if event.value == 'PRESS':
				vector = getView(self, context, event)
				name, value = ExcludeAxis(self, context, vector)
				findView2(self, context, name, value)
				print("sisi")
				return {'FINISHED'}
		if event.value == 'RELEASE':
			return {'FINISHED'}




		return {'PASS_THROUGH'}
		return {'RUNNING_MODAL'}


# # Preferences
# class AddonPreferences(bpy.types.AddonPreferences):
# 	bl_idname = __name__
#
# 	def draw(self, context):
# 		layout = self.layout
# 		wm = bpy.context.window_manager
# 		box = layout.box()
# 		split = box.split()
# 		col = split.column()
# 		col.label('Setup View Snap Hotkey')
# 		col.separator()
# 		kc = bpy.context.window_manager.keyconfigs.addon
# 		wm = bpy.context.window_manager
# 		#kc = wm.keyconfigs.user
# 		km = kc.keymaps['3D View Generic']
# 		kmi = get_hotkey_entry_item(km, 'view3d.Snap View Ortho', 'view3d.stream_snap_view')
# 		if kmi:
# 			col.context_pointer_set("keymap", km)
# 			rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
# 		else:
# 			col.label("No hotkey entry found")
# 			col.operator(Template_Add_Hotkey.bl_idname, text="Add hotkey entry", icon='ZOOMIN')
#
#
# # -----------------------------------------------------------------------------
# #    Keymap
# # -----------------------------------------------------------------------------
# addon_keymaps = []
#
#
# def get_addon_preferences():
# 	''' quick wrapper for referencing addon preferences '''
# 	addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
# 	return addon_preferences
#
#
# def get_hotkey_entry_item(km, kmi_name, kmi_value):
# 	'''
# 	returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
# 	if there are multiple hotkeys!)
# 	'''
# 	for i, km_item in enumerate(km.keymap_items):
# 		if km.keymap_items.keys()[i] == kmi_name:
# 			if km.keymap_items[i].properties.name == kmi_value:
# 				return km_item
# 	return None
#
#
# def add_hotkey():
# 	user_preferences = bpy.context.user_preferences
# 	addon_prefs = user_preferences.addons[__name__].preferences
#
# 	wm = bpy.context.window_manager
# 	kc = wm.keyconfigs.addon
# 	km = kc.keymaps.new(name="3D View Generic", space_type='VIEW_3D', region_type='WINDOW')
# 	kmi = km.keymap_items.new('view3d.Snap View Ortho', 'LEFTMOUSE', 'PRESS', alt=True)
# 	#kmi.properties.name = "view3d.StreamViewSnap"
# 	kmi.active = True
# 	addon_keymaps.append((km, kmi))
#
#
# class Template_Add_Hotkey(bpy.types.Operator):
# 	''' Add hotkey entry '''
# 	bl_idname = "template.add_hotkey"
# 	bl_label = "Addon Preferences Example"
# 	bl_options = {'REGISTER', 'INTERNAL'}
#
# 	def execute(self, context):
# 		add_hotkey()
#
# 		self.report({'INFO'}, "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
# 		return {'FINISHED'}
#
#
# def remove_hotkey():
# 	''' clears all addon level keymap hotkeys stored in addon_keymaps '''
# 	wm = bpy.context.window_manager
# 	kc = wm.keyconfigs.addon
# 	km = kc.keymaps['3D View Generic']
#
# 	for km, kmi in addon_keymaps:
# 		km.keymap_items.remove(kmi)
# 		wm.keyconfigs.addon.keymaps.remove(km)
# 	addon_keymaps.clear()

def register():
	bpy.utils.register_module(__name__)

	# hotkey setup
	#add_hotkey()

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
