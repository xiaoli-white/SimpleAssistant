<h1 align="center">
Simple Assistant
</h1>

<p align="center">
简单助手，但不简单。
</p>

# 介绍

简单助手是一个基于AI的助手。

# 如何使用

## 1. 克隆存储库

```bash
git clone https://github.com/xiaoli-white/SimpleAssistant.git
```

## 2. 创建虚拟环境(可选)

### 2.1. 创建虚拟环境

```bash
conda create -n SimpleAssistant python=3.11 -y
```

### 2.2 激活虚拟环境

```bash
conda activate SimpleAssistant
```

## 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 4. 配置文件

### 4.1. 复制配置文件

如果您使用的是 Windows，请运行以下命令复制配置文件。

```bat
copy config.yaml.example config.yaml
```

如果您使用的是 Linux 或 macOS，请运行以下命令复制配置文件。

```bash
cp config.yaml.example config.yaml
```

### 4.2. 编辑配置文件

#### 4.2.1. 设置系统提示(或使用默认)

例如：

```yaml
system_prompt: You are a helpful assistant.
```

#### 4.2.2. 设置提供商和模型

格式：

```yaml
providers:
  provider-name:
    name: provider-name
    description: provider-description(Optional)
    base_url: server host
    api_key: API-Key(Optional)
models:
  model-name:
    name: model-name
    description: model-description(Optional)
    provider: provider-name
    model_name: model-name
    temperature: temperature(Optional)
    max_tokens: max tokens(Optional)
```

#### 4.2.3. 设置mcp服务器

格式：

```yaml
mcp-servers:
  mcp-server-name:
    name: mcp-server-name
    description: mcp-server-description(Optional)
    protocol: sse or stdio
    # For sse
    url: server host
    # For stdio
    command: command
    args:
      - arg1
      - arg2
      - ...
```

## 5. 运行webui

```bash
streamlit run main.py
```