from .lora_folder_browser import LoRAFolderBrowser

NODE_CLASS_MAPPINGS = {
    "LoRAFolderBrowser": LoRAFolderBrowser
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoRAFolderBrowser": "📂 LoRA Folder Browser"
}

# 确保前端 JS 能够被 ComfyUI 自动加载
WEB_DIRECTORY = "./js"