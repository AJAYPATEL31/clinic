// Clinic On - Hospital Management System Javascript Helper
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds if not closed
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });
});
