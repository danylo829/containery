if (typeof SlimSelect !== 'undefined') {
    attachFilter('#compose', 'compose', 'Filter by compose');
    attachFilter('#docker_host', 'docker_host', 'Filter by docker host');
}

document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = new URL(window.location);
        const hasComposeFilter = url.searchParams.has('compose');
        const hasDockerHostFilter = url.searchParams.has('docker_host');
        
        let message = 'Delete all stopped containers?';
        
        if (hasDockerHostFilter) {
            message = 'Delete all stopped containers on selected hosts?';
        }
        
        let secondaryText = null;
        if (hasComposeFilter) {
            secondaryText = 'Note: Compose filter is not applied.';
        }
        
        // Pass current query parameters to the API
        const api_url = '/container/api/prune' + url.search;
        openModal(api_url, 'POST', message, '/container/list', secondaryText);
    });
});