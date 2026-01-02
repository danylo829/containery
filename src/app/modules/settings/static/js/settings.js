document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        openModal(`/settings/docker-hosts/delete/${id}`, 'POST', 'Are you sure you want to delete this docker host?', '/settings/docker-hosts');
    });
});

document.querySelectorAll('.enable-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', async function() {
        const id = this.getAttribute('data-id');
        const isEnabled = this.checked;

        spinner.classList.remove('hidden');
        disableAllActions();

        // Wait to finish checkbox animation
        await sleep(500); 

        fetch(`/settings/docker-hosts/edit/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                enabled: isEnabled
            })
        })
        .then(response => handleResponse(response))
        .catch(error => handleError(error))
    });
});

function resetSetting(fieldName) {
    spinner.classList.remove('hidden');
    disableAllActions();

    fetch('/settings/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            field_name: fieldName
        })
    })
    .then(response => handleResponse(response))
    .catch(error => handleError(error))
}
