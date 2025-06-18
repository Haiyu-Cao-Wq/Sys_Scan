import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import os
import psutil
import threading
from datetime import datetime
from send2trash import send2trash
import winsound  # 用于播放警告声
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler('file_scanner_debug.log')  # 输出到文件
    ]
)

class FileDetailsDialog:
    def __init__(self, parent, file_path):
        logging.info(f"打开文件详细信息窗口: {file_path}")
        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title("文件详细信息")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='black')  # 设置对话框背景为黑色
        
        # 使对话框成为模态窗口
        self.dialog.transient(parent.root)
        self.dialog.grab_set()
        
        self.file_path = file_path
        self.parent = parent
        
        # 设置样式
        style = ttk.Style()
        style.configure("Details.TLabel", foreground='green', background='black')
        style.configure("Details.TFrame", background='black')
        style.configure("Details.TButton", foreground='green', background='black')
        
        self.setup_ui()
        
        # 居中显示
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10", style="Details.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件信息显示
        try:
            file_stat = os.stat(self.file_path)
            file_info = [
                ("文件名:", os.path.basename(self.file_path)),
                ("路径:", os.path.dirname(self.file_path)),
                ("大小:", self.format_size(file_stat.st_size)),
                ("创建时间:", datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")),
                ("修改时间:", datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")),
                ("访问时间:", datetime.fromtimestamp(file_stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")),
            ]

            for i, (label, value) in enumerate(file_info):
                ttk.Label(main_frame, text=label, style="Details.TLabel").grid(row=i, column=0, sticky="e", padx=5, pady=2)
                ttk.Label(main_frame, text=value, style="Details.TLabel").grid(row=i, column=1, sticky="w", padx=5, pady=2)

            # 按钮框架
            button_frame = ttk.Frame(main_frame, style="Details.TFrame")
            button_frame.grid(row=len(file_info), column=0, columnspan=2, pady=20)

            ttk.Button(button_frame, text="删除文件", command=self.delete_file, style="Details.TButton").pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="打开所在文件夹", command=self.open_folder, style="Details.TButton").pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="关闭", command=self.dialog.destroy, style="Details.TButton").pack(side=tk.LEFT, padx=5)

        except Exception as e:
            logging.error(f"获取文件信息时出错: {str(e)}")
            ttk.Label(main_frame, text=f"错误: {str(e)}", style="Details.TLabel").pack(pady=20)
            ttk.Button(main_frame, text="关闭", command=self.dialog.destroy, style="Details.TButton").pack(pady=10)
        
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
            
    def delete_file(self):
        logging.info(f"尝试删除文件: {self.file_path}")
        try:
            # 播放自定义提示音（两声低音+两声高音）
            winsound.Beep(800, 200)   # 800Hz, 持续200毫秒
            time.sleep(0.1)           # 间隔0.1秒
            winsound.Beep(800, 200)   # 800Hz, 持续200毫秒
            time.sleep(0.1)           # 间隔0.1秒
            winsound.Beep(1000, 200)  # 1000Hz, 持续200毫秒
            time.sleep(0.1)           # 间隔0.1秒
            winsound.Beep(1000, 200)  # 1000Hz, 持续200毫秒
            
            # 创建自定义确认对话框
            confirm_dialog = tk.Toplevel(self.dialog)
            confirm_dialog.title("确认删除")
            confirm_dialog.geometry("300x150")
            confirm_dialog.configure(bg='black')
            confirm_dialog.transient(self.dialog)
            confirm_dialog.grab_set()
            
            # 居中显示对话框
            confirm_dialog.geometry("+%d+%d" % (
                self.dialog.winfo_rootx() + self.dialog.winfo_width()/2 - 150,
                self.dialog.winfo_rooty() + self.dialog.winfo_height()/2 - 75
            ))
            
            # 添加警告图标和文本
            warning_frame = ttk.Frame(confirm_dialog, style="TFrame")
            warning_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            warning_text = ttk.Label(
                warning_frame,
                text="确定要删除这个文件吗？\n此操作将把文件移动到回收站。",
                style="TLabel"
            )
            warning_text.pack(pady=10)
            
            # 按钮框架
            button_frame = ttk.Frame(warning_frame, style="TFrame")
            button_frame.pack(pady=10)
            
            def confirm_delete():
                confirm_dialog.destroy()
                try:
                    send2trash(self.file_path)
                    logging.info("文件已成功移动到回收站")
                    # 播放删除成功提示音（一声上升音）
                    winsound.Beep(800, 100)
                    time.sleep(0.05)
                    winsound.Beep(1200, 1000)  # 延长到1秒
                    self.dialog.destroy()
                    if hasattr(self.parent, 'refresh_file_lists'):
                        self.parent.refresh_file_lists(self.file_path)
                except Exception as e:
                    logging.error(f"删除文件时出错: {str(e)}")
                    # 播放错误提示音（三声低音）
                    for _ in range(3):
                        winsound.Beep(500, 100)
                        time.sleep(0.05)
                    messagebox.showerror("错误", f"无法删除文件：\n{str(e)}")
            
            def cancel_delete():
                confirm_dialog.destroy()
            
            # 确认和取消按钮
            ttk.Button(button_frame, text="确认", command=confirm_delete).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="取消", command=cancel_delete).pack(side=tk.LEFT, padx=10)
            
            # 设置对话框为模态
            confirm_dialog.wait_window()
            
        except Exception as e:
            logging.error(f"删除文件时出错: {str(e)}")
            messagebox.showerror("错误", f"操作失败：\n{str(e)}")
        
    def get_file_type(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        type_map = {
            '.txt': '文本文件',
            '.doc': 'Word文档',
            '.docx': 'Word文档',
            '.pdf': 'PDF文档',
            '.jpg': 'JPEG图片',
            '.jpeg': 'JPEG图片',
            '.png': 'PNG图片',
            '.gif': 'GIF图片',
            '.mp3': '音频文件',
            '.mp4': '视频文件',
            '.zip': '压缩文件',
            '.rar': '压缩文件',
            '.exe': '可执行文件'
        }
        return type_map.get(ext, f"{ext} 文件")
        
    def get_file_permissions(self, mode):
        permissions = []
        if mode & 0o400: permissions.append("可读")
        if mode & 0o200: permissions.append("可写")
        if mode & 0o100: permissions.append("可执行")
        return " | ".join(permissions)

    def open_folder(self):
        os.startfile(os.path.dirname(self.file_path))

class FileScanner:
    def __init__(self):
        logging.info("初始化文件扫描器")
        self.root = ThemedTk(theme="black")
        self.root.title("File Scanner v1.0")
        self.root.geometry("1200x600")
        
        # Variables
        self.scanning = False
        self.total_files = 0
        self.scanned_files = 0
        self.min_size = tk.StringVar(value="0")
        self.selected_drive = tk.StringVar()
        self.file_trees = {}  # 存储所有的树视图
        
        self.setup_ui()
        
    def setup_ui(self):
        # 设置主题和样式
        self.root.configure(bg='black')  # 设置主窗口背景为黑色
        self.root.geometry("1200x600")   # 设置窗口大小
        
        # 创建和配置样式
        style = ttk.Style()
        style.configure(".", foreground='green', background='black')  # 默认样式
        style.configure("Treeview", foreground='green', background='black', fieldbackground='black', rowheight=25)  # 树形视图
        style.configure("Treeview.Heading", foreground='green', background='black', font=('Arial', 10))  # 树形视图标题
        style.map('Treeview', background=[('selected', 'dark green')], foreground=[('selected', 'black')])  # 选中项样式
        style.configure("TLabel", foreground='green', background='black')  # 标签
        style.configure("TButton", foreground='green', background='black')  # 按钮
        style.configure("TFrame", background='black')  # 框架
        style.configure("Vertical.TScrollbar", background='black', troughcolor='black', arrowcolor='green')  # 滚动条
        style.configure("Horizontal.TScrollbar", background='black', troughcolor='black', arrowcolor='green')  # 滚动条
        style.configure("TCombobox", foreground='green', background='black', fieldbackground='black', selectbackground='dark green', selectforeground='black')  # 下拉框
        
        # Top Frame
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Drive Selection
        ttk.Label(top_frame, text="选择磁盘:").pack(side=tk.LEFT, padx=5)
        drives_combo = ttk.Combobox(top_frame, textvariable=self.selected_drive, width=10)
        drives = [d.device for d in psutil.disk_partitions() if 'removable' not in d.opts.lower()]
        drives_combo['values'] = drives
        drives_combo.pack(side=tk.LEFT, padx=5)
        if drives:
            drives_combo.set(drives[0])
            
        # Min File Size - 使用传统的tk.Entry以获得完全的样式控制
        ttk.Label(top_frame, text="最小文件大小(MB):").pack(side=tk.LEFT, padx=5)
        self.size_entry = tk.Entry(top_frame, textvariable=self.min_size, width=10,
                            fg='green', bg='black', insertbackground='green')  # insertbackground设置光标颜色
        self.size_entry.pack(side=tk.LEFT, padx=5)
        
        # Scan Button
        self.scan_button = ttk.Button(top_frame, text="开始扫描", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        # Stop Button
        self.stop_button = ttk.Button(top_frame, text="停止扫描", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.StringVar(value="准备就绪")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5, expand=True)
        
        # Tab Control
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Create tabs
        tabs = ['所有文件', '文档', '图片', '视频', '音频', '压缩文件', '安装包', '代码', '数据库', '日志', '备份', '其他']
        
        for tab in tabs:
            frame = ttk.Frame(self.tab_control)
            self.tab_control.add(frame, text=tab)
            
            # Create treeview
            tree = self.create_file_tree(frame, tab)
            
    def create_file_tree(self, tab, category):
        # 创建树形视图
        tree = ttk.Treeview(tab, columns=("size", "modified", "path"), show="headings", style="Treeview")
        
        # 设置列标题和宽度
        tree.heading("size", text="文件大小")
        tree.heading("modified", text="修改时间")
        tree.heading("path", text="文件路径")
        
        # 设置列宽
        tree.column("size", width=100, anchor="w")  # 文件大小列
        tree.column("modified", width=150, anchor="w")  # 修改时间列
        tree.column("path", width=900, anchor="w")  # 文件路径列
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        # 配置树形视图的滚动
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        
        self.file_trees[category] = tree
        
        # 绑定双击事件
        tree.bind("<Double-1>", lambda e: self.show_file_details(e, tree))
        
        return tree
        
    def get_drives(self):
        drives = []
        for partition in psutil.disk_partitions():
            if 'fixed' in partition.opts:
                drives.append(partition.device[0])
        return drives
        
    def get_file_category(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx']:
            return '文档'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return '图片'
        elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
            return '视频'
        elif ext in ['.mp3', '.wav', '.flac', '.m4a']:
            return '音频'
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return '压缩文件'
        elif ext in ['.exe', '.msi', '.pkg']:
            return '安装包'
        elif ext in ['.py', '.java', '.cpp', '.js', '.html', '.css']:
            return '代码'
        elif ext in ['.db', '.sqlite', '.mdb']:
            return '数据库'
        elif ext in ['.log']:
            return '日志'
        elif ext in ['.bak', '.backup']:
            return '备份'
        else:
            return '其他'
            
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
            
    def start_scan(self):
        if not self.selected_drive.get():
            messagebox.showerror("错误", "请选择要扫描的磁盘!")
            return
            
        try:
            min_size = float(self.min_size.get()) * 1024 * 1024  # Convert MB to bytes
        except ValueError:
            messagebox.showerror("错误", "请输入有效的最小文件大小!")
            return
            
        # Clear previous results
        for tree in self.file_trees.values():
            for item in tree.get_children():
                tree.delete(item)
                
        self.scanning = True
        self.scan_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start scanning in a separate thread
        self.scan_thread = threading.Thread(target=self.scan_directory, 
                                         args=(self.selected_drive.get(), min_size))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
    def stop_scan(self):
        self.scanning = False
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def scan_directory(self, start_path, min_size):
        logging.info(f"开始扫描目录: {start_path}, 最小文件大小: {min_size}字节")
        try:
            for root, dirs, files in os.walk(start_path):
                if not self.scanning:
                    logging.info("扫描被用户中止")
                    break
                    
                for file in files:
                    if not self.scanning:
                        break
                        
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        
                        if file_size >= min_size:
                            category = self.get_file_category(file_path)
                            modified_time = datetime.fromtimestamp(
                                os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                            
                            logging.debug(f"找到文件: {file_path}, 大小: {self.format_size(file_size)}")
                            
                            # Add to both category and all files
                            self.root.after(0, self.add_file_to_tree, 
                                          self.file_trees[category],
                                          file_path, 
                                          self.format_size(file_size),
                                          modified_time)
                            
                            if category != '所有文件':
                                self.root.after(0, self.add_file_to_tree,
                                              self.file_trees['所有文件'],
                                              file_path,
                                              self.format_size(file_size),
                                              modified_time)
                        
                        self.scanned_files += 1
                        self.root.after(0, self.update_progress)
                        
                    except (PermissionError, FileNotFoundError) as e:
                        logging.warning(f"访问文件时出错: {file_path}, 错误: {str(e)}")
                        continue
                    except Exception as e:
                        logging.error(f"处理文件时出错: {file_path}, 错误: {str(e)}", exc_info=True)
                        continue
                        
            logging.info(f"扫描完成, 共处理 {self.scanned_files} 个文件")
            self.root.after(0, self.scan_complete)
        except Exception as e:
            logging.error(f"扫描目录时出错: {str(e)}", exc_info=True)
            self.root.after(0, lambda: messagebox.showerror("错误", f"扫描目录时出错：\n{str(e)}"))
            self.root.after(0, self.scan_complete)
        
    def add_file_to_tree(self, tree, file_path, size, modified):
        tree.insert('', 'end', values=(size, modified, file_path))
        
    def update_progress(self):
        self.progress_label.config(text=f"已扫描: {self.scanned_files} 个文件")
        
    def scan_complete(self):
        self.scanning = False
        self.scan_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("完成", f"扫描完成!\n共扫描 {self.scanned_files} 个文件")
        self.scanned_files = 0
        
    def show_context_menu(self, event, tree):
        # 创建右键菜单
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="删除选中文件", command=lambda: self.delete_selected(tree))
        menu.add_command(label="打开所在文件夹", command=lambda: self.open_file_location(tree))
        
        # 显示菜单
        menu.post(event.x_root, event.y_root)

    def open_file_location(self, tree=None):
        if tree is None:
            tree = self.file_trees[self.tab_control.select()]
        
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择文件!")
            return
            
        file_path = tree.item(selection[0])['values'][2]
        folder_path = os.path.dirname(file_path)
        os.startfile(folder_path)

    def delete_selected(self, tree=None):
        if tree is None:
            tree = self.file_trees[self.tab_control.select()]
            
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的文件!")
            return
            
        if not messagebox.askyesno("确认", "确定要删除选中的文件吗?\n这些文件将被移动到回收站。"):
            return
            
        deleted_files = []
        failed_files = []
        
        for item in selection:
            file_path = tree.item(item)['values'][2]
            try:
                send2trash(file_path)
                deleted_files.append(file_path)
                # 从所有标签页中删除该文件
                for t in self.file_trees.values():
                    for item in t.get_children():
                        if t.item(item)['values'][2] == file_path:
                            t.delete(item)
            except Exception as e:
                failed_files.append(f"{file_path}: {str(e)}")
                
        if deleted_files:
            messagebox.showinfo("成功", f"成功删除 {len(deleted_files)} 个文件到回收站")
        if failed_files:
            messagebox.showerror("错误", "以下文件删除失败:\n" + "\n".join(failed_files))
            
    def show_file_details(self, event, tree):
        """显示文件详细信息"""
        item = tree.selection()[0]
        file_path = tree.item(item)["values"][2]  # 获取完整文件路径
        logging.info(f"显示文件详细信息: {file_path}")
        try:
            FileDetailsDialog(self, file_path)  # Pass self (FileScanner instance) as parent
        except Exception as e:
            logging.error(f"显示文件详细信息时出错: {str(e)}", exc_info=True)
            messagebox.showerror("错误", f"无法显示文件详细信息：\n{str(e)}")

    def refresh_file_lists(self, deleted_file_path):
        """从所有树视图中删除文件"""
        logging.info(f"刷新文件列表，删除文件: {deleted_file_path}")
        try:
            for tree in self.file_trees.values():
                for item in tree.get_children():
                    if tree.item(item)["values"][2] == deleted_file_path:
                        tree.delete(item)
                        logging.debug(f"从树视图中删除了文件项: {deleted_file_path}")
                        break
        except Exception as e:
            logging.error(f"刷新文件列表时出错: {str(e)}", exc_info=True)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = FileScanner()
    app.run() 