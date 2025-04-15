前言：这个是将blender的mcp插件提供给豆包，让他分析其中MCPServe部分各作用的结果
### 1.服务器启动与客户端连接处理
#### 启动服务器：BlenderMCPServer类的start方法会创建一个套接字并开始监听指定端口。一旦启动，服务器会在一个单独的线程里运行_server_loop方法。
![]()
#### 接受客户端连接：_server_loop方法持续监听客户端连接，当有新连接到来时，会启动一个新线程来处理该客户端，调用_handle_client方法。
def _server_loop(self):
    # ...
    while self.running:
        try:
            client, address = self.socket.accept()
            client_thread = threading.Thread(
                target=self._handle_client,
                args=(client,)
            )
            client_thread.daemon = True
            client_thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error accepting connection: {str(e)}")
    # ...
#### 处理客户端数据：_handle_client方法接收客户端发送的数据，将其解析为 JSON 格式的命令，然后调用execute_command方法来执行该命令。
def _handle_client(self, client):
    # ...
    while self.running:
        data = client.recv(8192)
        if not data:
            break
        buffer += data
        try:
            command = json.loads(buffer.decode('utf-8'))
            buffer = b''
            def execute_wrapper():
                response = self.execute_command(command)
                response_json = json.dumps(response)
                client.sendall(response_json.encode('utf-8'))
            bpy.app.timers.register(execute_wrapper, first_interval=0.0)
        except json.JSONDecodeError:
            pass
    # ...
### 2. 命令执行
#### 命令执行入口：execute_command方法依据命令类型判断是否需要切换到 3D 视图上下文，然后调用_execute_command_internal方法来执行具体命令。
