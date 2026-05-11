# netfound.py - 网络探测核心模块

`[根目录](../CLAUDE.md) > **netfound.py**`

## 模块职责

提供网络探测的核心功能，包括:
- ICMP PING 存活检测
- TCP 端口开放检测
- HTTP/HTTPS 服务信息获取 (网页标题)
- SSH 远程连接与命令执行

## 入口与启动

```python
# 命令行模式
python netfound.py

# 异步批量扫描
async def main():
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(4)
    tasks = [loop.run_in_executor(executor, testip, f"{PREFIX}{i}", print_data_func) 
             for i in range(RANGE[0], RANGE[1])]
    await asyncio.wait(tasks)
```

## 对外接口

### 核心函数

| 函数 | 签名 | 说明 |
|------|------|------|
| `testip` | `(ip: str, data_func: Callable) -> str` | 测试单个IP的多个端口 |
| `add_port_tester` | `(pt: PortTester) -> None` | 动态添加端口测试器 |
| `test_port_open` | `(ip: str, port: int) -> bool` | 检测端口是否开放 |
| `https_request_pattern` | `(ip, port, protocol, pattern) -> str` | HTTP请求并匹配正则 |
| `ssh_request_cmd` | `(ip, port, protocol, cmd) -> str` | SSH执行命令 |

### 数据类

```python
class PortTester:
    name: str           # 测试名称 (如 "SSH")
    port: int           # 端口号 (如 22)
    protocol: str       # 协议 (如 "ssh")
    test_func: Callable  # 端口检测函数
    info_func: Callable  # 信息获取函数
    operate_func: Callable  # 操作函数 (双击触发)
```

### 内置端口测试器

| 名称 | 端口 | 协议 | 功能 |
|------|------|------|------|
| PING | -1 | icmp | ICMP存活检测 |
| HTTP | 80 | http | 获取网页标题 |
| HTTPS | 443 | https | 获取网页标题 |
| SSH | 22 | ssh | 获取主机名 |

## 关键依赖与配置

### 全局配置变量
```python
PREFIX = "10.10.20."
RANGE = [1, 20]
SSH_USERNAME = "ubuntu"
SSH_PASSWORD = " "
```

### 外部依赖
- `requests` - HTTP 请求
- `socket` - TCP 端口检测
- `paramiko` - SSH 连接
- `pythonping` - ICMP PING

## 数据模型

无持久化存储，所有数据通过回调函数实时传递给调用方:

```python
def data_func(name: str, ip: str, port: int, protocol: str, info_data: Any):
    """回调函数格式"""
    pass
```

## 测试与质量

- 无正式单元测试
- 可通过 `python netfound.py` 进行功能验证
- GUI模式提供交互式测试界面

## 常见问题 (FAQ)

**Q: SSH连接失败显示 "auth error"?**
> 检查 `SSH_USERNAME` 和 `SSH_PASSWORD` 配置是否正确

**Q: SSH连接失败显示 "incompatible peer"?**
> SSH版本或加密算法不兼容，可能需要升级 paramiko 或目标服务器的 SSH 配置

**Q: 如何添加自定义端口检测?**
> 使用 `add_port_tester()` 函数，传入自定义的 `PortTester` 实例

## 相关文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| netfound_gui.py | ../netfound_gui.py | GUI调用本模块 |
| requirements.txt | ../requirements.txt | 依赖声明 |

---

## 变更记录 (Changelog)

| 日期 | 变更内容 |
|------|----------|
| 2026-05-11 | 添加架构文档 |