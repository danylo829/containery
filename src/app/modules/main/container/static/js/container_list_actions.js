if (typeof SlimSelect !== 'undefined') {
    const url = new URL(window.location);
    let redirect = false;

    ['compose', 'docker_host'].forEach(paramName => {
        const urlVal = url.searchParams.get(paramName);
        const lsVal = localStorage.getItem(paramName + '_filter');

        if (urlVal !== null) {
            localStorage.setItem(paramName + '_filter', urlVal);
        } else if (lsVal) {
            url.searchParams.set(paramName, lsVal);
            redirect = true;
        }
    });

    if (redirect) {
        window.location.replace(url.toString());
    } else {
        attachFilter('#compose', 'compose', 'Filter by compose');
        attachFilter('#docker_host', 'docker_host', 'Filter by docker host');
    }
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

document.querySelectorAll('.clear-filters-btn').forEach(button => {
    button.addEventListener('click', () => {
        localStorage.removeItem('compose_filter');
        localStorage.removeItem('docker_host_filter');
        window.location.href = window.location.pathname;
    });
});