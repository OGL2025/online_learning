document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 3000);
    });

    // Tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => {
        new bootstrap.Tooltip(el);
    });

    // --- THEME TUNER LOGIC ---
    const root = document.documentElement;
    
    // 1. Gradient Background Color
    const colorPickerGradient = document.getElementById('bgColorPicker');
    const savedGradientColor = localStorage.getItem('themeBgColor');
    
    if (savedGradientColor) {
        root.style.setProperty('--bg-theme-color', savedGradientColor);
        if(colorPickerGradient) colorPickerGradient.value = savedGradientColor;
    }

    if (colorPickerGradient) {
        colorPickerGradient.addEventListener('input', function(e) {
            const newColor = e.target.value;
            root.style.setProperty('--bg-theme-color', newColor);
            localStorage.setItem('themeBgColor', newColor);
        });
    }

    // 2. Root / Border Background Color
    const colorPickerRoot = document.getElementById('rootColorPicker');
    const savedRootColor = localStorage.getItem('themeRootColor');

    if (savedRootColor) {
        root.style.setProperty('--base-bg-color', savedRootColor);
        if(colorPickerRoot) colorPickerRoot.value = savedRootColor;
    }

    if (colorPickerRoot) {
        colorPickerRoot.addEventListener('input', function(e) {
            const newColor = e.target.value;
            root.style.setProperty('--base-bg-color', newColor);
            localStorage.setItem('themeRootColor', newColor);
        });
    }
});

function toggleTuner() {
    const panel = document.getElementById('tunerPanel');
    panel.classList.toggle('active');
}