document.addEventListener('DOMContentLoaded', function() {
    var currentPath = window.location.pathname;

    var navLinks = document.querySelectorAll('.block-header-bar ul li a');
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.parentNode.classList.add('current_tab');
        }
    });
});