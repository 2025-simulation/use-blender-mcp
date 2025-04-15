class BlenderMCPServer:
    # 类的初始化方法
    def __init__(self, host='localhost', port=9876):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None

    # 启动服务器的方法
    def start(self):
        # 检查服务器是否已经在运行
        if self.running:
            print("Server is already running")
            return
        
        self.running = True
        
        try:
            # 创建套接字
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            
            # 启动服务器线程
            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            print(f"BlenderMCP server started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {str(e)}")
            self.stop()

    # 停止服务器的方法
    def stop(self):
        self.running = False
        
        # 关闭套接字
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # 等待线程结束
        if self.server_thread:
            try:
                if self.server_thread.is_alive():
                    self.server_thread.join(timeout=1.0)
            except:
                pass
            self.server_thread = None
        
        print("BlenderMCP server stopped")

    # 服务器主循环方法
    def _server_loop(self):
        print("Server thread started")
        self.socket.settimeout(1.0)  # 设置超时时间
        
        while self.running:
            try:
                # 接受新连接
                try:
                    client, address = self.socket.accept()
                    print(f"Connected to client: {address}")
                    
                    # 在单独的线程中处理客户端
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    # 只是检查运行状态
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {str(e)}")
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error in server loop: {str(e)}")
                if not self.running:
                    break
                time.sleep(0.5)
        
        print("Server thread stopped")

    # 处理客户端连接的方法
    def _handle_client(self, client):
        print("Client handler started")
        client.settimeout(None)  # 无超时时间
        buffer = b''
        
        try:
            while self.running:
                # 接收数据
                try:
                    data = client.recv(8192)
                    if not data:
                        print("Client disconnected")
                        break
                    
                    buffer += data
                    try:
                        # 尝试解析命令
                        command = json.loads(buffer.decode('utf-8'))
                        buffer = b''
                        
                        # 在Blender的主线程中执行命令
                        def execute_wrapper():
                            try:
                                response = self.execute_command(command)
                                response_json = json.dumps(response)
                                try:
                                    client.sendall(response_json.encode('utf-8'))
                                except:
                                    print("Failed to send response - client disconnected")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                traceback.print_exc()
                                try:
                                    error_response = {
                                        "status": "error",
                                        "message": str(e)
                                    }
                                    client.sendall(json.dumps(error_response).encode('utf-8'))
                                except:
                                    pass
                            return None
                        
                        # 在主线程中调度执行
                        bpy.app.timers.register(execute_wrapper, first_interval=0.0)
                    except json.JSONDecodeError:
                        # 数据不完整，等待更多数据
                        pass
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")
                    break
        except Exception as e:
            print(f"Error in client handler: {str(e)}")
        finally:
            try:
                client.close()
            except:
                pass
            print("Client handler stopped")

    # 执行命令的方法
    def execute_command(self, command):
        try:
            cmd_type = command.get("type")
            params = command.get("params", {})
            
            # 确保在正确的上下文中
            if cmd_type in ["create_object", "modify_object", "delete_object"]:
                override = bpy.context.copy()
                override['area'] = [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D'][0]
                with bpy.context.temp_override(**override):
                    return self._execute_command_internal(command)
            else:
                return self._execute_command_internal(command)
                
        except Exception as e:
            print(f"Error executing command: {str(e)}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    # 内部执行命令的方法
    def _execute_command_internal(self, command):
        cmd_type = command.get("type")
        params = command.get("params", {})

        # 添加一个处理程序来检查PolyHaven状态
        if cmd_type == "get_polyhaven_status":
            return {"status": "success", "result": self.get_polyhaven_status()}
        
        # 基本处理程序
        handlers = {
            "get_scene_info": self.get_scene_info,
            "create_object": self.create_object,
            "modify_object": self.modify_object,
            "delete_object": self.delete_object,
            "get_object_info": self.get_object_info,
            "execute_code": self.execute_code,
            "set_material": self.set_material,
            "get_polyhaven_status": self.get_polyhaven_status,
            "get_hyper3d_status": self.get_hyper3d_status,
        }
        
        # 如果启用了Polyhaven，则添加Polyhaven处理程序
        if bpy.context.scene.blendermcp_use_polyhaven:
            polyhaven_handlers = {
                "get_polyhaven_categories": self.get_polyhaven_categories,
                "search_polyhaven_assets": self.search_polyhaven_assets,
                "download_polyhaven_asset": self.download_polyhaven_asset,
                "set_texture": self.set_texture,
            }
            handlers.update(polyhaven_handlers)
        
        # 如果启用了Hyper3d，则添加Hyper3d处理程序
        if bpy.context.scene.blendermcp_use_hyper3d:
            polyhaven_handlers = {
                "create_rodin_job": self.create_rodin_job,
                "poll_rodin_job_status": self.poll_rodin_job_status,
                "import_generated_asset": self.import_generated_asset,
            }
            handlers.update(polyhaven_handlers)

        handler = handlers.get(cmd_type)
        if handler:
            try:
                print(f"Executing handler for {cmd_type}")
                result = handler(**params)
                print(f"Handler execution complete")
                return {"status": "success", "result": result}
            except Exception as e:
                print(f"Error in handler: {str(e)}")
                traceback.print_exc()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command type: {cmd_type}"}

    # 获取简单信息的方法
    def get_simple_info(self):
        return {
            "blender_version": ".".join(str(v) for v in bpy.app.version),
            "scene_name": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects)
        }

    # 获取场景信息的方法
    def get_scene_info(self):
        try:
            print("Getting scene info...")
            # 简化场景信息以减少数据大小
            scene_info = {
                "name": bpy.context.scene.name,
                "object_count": len(bpy.context.scene.objects),
                "objects": [],
                "materials_count": len(bpy.data.materials),
            }
            
            # 收集最小的对象信息（限制为前10个对象）
            for i, obj in enumerate(bpy.context.scene.objects):
                if i >= 10:  # 从20减少到10
                    break
                    
                obj_info = {
                    "name": obj.name,
                    "type": obj.type,
                    # 仅包括基本的位置数据
                    "location": [round(float(obj.location.x), 2), 
                                round(float(obj.location.y), 2), 
                                round(float(obj.location.z), 2)],
                }
                scene_info["objects"].append(obj_info)
            
            print(f"Scene info collected: {len(scene_info['objects'])} objects")
            return scene_info
        except Exception as e:
            print(f"Error in get_scene_info: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}

    # 获取对象的轴对齐边界框（AABB）的静态方法
    @staticmethod
    def _get_aabb(obj):
        if obj.type != 'MESH':
            raise TypeError("Object must be a mesh")

        # 获取对象在局部空间中的边界框角点
        local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]

        # 转换为世界坐标
        world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]

        # 计算轴对齐的最小/最大坐标
        min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
        max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))

        return [
            [*min_corner], [*max_corner]
        ]

    # 创建对象的方法
    def create_object(self, type="CUBE", name=None, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1),
                    align="WORLD", major_segments=48, minor_segments=12, mode="MAJOR_MINOR",
                    major_radius=1.0, minor_radius=0.25, abso_major_rad=1.25, abso_minor_rad=0.75, generate_uvs=True):
        try:
            # 首先取消选择所有对象
            bpy.ops.object.select_all(action='DESELECT')
            
            # 根据类型创建对象
            if type == "CUBE":
                bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation, scale=scale)
            elif type == "SPHERE":
                bpy.ops.mesh.primitive_uv_sphere_add(location=location, rotation=rotation, scale=scale)
            elif type == "CYLINDER":
                bpy.ops.mesh.primitive_cylinder_add(location=location, rotation=rotation, scale=scale)
            elif type == "PLANE":
                bpy.ops.mesh.primitive_plane_add(location=location, rotation=rotation, scale=scale)
            elif type == "CONE":
                bpy.ops.mesh.primitive_cone_add(location=location, rotation=rotation, scale=scale)
            elif type == "TORUS":
                bpy.ops.mesh.primitive_torus_add(
                    align=align,
                    location=location,
                    rotation=rotation,
                    major_segments=major_segments,
                    minor_segments=minor_segments,
                    mode=mode,
                    major_radius=major_radius,
                    minor_radius=minor_radius,
                    abso_major_rad=abso_major_rad,
                    abso_minor_rad=abso_minor_rad,
                    generate_uvs=generate_uvs
                )
            elif type == "EMPTY":
                bpy.ops.object.empty_add(location=location, rotation=rotation, scale=scale)
            elif type == "CAMERA":
                bpy.ops.object.camera_add(location=location, rotation=rotation)
            elif type == "LIGHT":
                bpy.ops.object.light_add(type='POINT', location=location, rotation=rotation, scale=scale)
            else:
                raise ValueError(f"Unsupported object type: {type}")
            
            # 强制更新视图层
            bpy.context.view_layer.update()
            
            # 获取活动对象（应该是我们新创建的对象）
            obj = bpy.context.view_layer.objects.active
            
            # 如果没有活动对象，则出了问题
            if obj is None:
                raise RuntimeError("Failed to create object - no active object")
            
            # 确保它被选中
            obj.select_set(True)
            
            # 如果提供了名称，则重命名
            if name:
                obj.name = name
                if obj.data:
                    obj.data.name = name
            
            # 返回对象信息
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
        except Exception as e:
            print(f"Error in create_object: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}

    # 修改对象的方法
    def modify_object(self, name, location=None, rotation=None, scale=None, visible=None):
        # 按名称查找对象
        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object not found: {name}")
        
        # 根据请求修改属性
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

    # 删除对象的方法
    def delete_object(self, name):
        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object not found: {name}")
        
        # 存储名称以返回
        obj_name = obj.name
        
        # 选择并删除对象
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
        
        return {"deleted": obj_name}

    # 获取对象信息的方法
    def get_object_info(self, name):
        obj = bpy.data.objects.get(name)
        if not obj:
            raise ValueError(f"Object not found: {name}")
