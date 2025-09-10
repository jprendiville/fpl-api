document.addEventListener("DOMContentLoaded", function () {
    // Attach event listeners only to elements explicitly requiring a spinner
    var linksAndForms = document.querySelectorAll('a[data-trigger-spinner], form[data-trigger-spinner]');
    linksAndForms.forEach(function (element) {
        // Listen for 'click' event for links
        if (element.tagName === 'A') {
            element.addEventListener('click', function () {
                showOverlay();
            });
        }

        // Listen for 'submit' event for forms
        if (element.tagName === 'FORM') {
            element.addEventListener('submit', function () {
                showOverlay();
            });
        }
    });

    // Attach spinner to dropdowns with the data-trigger-spinner attribute
    var dropdowns = document.querySelectorAll('select[data-trigger-spinner]');
    dropdowns.forEach(function (dropdown) {
        dropdown.addEventListener('change', function () {
            showOverlay();
        });
    });

    // Listen for 'beforeunload' event to show spinner during page refresh
    window.addEventListener('beforeunload', function () {
        showOverlay();
    });

    // Hide the overlay when the entire page has loaded
    window.addEventListener('load', function () {
        hideOverlay();
    });
});

function showOverlay() {
    var overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'block';
    }
}

function hideOverlay() {
    var overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}
