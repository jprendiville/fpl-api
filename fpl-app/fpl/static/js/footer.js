document.addEventListener('DOMContentLoaded', function () {
    // Select all toast elements
    var toastElements = document.querySelectorAll('[id^="toastMessage"]');

    // Function to show each toast sequentially
    function showToastSequentially(toasts, index) {
        if (index >= toasts.length) {
            return; // Stop if there are no more toasts
        }

        var toastEl = toasts[index];
        var messageStatus = toastEl.getAttribute('data-status');
        var delay = parseInt(toastEl.getAttribute('data-bs-delay')) || 5000; // Default to 5000ms if delay not found

        // Reset classes before applying new ones
        toastEl.classList.remove('text-white', 'text-dark');

        // Apply the correct Bootstrap class based on the status
        if (messageStatus === 'success') {
            toastEl.classList.add('bg-success', 'text-white');
        } else if (messageStatus === 'warning') {
            toastEl.classList.add('bg-warning', 'text-dark');
        } else if (messageStatus === 'error') {
            toastEl.classList.add('bg-danger', 'text-white');
        } else {
            toastEl.classList.add('bg-info');  // Fallback to info class
        }

        // Show the toast
        var toast = new bootstrap.Toast(toastEl);
        toast.show();

        // Wait for the toast to hide before showing the next one
        setTimeout(function () {
            toast.hide(); // Hide the current toast after delay
            showToastSequentially(toasts, index + 1); // Show the next toast
        }, delay + 1000); // Delay + extra time for smooth transition
    }

    // Start showing toasts from the first one
    if (toastElements.length > 0) {
        showToastSequentially(toastElements, 0);
    }
});
