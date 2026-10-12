// Shared scripts

document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) {
        lucide.createIcons();
    }

    // Auto fade out success alerts after 5 seconds
    setTimeout(() => {
        const successAlerts = document.querySelectorAll('.animate-fade-in');
        successAlerts.forEach(alert => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
});

