# File Scanner

一个用Python开发的文件扫描工具，可以帮助你扫描和管理磁盘中的文件。

## 功能特点

- 选择磁盘分区进行扫描
- 设置最小文件大小过滤
- 实时显示扫描进度
- 按文件类型自动分类
- 显示文件大小、修改时间和完整路径
- 支持停止扫描操作
- 美观的深色主题界面

## 文件分类

- 所有文件
- 文档 (.txt, .doc, .docx, .pdf, .xls, .xlsx, .ppt, .pptx)
- 图片 (.jpg, .jpeg, .png, .gif, .bmp)
- 视频 (.mp4, .avi, .mkv, .mov)
- 音频 (.mp3, .wav, .flac, .m4a)
- 压缩文件 (.zip, .rar, .7z, .tar, .gz)
- 安装包 (.exe, .msi, .pkg)
- 代码 (.py, .java, .cpp, .js, .html, .css)
- 数据库 (.db, .sqlite, .mdb)
- 日志 (.log)
- 备份 (.bak, .backup)
- 其他 (不属于以上类别的文件)

## 安装要求

1. Python 3.6+
2. 必需的Python包：
   ```
   tkinter (通常随Python一起安装)
   ttkthemes==3.2.2
   psutil==5.9.5
   send2trash==1.8.2
   ```

## 安装步骤

1. 克隆或下载此仓库
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行程序：
   ```
   python file_scanner.py
   ```
2. 在界面上选择要扫描的磁盘分区
3. 设置最小文件大小（可选）
4. 点击"开始扫描"按钮
5. 等待扫描完成
6. 在不同的标签页中查看分类后的文件

## 注意事项

- 扫描大容量磁盘可能需要较长时间
- 某些系统文件或需要管理员权限的文件可能无法访问
- 可以随时点击"停止扫描"按钮中断扫描过程 