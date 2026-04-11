// CampusConnect - Client-side helpers
// Caio Albuquerque (caio-a18)
//
// Nothing heavy here — just a couple small UX improvements.
// The real logic lives server-side in app.py.

document.addEventListener("DOMContentLoaded", function () {

    // Auto-dismiss flash messages after 4 seconds
    const flashMessages = document.querySelectorAll(".flash");
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = "opacity 0.5s";
            msg.style.opacity = "0";
            setTimeout(function () {
                msg.remove();
            }, 500);
        }, 4000);
    });


    // Confirm before removing a saved school
    // Finds any remove/unsave form and attaches a confirmation dialog
    const removeForms = document.querySelectorAll("form[action*='unsave']");
    removeForms.forEach(function (form) {
        form.addEventListener("submit", function (e) {
            const confirmed = confirm("Remove this school from your saved list?");
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });


    // Highlight the active nav link based on the current URL path
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-links a");
    navLinks.forEach(function (link) {
        if (link.getAttribute("href") === currentPath) {
            link.style.color = "white";
            link.style.fontWeight = "600";
        }
    });

});
