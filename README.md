# comfyui-lora-folder-browser

> *Why are my folders getting deeper and deeper, making it harder and harder to find that one LoRA?* 😵‍💫
> Don't worry — this node lets you browse nested folders and auto-detects trigger words, so you can stop digging and start generating!

A ComfyUI node for browsing and selecting LoRA files from organized folder structures.

## Features

- **Folder Browsing**: Navigate through nested LoRA directories with ease
- **Auto Trigger Word Detection**: Automatically reads trigger words from LoRA metadata
  - Supports standard trigger word fields
  - Parses AI-Toolkit/Ostris config JSON
  - Extracts from Kohya_ss dataset directories
  - Falls back to tag frequency analysis
- **Clean Output**: Returns LoRA path and trigger word

## Node Inputs

| Input | Type | Description |
|-------|------|-------------|
| `folder` | COMBO | LoRA folder to browse (supports nested directories) |
| `lora_name` | COMBO | LoRA file to select from the chosen folder |

## Node Outputs

| Output | Type | Description |
|--------|------|-------------|
| `lora_path` | STRING | Relative path to the selected LoRA file |
| `trigger` | STRING | Auto-detected trigger word(s) |

## Usage

1. Add the node to your workflow from `custom/lora` category
2. Select a folder from the dropdown
3. Pick a LoRA file from that folder
4. Connect outputs to your LoRA loader node

## Installation

### Option 1: Git Clone (Recommended)

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/joo1es/comfyui-lora-folder-browser.git
```

Restart ComfyUI after cloning.

### Option 2: Manual

Copy this folder to `ComfyUI/custom_nodes/` and restart ComfyUI.
