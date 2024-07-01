import asyncio
import re
import tkinter
import os
from typing import List
from tkinter import ttk, messagebox
from tkinter.constants import *
import threading

from concurrent.futures import ThreadPoolExecutor
import netfound

async def test_ip_async(ip, data_func):
    netfound.testip(ip, data_func)

class MainDialog():
    def __init__(self,) -> None:
        
        self.tk = tkinter.Tk()
        self.tk.title("网络探测工具")
        self.tk.geometry("600x600")

        self.loop:asyncio.AbstractEventLoop = None
        self.executor: ThreadPoolExecutor = None
        self.task_done_num:int = 0
        self.tasks : List[asyncio.Task] = []

        columns = ['IP',]
        columns += [pt.name for pt in netfound.PORT_TESTS]
        col_idx = {k:i for i, k in enumerate(columns) }

        frame = ttk.Frame(self.tk, relief=RIDGE, borderwidth=2)
        frame.pack(fill=BOTH,expand=1)

        # input tabel data
        def input_data_func(name:str, ip: str, port: int, protocol:str, info_data):
            if port == -1:
                init_data = [ip, info_data]
                init_data += ["" for _ in netfound.PORT_TESTS]
                table.insert("", END, id=ip, values=init_data)
            else:
                loc = table.index(ip)
                if loc >= 0:
                    idx = col_idx.get(name, 0)
                    table.set(ip, idx, f"[√]{info_data}")
                print(f"{ip}, -> {name},{port}:{info_data}")

        # callback
        def task_done_call(fut : asyncio.Future, ip):
            self.task_done_num += 1
            
            print(f"{fut._state} {self.task_done_num}, ip: {ip}")
            if self.loop.is_running():
                state = "运行中"
                t = f"{state}:{self.task_done_num}/{len(self.tasks)}"
                self.mesg_str.set(t)


        #######################
        # infomations
        self.mesg_str = tkinter.StringVar(self.tk, value="请确认参数")
        info_frame = ttk.Frame(frame, borderwidth=2)
        info_frame.pack(fill=BOTH, side=TOP)
        self.mesg = ttk.Label(info_frame, textvariable=self.mesg_str)
        self.mesg.pack(fill=BOTH, side=TOP)
        
        #######################
        # inputs
        def _pattern_validate(content, prev, entry_name, pattern):
            check_pass =  re.match(pattern, content) is not None
            if not check_pass:
                print(entry_name)
                entry:ttk.Entry = self.tk.nametowidget(entry_name)
                entry.config(foreground='red')

            return check_pass
        
        pattern_validate_cmd = self.tk.register(_pattern_validate)
        # lambda: re.match(r"^\d{,3}\.\d{,3}\.\d{,3}\.?$", ip_prefix.get()) is not None, 
        ip_prefix = tkinter.StringVar(value="10.10.20.")
        ip_range1 = tkinter.IntVar(value=1)
        ip_range2 = tkinter.IntVar(value=50)

        ssh_account = tkinter.StringVar(value="ubuntu")
        ssh_password = tkinter.StringVar(value="")

        input_frame = ttk.Frame(frame, borderwidth=2)
        input_frame.pack(fill=X, side=TOP)
        
        _ip_tip = ttk.Label(input_frame, text="IP范围：",width=10)
        _ip_tip.pack(fill=X, side=LEFT)

        _prefix = ttk.Entry(input_frame, name="ip_prefix", textvariable=ip_prefix,
                                validate="focusout", validatecommand=(pattern_validate_cmd, '%P', '%s', '%W', r"^\d{,3}\.\d{,3}\.\d{,3}\.?$"), 
                                invalidcommand=lambda: messagebox.showerror("输入错误", "必须输入规范的IP前缀，包含3组数字，并用.分割")
                                )
        _prefix.pack(fill=X, side=LEFT)

        _range1 = ttk.Entry(input_frame, name="ip_range1", textvariable=ip_range1, width=4,
                                validate="focusout", validatecommand=(pattern_validate_cmd, '%P', '%s', '%W', r"^\d{,3}$"), 
                                invalidcommand=lambda: messagebox.showerror("输入错误", "必须输入小于255的数字")
                                )
        _range1.pack(fill=X, side=LEFT)

        _range_line = ttk.Label(input_frame, text="-->")
        _range_line.pack(fill=X, side=LEFT)

        _range2 = ttk.Entry(input_frame, name="ip_range2", textvariable=ip_range2, width=4,
                                validate="focusout", validatecommand=(pattern_validate_cmd, '%P', '%s', '%W', r"^\d{,3}$"), 
                                invalidcommand=lambda: messagebox.showerror("输入错误", "必须输入小于255的数字")
                                )
        _range2.pack(fill=X, side=LEFT)

        input_frame2 = ttk.Frame(frame, borderwidth=2)
        input_frame2.pack(fill=X, side=TOP)
        
        _inp_tip1 = ttk.Label(input_frame2, text="SSH账号：",width=10)
        _inp_tip1.pack(fill=X, side=LEFT)
        _ssh_uname = ttk.Entry(input_frame2, name="ssh_account", textvariable=ssh_account, width=8)
        _ssh_uname.pack(fill=X, side=LEFT)

        _inp_tip2 = ttk.Label(input_frame2, text="SSH密码：",width=10)
        _inp_tip2.pack(fill=X, side=LEFT)
        _ssh_passwd = ttk.Entry(input_frame2, name="ssh_password", textvariable=ssh_password, width=8, show="*")
        _ssh_passwd.pack(fill=X, side=LEFT)

        #######################
        # buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=BOTH, side=TOP)
        def start_click():
            self.stop_btn.config(state=ACTIVE)
            self.start_btn.config(state=DISABLED)
            clear_table(table)

            prefix = ip_prefix.get()
            
            range1 = ip_range1.get()
            range2 = ip_range2.get()

            netfound.SSH_USERNAME = ssh_account.get()
            netfound.SSH_PASSWORD = ssh_password.get()
            execut_num = int(os.cpu_count()/2)

            print(f"running in {execut_num} threads")
            self.mesg_str.set(f"{execut_num}线程 运行中")

            self.executor = ThreadPoolExecutor(execut_num)
            self.loop = asyncio.new_event_loop()
            self.loop.set_default_executor(self.executor)
            self.task_done_num = 0
            self.tasks = []
            for i in range(range1, range2):
                # task = self.loop.create_task(test_ip_async(f"{prefix}{i}", input_data_func))
                ip = f"{prefix}{i}"
                task = self.loop.run_in_executor(self.executor, netfound.testip, ip, input_data_func)
                def make_callback(ip2):
                    return lambda x: task_done_call(x, ip2)
                task.add_done_callback(make_callback(ip))
                self.tasks.append(task)
            t = threading.Thread(target=self.thread_run_async)
            t.start()
            
        self.start_btn = ttk.Button(button_frame, text="开始", command=start_click)
        self.start_btn.pack(fill=X, side=LEFT)

        def stop_click():
            self.executor.shutdown(False, cancel_futures=True)
            self.stop_btn.config(state=DISABLED)
            # self.start_btn.config(state=ACTIVE)
            pass
        self.stop_btn = ttk.Button(button_frame, text="停止", command=stop_click, state="disabled")
        self.stop_btn.pack(fill=X, side=LEFT)
        
        #################
        # table
        def clear_table(treeview : ttk.Treeview):
            children = treeview.get_children()
            if len(children):
                treeview.delete(*treeview.get_children())

        def treeview_sort_column(tv:ttk.Treeview, col, reverse):  # Treeview、列名、排列方式
            l = [(tv.set(k, col), k) for k in tv.get_children('')]
            l.sort(reverse=reverse)  # 排序方式
            # rearrange items in sorted positions
            for index, (val, k) in enumerate(l):  # 根据排序后索引移动
                tv.move(k, '', index)
            tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))  
        
        def double_click_cell(event : tkinter.Event) -> object:
            tv:ttk.Treeview = event.widget
            # for item in tv.selection():
            #     item_text = tv.item(item, "values")
            column= tv.identify_column(event.x)# 列
            cn = int(str(column).replace('#',''))-1
            row = tv.identify_row(event.y)  # 行
            values = tv.item(row, "values")
            col_name = columns[cn]
            # print(f"col: {column}:{col_name}, row: {row}")
            if cn == 0:
                # line of ip
                self.tk.clipboard_clear()
                self.tk.clipboard_append(row)
                self.mesg_str.set(f"[{row}]已复制")
                pass

            for pt in netfound.PORT_TESTS:
                if pt.name == col_name:
                    res = pt.operate_func(row, pt.port, pt.protocol, values[cn])
                    if res:
                        tv.set(row, cn, res)

            return True

        table = ttk.Treeview(frame, columns=columns, show='headings',height=30, selectmode="browse")
        for column in columns:
            table.heading(column=column, text=column, anchor=CENTER, command=lambda _col=column: treeview_sort_column(table, _col, False))  # 定义表头
            table.column(column=column, width=100, minwidth=30, anchor=CENTER, stretch=True)  # 定义列
        
        table.bind('<Double-1>', double_click_cell) # 双击左键进入编辑
        table.pack(side=TOP, fill=BOTH, expand=YES)
        
        scroller = ttk.Scrollbar(table, command=table.yview)
        table.config(yscrollcommand=scroller.set)
        scroller.pack(side=RIGHT, fill=Y)
        pass

    def thread_run_async(self):
        finish_co = asyncio.wait(self.tasks)
        self.loop.run_until_complete(finish_co)
        
        self.loop.stop()
        self.loop.close()

        self.stop_btn.config(state=DISABLED)
        self.start_btn.config(state=ACTIVE)
    
    def mainloop(self):
        self.tk.mainloop()

def main():
    md = MainDialog()
    md.mainloop()

if __name__ == "__main__":
    main()