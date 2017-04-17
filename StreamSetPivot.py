import bpy
import bmesh
from bpy_extras import view3d_utils
from bpy.props import IntProperty, FloatProperty
from mathutils.bvhtree import BVHTree
from mathutils import Vector, Matrix

bl_info = {
"name": "Stream Quick Set Pivot",
"location": "View3D > Add > Mesh > Stream Quiс Set Pivot",
"description": "___",
"author": "Vladislav Kindushov",
"version": (0,1),
"blender": (2, 7, 8),
"category": "Mesh",}



def GetUserSetings(self, context):
	global pivot
	global orientation
	global active_obj_name
	global select_obj
	global selected_vertices_one
	global edit_mode
	global cursor_loc
	global user_snap_target

	user_snap_target = context.scene.tool_settings.snap_target
	pivot = context.space_data.pivot_point
	orientation = context.space_data.transform_orientation
	cursor_loc = context.scene.cursor_location

	if context.mode == 'OBJECT':
		active_obj_name = context.active_object.name
		select_obj = context.selected_objects
		print(select_obj)

	elif context.mode == 'EDIT_MESH':
		edit_mode = bpy.context.tool_settings.mesh_select_mode
		selected_vertices_one = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if
									  i.select]

def ObjReturnSel(self):
	for i in select_obj:
		i.select = True
	bpy.context.scene.objects.active = bpy.data.objects[active_obj_name]

def ReturnSelElement(self):
	obj = bpy.context.edit_object
	me = obj.data
	bm = bmesh.from_edit_mesh(me)
	for i in selected_vertices_one:
		bm.verts[i].select = True
	bpy.context.tool_settings.mesh_select_mode = edit_mode



def ReturnOrint(self):
	context.space_data.transform_orientation = orientation





def Rotation(self, context, vec):
	obj = bpy.context.active_object
	#obj.hide
	axis = Vector((0.0, 0.0, 1.0))
	q = axis.rotation_difference(vec)
	loc, rot, scale = obj.matrix_world.decompose()
	mat_scale = Matrix()

	for i in range(3):
		mat_scale[i][i] = scale[i]

	obj.matrix_world = (
		Matrix.Translation(loc) *
		q.to_matrix().to_4x4() *
		mat_scale)

def CreateOrientation(self, context, event, vec):
	if context.mode == 'OBJECT':
		bpy.ops.object.empty_add(type='PLAIN_AXES')

		Rotation(self, context, vec)
		context.space_data.transform_orientation = "NORMAL"
		bpy.ops.transform.create_orientation(name="Smart_Orientation", use=True, overwrite=True)
		bpy.ops.object.delete(use_global=True)
		ObjReturnSel(self)

	elif context.mode == 'EDIT_MESH':
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.context.tool_settings.mesh_select_mode = (True, True, True)

		loc = event.mouse_region_x, event.mouse_region_y
		bpy.ops.view3d.select(extend=True, location=loc)
		try:
			bpy.ops.transform.create_orientation(name="Smart_Orientation", use=True, overwrite=True)
		except:
			None
		bpy.ops.mesh.select_all(action='DESELECT')
		ReturnSelElement(self)



def RayCast(self, context, event, ray_max=1000.0):
	"""Run this function on left mouse, execute the ray cast"""
	# get the context arguments
	scene = context.scene
	region = context.region
	rv3d = context.region_data
	coord = event.mouse_region_x, event.mouse_region_y

	# get the ray from the viewport and mouse
	view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord).normalized()
	ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

	ray_target = ray_origin + view_vector

	def visible_objects_and_duplis():
		"""Loop over (object, matrix) pairs (mesh only)"""

		for obj in context.visible_objects:
			if obj.type == 'MESH':
				yield (obj, obj.matrix_world.copy())

			if obj.dupli_type != 'NONE':
				obj.dupli_list_create(scene)
				for dob in obj.dupli_list:
					obj_dupli = dob.object
					if obj_dupli.type == 'MESH':
						yield (obj_dupli, dob.matrix.copy())

			obj.dupli_list_clear()

	def obj_ray_cast(obj, matrix):
		"""Wrapper for ray casting that moves the ray into object space"""

		# get the ray relative to the object
		matrix_inv = matrix.inverted()
		ray_origin_obj = matrix_inv * ray_origin
		ray_target_obj = matrix_inv * ray_target
		ray_direction_obj = ray_target_obj - ray_origin_obj
		d = ray_direction_obj.length

		ray_direction_obj.normalize()

		# cast the ray
		bvh = BVHTree.FromObject(obj, context.scene)
		location, normal, face_index, d = bvh.ray_cast(ray_origin_obj, ray_direction_obj)

		if face_index != -1:
			return location, normal, face_index
		else:
			return None, None, None

	# cast rays and find the closest object
	best_length_squared = -1.0
	best_obj = None
	best_matrix = None
	best_face = None
	best_hit = None

	for obj, matrix in visible_objects_and_duplis():
		if obj.type == 'MESH':
			hit, normal, face_index = obj_ray_cast(obj, matrix)
			if hit is not None:
				hit_world = matrix * hit
				scene.cursor_location = hit_world
				length_squared = (hit_world - ray_origin).length_squared
				if best_obj is None or length_squared < best_length_squared:
					best_length_squared = length_squared
					best_obj = obj
					best_matrix = matrix
					best_face = face_index
					best_hit = hit
					break

	if best_obj is not None:
		best_distance = float("inf")  # use float("inf") (infinity) to have unlimited search range
		mesh = best_obj.data
		best_matrix = best_obj.matrix_world
		for vert_index in mesh.polygons[best_face].vertices:
			vert_coord = mesh.vertices[vert_index].co
			distance = (vert_coord - best_hit).magnitude
			if distance < best_distance:
				best_distance = distance
				CreateOrientation(self, context, event, vert_coord)
				scene.cursor_location = best_matrix * vert_coord
		mesh.update(calc_edges=True, calc_tessface=False)
		for v0, v1 in mesh.polygons[best_face].edge_keys:
			p0 = obj.data.vertices[v0].co
			p1 = obj.data.vertices[v1].co
			p = (p0 + p1) / 2
			distance = (p - best_hit).magnitude
			if distance < best_distance:
				best_distance = distance
				vec = p0-p1
				CreateOrientation(self, context, event, vec)
				scene.cursor_location = best_matrix * p



		face_pos = Vector(mesh.polygons[best_face].center)
		distance = (face_pos - best_hit).magnitude
		if distance < best_distance:
			best_distance = distance
			vec = mesh.polygons[best_face].normal.copy()
			CreateOrientation(self, context, event, vec)
			scene.cursor_location = best_matrix * face_pos



