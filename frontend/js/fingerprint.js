async function getFingerprint() {
    return {
        screen: window.screen.width + "x" + window.screen.height,
        platform: navigator.platform,
        language: navigator.language
    };
}