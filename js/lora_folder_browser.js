import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

async function updateLoraList(node, folderValue, isLoading = false) {
    try {
        if (node.widgets) {
            node.widgets = node.widgets.filter(Boolean);
        }

        const loraWidget = node.widgets?.find((w) => w && w.name === "lora_name");
        if (!loraWidget) return;

        const response = await api.fetchApi(`/smart_lora/get_loras?folder=${encodeURIComponent(folderValue)}`);
        if (!response.ok) return;

        const data = await response.json();
        const loras = data.loras && data.loras.length > 0 ? data.loras : ["None"];

        if (loraWidget.options) {
            loraWidget.options.values = loras;
        }

        if (!isLoading) {
            if (!loras.includes(loraWidget.value)) {
                loraWidget.value = loras[0];
            }
        }

        node.graph?.setDirtyCanvas(true, true);
    } catch (error) {
        console.error("[LoRAFolderBrowser] Failed to update Lora list:", error);
    }
}

app.registerExtension({
    name: "LoRAFolderBrowser",

    async nodeCreated(node) {
        if (node.comfyClass === "LoRAFolderBrowser") {
            if (node.widgets) {
                node.widgets = node.widgets.filter(Boolean);
            }

            const folderWidget = node.widgets?.find((w) => w && w.name === "folder");

            if (folderWidget) {
                const originalCallback = folderWidget.callback;

                folderWidget.callback = async function (value) {
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    await updateLoraList(node, value, false);
                };
            }
        }
    },

    async loadedGraphNode(node, app) {
        if (node.comfyClass === "LoRAFolderBrowser") {
            const folderWidget = node.widgets?.find((w) => w && w.name === "folder");
            if (folderWidget && folderWidget.value) {
                await updateLoraList(node, folderWidget.value, true);
            }
        }
    }
});