class StreamSetPivot(bpy.types.Operator):
	bl_idname = "stream.pivot"
	bl_label = "Stream Quick Set Pivot"
	bl_options = {'REGISTER', 'UNDO'}


	@classmethod
	def pool(cls, context):
		return (context.active_object == 'MESH') and (not context.active_object.hide) and context.active_object

#__________________________INVOKE____________________#

	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':
			context.window_manager.modal_handler_add(self)
			GetUserSetings(self, context)
			context.space_data.pivot_point = 'CURSOR'
			ob = context.object
			self.BVH = BVHTree.FromObject(ob, context.scene)
			context.scene.tool_settings.snap_target = 'CENTER'

			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

# __________________________MODAL____________________#

	def modal(self, context, event):
		if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'LEFTMOUSE', 'RIGHTMOUSE'} and (event.alt or event.shift):
			return {'PASS_THROUGH'}

		elif event.type == 'MOUSEMOVE':
			RayCast(self, context, event)
			return {'RUNNING_MODAL'}

		elif event.type == 'LEFTMOUSE':
			bpy.ops.transform.delete_orientation('INVOKE_DEFAULT')

			bpy.ops.stream.pivot_haunter('INVOKE_DEFAULT')

			return {'FINISHED'}

		elif event.type == 'MIDDLEMOUSE':
			context.space_data.pivot_point = pivot
			#bpy.ops.transform.delete_orientation('INVOKE_DEFAULT')
			return {'FINISHED'}

		elif event.type == 'RIGHTMOUSE':
			context.space_data.pivot_point = 'CURSOR'
			context.scene.cursor_location = cursor_loc
			bpy.ops.stream.pivot_haunter('INVOKE_DEFAULT')

			return {'FINISHED'}

		elif event.type in {'ESC'}:
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}


class StreamPivotHaunter(bpy.types.Operator):
	bl_idname = "stream.pivot_haunter"
	bl_label = "Stream Pivot Haunter"

	@classmethod
	def pool(cls, context):
		return context.space_data.type == "VIEW_3D"

	def invoke(self, context, event):
		if context.space_data.type == 'VIEW_3D':

			context.window_manager.modal_handler_add(self)
			return {'RUNNING_MODAL'}
		else:
			self.report({'WARNING'}, "Active space must be a View3d")
			return {'CANCELLED'}

	def modal(self, context, event):
		try:
			if context.mode == 'OBJECT':
				self.sel_buffer = context.selected_objects
				if self.sel_buffer != select_obj:
					if pivot == 'CURSOR':
						context.space_data.pivot_point = 'MEDIAN_POINT'
					else:
						context.space_data.pivot_point = pivot
					context.scene.tool_settings.snap_target = user_snap_target
					context.scene.cursor_location = cursor_loc
					try:
						bpy.ops.transform.delete_orientation('INVOKE_DEFAULT')

					except:
						None
					context.space_data.transform_orientation = orientation
					return {'FINISHED'}
				else:
					return {'PASS_THROUGH'}
			elif context.mode == 'EDIT_MESH':
				self.selection_vertices_two = [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]
				if selected_vertices_one != self.selection_vertices_two:
					context.space_data.pivot_point = pivot
					context.scene.tool_settings.snap_target = user_snap_target
					try:
						context.space_data.transform_orientation = orientation
					except:
						None
					try:
						bpy.ops.transform.delete_orientation('INVOKE_DEFAULT')

					except:
						None

					context.scene.cursor_location = cursor_loc

					return {'FINISHED'}
				else:
					return {'PASS_THROUGH'}
			else:
				return {'PASS_THROUGH'}
		except:
			if pivot == 'CURSOR':
				context.space_data.pivot_point = 'MEDIAN_POINT'
			else:
				context.space_data.pivot_point = pivot
			try:
				context.space_data.transform_orientation = orientation
			except:
				None
			context.scene.cursor_location = cursor_loc
			return {'FINISHED'}

		return {'RUNNING_MODAL'}

def register():
	bpy.utils.register_class(StreamSetPivot)
	bpy.utils.register_class(StreamPivotHaunter)
	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
		kmi = km.keymap_items.new('stream.pivot', 'D', 'PRESS',)

def unregister():
	bpy.utils.unregister_class(StreamSetPivot)
	bpy.utils.unregister_class(StreamPivotHaunter)
	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps["3D View"]
		for kmi in km.keymap_items:
			if kmi.idname == 'stream.pivot':
				km.keymap_items.remove(kmi)


if __name__ == "__main__":
	register()
