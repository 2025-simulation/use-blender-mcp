# use-blender-mcp
## 概述：mcp是一种实现AI大模型与各种具有特定功能的软件/工具相连接的协议。在此我们借助cherry studio平台部署blender的mcp，将其与AI连接，以达到在cherry studio输入自然语言即可在blender生成相关模型的目的。这里有一个视频详细介绍了如何在blender上部署mcp，看完基本上就会了：https://www.youtube.com/watch?v=iqnE6jt2lPU&t=516s
## 具体步骤
### 1.cherry studio 上面部署blender-mcp ![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-14%20233701.png) 提前确保电脑有uv环境（可直接根据 cherry studio的指示下载uv）       
###  2.选择一个具有函数调用功能的AI（有扳手🔧图标）![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-15%20000006.png)然后启用mcp![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202025-04-14%20235637.png)
### 3.配置blender插件 addon.py https://github.com/ahujasid/blender-mcp/blob/main/addon.py 在blender内添加插件的步骤不再赘述
### 4.在blender内启用mcp ![](https://github.com/2025-simulation/use-blender-mcp/blob/main/images/start2025-04-15%20001306.png)另外，这里的两个选项是选择性的，使用后会调用Hyper 3D的api，当然api也先需要输入到上面的交互框内。
### 5.当这一切都准备好后，就可以在cherry studio中输入自然语言以生成blender模型了
