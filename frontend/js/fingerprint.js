async function getFingerprint() {
    return {
        screen        : window.screen.width + "x" + window.screen.height,
        platform      : navigator.platform,
        language      : navigator.language,
        timezone      : Intl.DateTimeFormat().resolvedOptions().timeZone,
        userAgent     : navigator.userAgent,
        colorDepth    : window.screen.colorDepth,
        cores         : navigator.hardwareConcurrency,
        memory        : navigator.deviceMemory || "unknown",
        touchPoints   : navigator.maxTouchPoints,
        cookiesEnabled: navigator.cookieEnabled,
        canvas        : getCanvasFingerprint()
    };
}

function getCanvasFingerprint() {
    const canvas = document.createElement("canvas");
    const ctx    = canvas.getContext("2d");
    ctx.textBaseline = "top";
    ctx.font         = "14px Arial";
    ctx.fillText("Browser Fingerprint 🔒", 2, 2);
    return canvas.toDataURL();
}