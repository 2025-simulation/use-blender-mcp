#创建对象：create_object方法依据指定的类型、位置、旋转等参数在 Blender 中创建对象
def create_object(self, type="CUBE", name=None, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1),
                  align="WORLD", major_segments=48, minor_segments=12, mode="MAJOR_MINOR",
                  major_radius=1.0, minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75, generate_uvs=True):
    bpy.ops.object.select_all(action='DESELECT')
    if type == "CUBE":
        bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation, scale=scale)
    # ... 其他对象类型的创建
    obj = bpy.context.view_layer.objects.active
    if obj is None:
        raise RuntimeError("Failed to create object - no active object")
    obj.select_set(True)
    if name:
        obj.name = name
        if obj.data:
            obj.data.name = name
    result = {
        "name": obj.name,
        "type": obj.type,
        "location": [obj.location.x, obj.location.y, obj.location.z],
        "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
        "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
    }
    if obj.type == "MESH":
        bounding_box = self._get_aabb(obj)
        result["world_bounding_box"] = bounding_box
    return result

#修改对象：modify_object方法依据指定的名称查找对象，并修改其位置、旋转、缩放和可见性等属性。
def modify_object(self, name, location=None, rotation=None, scale=None, visible=None):
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object not found: {name}")
    if location is not None:
        obj.location = location
    if rotation is not None:
        obj.rotation_euler = rotation
    if scale is not None:
        obj.scale = scale
    if visible is not None:
        obj.hide_viewport = not visible
        obj.hide_render = not visible
    result = {
        "name": obj.name,
        "type": obj.type,
        "location": [obj.location.x, obj.location.y, obj.location.z],
        "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
        "scale": [obj.scale.x, obj.scale.y, obj.scale.z],
        "visible": obj.visible_get(),
    }
    if obj.type == "MESH":
        bounding_box = self._get_aabb(obj)
        result["world_bounding_box"] = bounding_box
    return result

#删除对象：delete_object方法依据指定的名称查找对象并将其从 Blender 场景中删除。
def delete_object(self, name):
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object not found: {name}")
    obj_name = obj.name
    bpy.data.objects.remove(obj, do_unlink=True)
    return {"deleted": obj_name}
