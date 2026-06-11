initFilters([
    { selector: '#docker_host', paramName: 'docker_host', placeholder: 'Filter by docker host' }
]);

document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = new URL(window.location);
        const api_url = '/image/api/prune' + url.search;
        openModal(api_url, 'POST', 'Are you sure you want to delete all unused images?', '/image/list');
    });
});
