document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        openModal(`/container/api/${id}/delete`, 'DELETE', 'Are you sure you want to delete this container?', '/container/list');
    });
});

document.querySelectorAll('.start-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');

        spinner.classList.remove('hidden');

        disableAllActions();

        fetch(`/container/api/${containerId}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response))
        .catch(error => handleError(error));
    });
});

document.querySelectorAll('.restart-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');

        spinner.classList.remove('hidden');

        disableAllActions();

        fetch(`/container/api/${containerId}/restart`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response))
        .catch(error => handleError(error));
    });
});

document.querySelectorAll('.stop-btn').forEach(button => {
    button.addEventListener('click', function() {
        const containerId = this.getAttribute('data-id');

        spinner.classList.remove('hidden');

        disableAllActions();

        fetch(`/container/api/${containerId}/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response))
        .catch(error => handleError(error));
    });
});