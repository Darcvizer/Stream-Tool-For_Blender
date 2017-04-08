bl_info = {
    "name": "Stream tool Extrude :)",
    "description": "Quick tool Extrude",
    "author": "Vladislav Kindushov",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "Mesh",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }

import bpy
import bmesh
import bgl
import blf
from bpy.types import Operator
from bpy_extras import view3d_utils
from mathutils import Vector, Matrix

def UserPresets(self, context, chen):
	global save_user_drag
	#bpy.app.binary_path

	if chen == True:
		save_user_drag = context.user_preferences.edit.use_drag_immediately
		if save_user_drag != True:
			context.user_preferences.edit.use_drag_immediately = True

	elif chen == False:
		context.user_preferences.edit.use_drag_immediately = save_user_drag

def GetCoordMouse(self, context, event):
	'''Get Coordinate Mouse in 3d view'''
	#scene = context.scene
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y
	#rv3d.view_rotation * Vector((0.0, 0.0, -1.0))
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
	loc = view3d_utils.region_2d_to_location_3d(region, rv3d, coord, view_vector)
	return loc

def SetupAxis(self, temp_loc_first, temp_loc_last):

	first_x = temp_loc_first[0]
	first_y = temp_loc_first[1]
	first_z = temp_loc_first[2]

	last_x = temp_loc_last[0]
	last_y = temp_loc_last[1]
	last_z = temp_loc_last[2]

	x = first_x - last_x
	if x < 0:
		x = -x
	y = first_y - last_y
	if y < 0:
		y = -y
	z = first_z - last_z
	if z < 0:
		z = -z

	if x > y and x > z:
		return 'x'
	elif y > x and y > z:
		return 'y'
	elif z > x and z > y:
		return 'z'

def draw_along_normal(self, context):
	width = None
	for region in bpy.context.area.regions:
		if region.type == "TOOLS":
			width = region.width
			break
	font_id = 0
	blf.position(font_id, width+120, 100, 0)
	blf.size(font_id, 12, 72)
	blf.draw(font_id, "Space  Bar - Destructive Extrude")
	blf.position(font_id, width+120, 115, 0)
	blf.size(font_id, 12, 72)
	blf.draw(font_id, "Middle Mouse Bottom - Extrude Global Direction Axis")
	blf.position(font_id, width+120, 130, 0)
	blf.size(font_id, 12, 72)
	blf.draw(font_id, "Right Mouse Bottom - Extrude Vertex Normal")
	blf.position(font_id, width+120, 145, 0)
	blf.size(font_id, 12, 72)
	blf.draw(font_id, "Left Mouse Bottom - Extrude Along Normal")


def Extrude(self, context, axis):
	if self.axis == 'x':
		bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT',
										 TRANSFORM_OT_translate={"constraint_axis": (True, False, False)})
	elif self.axis == 'y':
		bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT',
										 TRANSFORM_OT_translate={"constraint_axis": (False, True, False)})
	elif self.axis == 'z':
		bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT',
										 TRANSFORM_OT_translate={"constraint_axis": (False, False, True)})



class StreamExtrude(Operator):
	bl_idname = "mesh.stream_extrude"
	bl_label = "Stream Extrude"
	bl_options = {'REGISTER', 'UNDO'}

	LB = False
	count_step = 0
	@classmethod
	def poll(cls,context):
		return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH"

# ______________________________INVOKE________________________________#


	def invoke(self,context, event):
		if context.space_data.type == 'VIEW_3D':
			self.merdg = bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge
			bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = False
			self.user_orint = bpy.context.space_data.transform_orientation
			bpy.context.space_data.transform_orientation = 'GLOBAL'
			UserPresets(self, context, True)
			self.temp_loc_first = GetCoordMouse(self, context, event)


			args = (self, context)
			self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_along_normal, args, 'WINDOW', 'POST_PIXEL')

			self.mouse_pos = 0


			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

#______________________________MODAL________________________________#

	def modal(self, context, event):
		context.area.tag_redraw()

		self.mouse_pos = event.mouse_region_x
		self.delta = (self.mouse_pos - event.mouse_region_x) * 100000

		if event.type == "RIGHTMOUSE":
			bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror": False},
											 TRANSFORM_OT_translate={"value": (0, 0, 0)})





			bpy.ops.transform.shrink_fatten('INVOKE_DEFAULT', use_even_offset=True)
			bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = self.merdg
			bpy.context.space_data.transform_orientation = self.user_orint
			UserPresets(self, context, False)
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'FINISHED'}

		elif event.type == "LEFTMOUSE":
			bpy.ops.view3d.edit_mesh_extrude_move_normal('INVOKE_DEFAULT')
			bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = self.merdg
			bpy.context.space_data.transform_orientation = self.user_orint
			UserPresets(self, context, False)
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'FINISHED'}

		elif event.type == 'MIDDLEMOUSE' or self.LB:
			self.LB = True
			if event.value == 'PRESS':
				if self.count_step <= 3:
					self.count_step += 1
					#print(self.count_step)
					return {'RUNNING_MODAL'}

				else:
					self.temp_loc_last = GetCoordMouse(self, context, event)
					self.axis = SetupAxis(self, self.temp_loc_first, self.temp_loc_last)
					Extrude(self,context, self.axis)
					return {'RUNNING_MODAL'}


			if event.value == 'RELEASE':
				bpy.context.space_data.transform_orientation = self.user_orint
				bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = self.merdg
				bpy.ops.mesh.select_more()
				bpy.ops.mesh.remove_doubles()
				UserPresets(self, context, False)
				bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
				return {'FINISHED'}

		elif event.type == 'SPACE':
			try:
				bpy.ops.mesh.destructive_extrude('INVOKE_DEFAULT')
			except:
				self.report({'WARNING'}, "Addon not found")
			try:
				bpy.ops.destructive.extrude('INVOKE_DEFAULT')
			except:
				self.report({'WARNING'}, "Addon not found")
			try:
				bpy.ops.view3d.destructive_extrude('INVOKE_DEFAULT')
			except:
				self.report({'WARNING'}, "Addon not found")
			bpy.context.space_data.transform_orientation = self.user_orint
			bpy.data.scenes['Scene'].tool_settings.use_mesh_automerge = self.merdg
			UserPresets(self, context, False)
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'FINISHED'}




		elif event.type in {'ESC'}:
			bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
			return {'CANCELLED'}
		return {'RUNNING_MODAL'}

def operator_draw(self,context):
	layout = self.layout
	col = layout.column(align=True)
	self.layout.operator_context = 'INVOKE_REGION_WIN'
	col.operator("mesh.stream_extrude", text="Stream Extrude")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_extrude.append(operator_draw)

	# kc = bpy.context.window_manager.keyconfigs.addon
	# if kc:
	# 	km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
	# 	kmi = km.keymap_items.new("view3d.smart_extrude", 'S', 'PRESS', )

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_extrude.remove(operator_draw)


if __name__ == "__main__":
	register()