


# Blender MCP 

## “BlenderMCPServer文件夹”里有MCP利用blender的function call

先看每个文件夹内的md文件

## How to set up Blender-mcp 

## 概述
mcp 是一种实现AI大模型与各种具有特定功能的软件/工具相连接的协议。
在此我们借助 cherry studio 平台部署 blender 的 mcp ，将其与AI连接，以达到在 cherry studio 输入自然语言即可在 blender 生成相关模型的目的。
这里有一个[视频](https://www.youtube.com/watch?v=iqnE6jt2lPU&t=516s)详细介绍了如何在 blender 上部署 mcp，看完基本上就会了

## 具体步骤
### Preparation 

提前确保电脑有 uv 环境（可直接根据 cherry studio 的 [教程](https://docs.cherry-ai.com/advanced-basic/mcp/install) 下载 uv）       

### 1.cherry studio 上面部署 blender-mcp
![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-14%20233701.png) 

先保存，然后再启用，否则会报错


###  2.选择一个具有函数调用功能的AI（有扳手🔧图标）
![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-15%20000006.png)
然后启用 mcp
![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-14%20235637.png)

### 3.配置 blender 插件 需要下载 [addon.py](./useMCP/addon.py)

在文件里有，来自 [here](https://github.com/ahujasid/blender-mcp/blob/main/addon.py) 在 blender 内添加插件的步骤不再赘述

### 4.在 blender 内启用 mcp ![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/start2025-04-15%20001306.png)
另外，这里的两个选项是选择性的，使用后会调用 Hyper 3D 的 api，当然 api 也先需要输入到上面的交互框内。

### 5.成果展示
![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-09%20232846.png)

## 参考材料 

- [blender-mcp](https://github.com/ahujasid/blender-mcp)
- [mcp servers](https://github.com/modelcontextprotocol/servers)
