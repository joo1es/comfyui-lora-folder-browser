import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

// 将请求后端的逻辑单独抽出来，方便复用
async function updateLoraList(node, folderValue, isLoading = false) {
    try {
        // 动态清理，确保组件列表健康
        if (node.widgets) {
            node.widgets = node.widgets.filter(Boolean);
        }

        const loraWidget = node.widgets?.find((w) => w && w.name === "lora_name");
        if (!loraWidget) return;

        // 向后端请求对应文件夹的 lora 列表
        const response = await api.fetchApi(`/smart_lora/get_loras?folder=${encodeURIComponent(folderValue)}`);
        if (!response.ok) return;

        const data = await response.json();
        const loras = data.loras && data.loras.length > 0 ? data.loras : ["None"];

        // 更新下拉菜单的可选项
        if (loraWidget.options) {
            loraWidget.options.values = loras;
        }

        // 【关键判断】：如果是用户手动切换(isLoading=false)，且当前选中的不在新列表里，强制重置为第一个
        // 但如果是加载工作流(isLoading=true)，我们千万不要去改变它，保留工作流原本保存的值即可
        if (!isLoading) {
            if (!loras.includes(loraWidget.value)) {
                loraWidget.value = loras[0];
            }
        }

        node.graph?.setDirtyCanvas(true, true);
    } catch (error) {
        console.error("[SmartLora] Failed to update Lora list:", error);
    }
}

app.registerExtension({
    name: "SmartLora.Selector",

    // 1. 节点被创建，或用户手动操作时
    async nodeCreated(node) {
        if (node.comfyClass === "SmartLoraSelector") {
            if (node.widgets) {
                node.widgets = node.widgets.filter(Boolean);
            }

            const folderWidget = node.widgets?.find((w) => w && w.name === "folder");

            if (folderWidget) {
                const originalCallback = folderWidget.callback;

                // 用户手动切换文件夹时触发
                folderWidget.callback = async function (value) {
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    // isLoading 传 false，代表是手动切换，如果 lora 不匹配需要重置
                    await updateLoraList(node, value, false);
                };
            }
        }
    },

    // 2. 【核心新增】：当工作流被加载时（刷新网页、重启服务、拖入旧工作流）
    async loadedGraphNode(node, app) {
        if (node.comfyClass === "SmartLoraSelector") {
            const folderWidget = node.widgets?.find((w) => w && w.name === "folder");
            if (folderWidget && folderWidget.value) {
                // 读取工作流中保存的 folder 值，主动去后端请求一次列表
                // isLoading 传 true，代表只是静默更新列表内容，不要破坏用户保存的 lora_name 值
                await updateLoraList(node, folderWidget.value, true);
            }
        }
    }
});