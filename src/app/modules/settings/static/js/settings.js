// Docker Hosts Management
document.querySelectorAll('.status').forEach(statusElem => {
    const id = statusElem.getAttribute('data-id');
    const versionSpan = document.getElementById(`version-${id}`);

    spinner.classList.remove('hidden');
    disableAllActions();

    fetch(`/settings/docker-hosts/check/${id}`)
    .then(async response => {
        if (response.status === 200) {
            const data = await response.json();
            
            statusElem.classList.remove('unknown', 'offline');
            statusElem.textContent = 'Online';
            statusElem.classList.add('online');
            
            if (versionSpan) {
                versionSpan.textContent = `v${data.version}`;
            }
        } else {
            statusElem.classList.remove('unknown', 'online');
            statusElem.textContent = 'Offline';
            statusElem.classList.add('offline');
        }
    })
    .catch(() => {
        statusElem.textContent = 'Unknown';
        statusElem.classList.remove('unknown', 'online', 'offline');
        statusElem.classList.add('unknown');
    }).finally(() => {
        spinner.classList.add('hidden');
        enableAllActions();
    });
});

document.querySelectorAll('.url-input').forEach(input => {
    input.addEventListener('change', function() {
        const id = this.getAttribute('data-id');
        const url = this.value;

        if (!url) return;

        spinner.classList.remove('hidden');
        disableAllActions();

        fetch(`/settings/docker-hosts/edit/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                url: url
            })
        })
        .then(response => handleResponse(response))
        .catch(error => handleError(error))
    });
});

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

// Settings
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

// Test Connection
const testConnectionBtn = document.getElementById('test-connection-btn');
if (testConnectionBtn) {
    testConnectionBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        const urlInput = document.getElementById('docker-host-url');
        const url = urlInput.value;

        if (!url) {
            showFlashMessage('Please enter a URL first.', 'error');
            return;
        }

        spinner.classList.remove('hidden');
        disableAllActions();

        // Wait a bit for UI update
        await sleep(500);

        fetch('/settings/docker-hosts/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                url: url
            })
        })
        .then(response => {
             if (response.ok) {
                return response.json().then(data => {
                    showFlashMessage(`Success: ${data.message} (v${data.version})`, 'success');
                });
             } else {
                 return response.json().then(data => {
                     showFlashMessage(`Error: ${data.message}`, 'error');
                 });
             }
        })
        .catch(error => {
            showFlashMessage('An error occurred.', 'error');
            console.error(error);
        })
        .finally(() => {
            spinner.classList.add('hidden');
            enableAllActions();
        });
    });
}