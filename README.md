<h1 align="center">
Simple Assistant
</h1>

<p align="center">
  <a href="./docs/README_ZH.md">中文</a>
</p>

<p align="center">
Simple assistant, but not simple.
</p>

# Introduction

Simple Assistant is an AI-based assistant.

# How to use

## 1. Create a virtual environment(Optional)
### 1.1 Create a virtual environment
```bash
conda create -n SimpleAssistant python=3.11 -y
```
### 1.2 Activate the virtual environment
```bash
conda activate SimpleAssistant
```
## 2. Install dependencies
```bash
pip install -r requirements.txt
```
## 3. Set the configuration file
### 3.1 Copy the configuration file
If you are using Windows, run the following command to copy the configuration file.
```bat
copy config.yaml.example config.yaml
```
If you are using Linux or macOS, run the following command to copy the configuration file.
```bash
cp config.yaml.example config.yaml
```
### 3.2 Edit the configuration file
#### 3.2.1 Set the system prompt(Or use default)
For example:
```yaml
system_prompt: You are a helpful assistant.
```
#### 3.2.2 Set providers and models
Format:
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
#### 3.2.3 Set mcp servers
Format:
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
## 4. Run the webui
```bash
streamlit run main.py
```