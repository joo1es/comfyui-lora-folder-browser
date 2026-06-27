from .smart_lora_node import SmartLoraSelector

NODE_CLASS_MAPPINGS = {
    "SmartLoraSelector": SmartLoraSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SmartLoraSelector": "📂 LoRA Folder Browser"
}

# 确保前端 JS 能够被 ComfyUI 自动加载
WEB_DIRECTORY = "./js"