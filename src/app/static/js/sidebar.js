document.getElementById('menu-toggle').addEventListener('click', function () {
    const sidebar = document.querySelector('.sidebar');
    const body = document.querySelector('body');
    sidebar.classList.toggle('closed');

    if (sidebar.classList.contains('closed')) {
        body.style.overflow = 'auto';
    } else {
        body.style.overflow = 'hidden';
    }

    fetch('/toggle-sidebar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    });
});