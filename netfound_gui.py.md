# netfound_gui.py - GUI界面模块

`[根目录](../CLAUDE.md) > **netfound_gui.py**`

## 模块职责

提供基于 Tkinter 的图形用户界面，用于:
- IP 地址段配置 (前缀 + 范围)
- SSH 认证信息输入
- 扫描任务启动/停止控制
- 结果表格展示与双击操作

## 入口与启动

```python
# 启动GUI
python netfound_gui.py

# 或作为模块调用
from netfound_gui import MainDialog
md = MainDialog()
md.mainloop()
```

## 对外接口

### MainDialog 类

```python
class MainDialog:
    def __init__(self) -> None:
        """初始化GUI界面，创建主窗口、输入框、表格"""
        
    def thread_run_async(self) -> None:
        """在子线程中运行异步任务"""
        
    def mainloop(self) -> None:
        """启动Tkinter事件循环"""
```

### GUI 组件结构

```
MainDialog
├── tk (tkinter.Tk)
│   ├── info_frame (状态信息)
│   ├── input_frame (IP范围输入)
│   ├── input_frame2 (SSH认证输入)
│   ├── button_frame (开始/停止按钮)
│   └── table (ttk.Treeview 结果表格)
```

## 关键依赖与配置

### 内部依赖
- `netfound` - 核心网络探测模块
- `asyncio` - 异步任务管理
- `threading` - 多线程执行

### GUI 库
- `tkinter` - Python标准GUI库
- `tkinter.ttk` - 主题化组件
- `tkinter.messagebox` - 消息对话框

## 数据模型

### 输入配置
```python
ip_prefix: str     # IP前缀 (如 "10.10.20.")
ip_range1: int     # IP范围起始 (如 1)
ip_range2: int     # IP范围结束 (如 50)
ssh_account: str   # SSH用户名
ssh_password: str  # SSH密码
```

### 表格数据结构
```python
columns = ['IP'] + [pt.name for pt in netfound.PORT_TESTS]
# 示例列: ['IP', 'PING', 'HTTP', 'HTTPS', 'SSH']
```

## 测试与质量

- 手动测试: 运行 GUI 执行扫描操作
- 边界测试: 测试 IP 格式验证、超大范围扫描

## 双击操作 (operate_func)

| 列名 | 双击行为 |
|------|----------|
| PING | 重新执行 PING 并显示延迟 |
| HTTP | 在浏览器打开 `http://ip:port` |
| HTTPS | 在浏览器打开 `https://ip:port` |
| SSH | 显示 SSH 连接信息 |

## 常见问题 (FAQ)

**Q: 启动报错 "No module named 'netfound'"?**
> 确保 netfound.py 与 netfound_gui.py 在同一目录

**Q: IP格式验证失败?**
> 必须输入3组数字(如 `192.168.1.`) 用 `.` 分隔

**Q: 扫描过程中如何停止?**
> 点击"停止"按钮终止所有线程任务

## 相关文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| netfound.py | ../netfound.py | 核心探测逻辑 |
| requirements.txt | ../requirements.txt | Python依赖 |
| netfound_gui.spec | ../netfound_gui.spec | PyInstaller配置 |

---

## 变更记录 (Changelog)

| 日期 | 变更内容 |
|------|----------|
| 2026-05-11 | 添加架构文档 |