if (typeof SlimSelect !== 'undefined') {
    attachFilter('#compose', 'compose', 'Filter by compose');
    attachFilter('#docker_host', 'docker_host', 'Filter by docker host');
}

document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = new URL(window.location);
        const hasFilter = url.searchParams.has('compose');
        const message = hasFilter
            ? 'Delete all stopped containers across all composes (filters not applied)?'
            : 'Delete all stopped containers?';
        openModal('/container/api/prune', 'POST', message, '/container/list');
    });
});