const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld(
    "api", {
        send: (channel, data) => {
            console.log(`Sending message to channel: ${channel}`)
            ipcRenderer.send(channel, data);
        }
    }
);
