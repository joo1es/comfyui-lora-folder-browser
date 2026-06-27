import os
import json
import folder_paths
from safetensors import safe_open
from server import PromptServer
from aiohttp import web

# 1. 递归获取多层子文件夹
def get_recursive_folders(root_path):
    if not root_path or not os.path.exists(root_path):
        return []
    folders = ["."]
    for root, dirs, files in os.walk(root_path):
        for d in dirs:
            full_path = os.path.join(root, d)
            rel_path = os.path.relpath(full_path, root_path)
            rel_path = rel_path.replace("\\", "/")
            folders.append(rel_path)
    return sorted(list(set(folders)))

# 2. 获取特定文件夹下的 LoRA 文件列表
def get_loras_in_folder(folder):
    lora_paths = folder_paths.get_folder_paths("loras")
    if not lora_paths:
        return []
    root = lora_paths[0]
    
    target_dir = root if folder == "." else os.path.join(root, folder)
    if not os.path.exists(target_dir):
        return []
        
    return sorted([f for f in os.listdir(target_dir) if f.endswith(".safetensors")])

# 3. 注册 API 路由
@PromptServer.instance.routes.get("/smart_lora/get_loras")
async def api_get_loras(request):
    folder = request.query.get("folder", ".")
    loras = get_loras_in_folder(folder)
    return web.json_response({"loras": loras})

# 辅助函数：递归在复杂的嵌套 Dict/List 中寻找指定的键（如 config JSON 中的 trigger_word）
def find_key_recursive(data, target_keys):
    if isinstance(data, dict):
        for k, v in data.items():
            if k.lower() in target_keys:
                return v
            res = find_key_recursive(v, target_keys)
            if res:
                return res
    elif isinstance(data, list):
        for item in data:
            res = find_key_recursive(item, target_keys)
            if res:
                return res
    return None

class LoRAFolderBrowser:
    @classmethod
    def INPUT_TYPES(cls):
        lora_paths = folder_paths.get_folder_paths("loras")
        root = lora_paths[0] if lora_paths else ""
        
        folders = get_recursive_folders(root)
        
        initial_folder = folders[0] if folders else "."
        initial_loras = get_loras_in_folder(initial_folder)
        if not initial_loras:
            initial_loras = ["None"]

        return {
            "required": {
                "folder": (folders,),
                "lora_name": (initial_loras,),
            }
        }

    # ==================== 修改 1：将第一个返回值类型改为 COMBO ====================
    RETURN_TYPES = ("*", "STRING")
    RETURN_NAMES = ("lora_path", "trigger")
    FUNCTION = "run"
    CATEGORY = "custom/lora"

    @classmethod
    def VALIDATE_INPUTS(cls, folder, lora_name):
        return True

    # ==================== 升级版的触发词读取函数 ====================
    def read_trigger(self, path):
        if not path or not os.path.isfile(path):
            return ""
        try:
            with safe_open(path, framework="pt") as f:
                meta = f.metadata()
            if not meta:
                return ""

            # 1. 尝试直接匹配标准/常见触发词键
            direct_keys = ["trigger_words", "modelspec.trigger_words", "dataset_trigger", "trigger_word"]
            for k in direct_keys:
                if k in meta:
                    val = meta[k]
                    if val:
                        return str(val).strip()

            # 2. 针对 FLUX 主流训练器 (AI-Toolkit / Ostris): 解析其嵌入的 config JSON 字符串
            config_str = meta.get("config", "")
            if config_str:
                try:
                    config_json = json.loads(config_str)
                    target_keys = ["trigger_word", "trigger_words", "dataset_trigger"]
                    found_val = find_key_recursive(config_json, target_keys)
                    if found_val:
                        return str(found_val).strip()
                except:
                    pass

            # 3. 针对 Kohya_ss 格式: 尝试从数据集文件夹解析触发词 (例如把 "10_concept_name" 还原为 "concept_name")
            dataset_dirs_str = meta.get("ss_dataset_dirs", "")
            if dataset_dirs_str:
                try:
                    dirs = json.loads(dataset_dirs_str)
                    triggers = []
                    for folder_path in dirs.keys():
                        folder_name = os.path.basename(folder_path.replace("\\", "/"))
                        # 检查命名是否符合 Kohya 标准 (数字+下划线+词)
                        parts = folder_name.split("_", 1)
                        if len(parts) == 2 and parts[0].isdigit():
                            triggers.append(parts[1])
                        else:
                            if folder_name not in ["", ".", ".."]:
                                triggers.append(folder_name)
                    if triggers:
                        return ", ".join(list(set(triggers))).strip()
                except:
                    pass

            # 4. 兜底方案：从 Kohya 的标签频率（ss_tag_frequency）的根目录名中提取
            tag_freq_str = meta.get("ss_tag_frequency", "")
            if tag_freq_str:
                try:
                    freqs = json.loads(tag_freq_str)
                    triggers = []
                    for folder_path in freqs.keys():
                        folder_name = os.path.basename(folder_path.replace("\\", "/"))
                        parts = folder_name.split("_", 1)
                        if len(parts) == 2 and parts[0].isdigit():
                            triggers.append(parts[1])
                        else:
                            if folder_name not in ["", ".", ".."]:
                                triggers.append(folder_name)
                    if triggers:
                        return ", ".join(list(set(triggers))).strip()
                except:
                    pass

        except Exception as e:
            print(f"[LoRAFolderBrowser] 读取元数据失败 {path}: {e}")

        return ""

    def run(self, folder, lora_name):
        lora_paths = folder_paths.get_folder_paths("loras")
        root = lora_paths[0] if lora_paths else ""
        
        if lora_name == "None" or not lora_name:
            return ("", "")
            
        # ==================== 修改 2：生成适配官方 LoraLoader 的相对路径 ====================
        if folder == "." or not folder:
            relative_path = lora_name
        else:
            relative_path = f"{folder}/{lora_name}"
            
        # 获取绝对路径用来读取触发词
        full_path = os.path.normpath(os.path.join(root, folder, lora_name))
        trigger = self.read_trigger(full_path)
        
        # 返回相对路径（作为 COMBO）和触发词
        return (relative_path, trigger)