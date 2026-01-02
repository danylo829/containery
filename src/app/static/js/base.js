const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
const spinner = document.querySelector('.loading-spinner');

function handleResponse(response, returnUrl) {
    if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            response.json().then(data => {
                if (data && data.message) {
                    localStorage.setItem('flash_message', data.message);
                }
            });
        } else {
            localStorage.setItem('flash_message',  'Success!');
        }
        localStorage.setItem('flash_type', 'success');
        if (returnUrl) {
            window.location.href = returnUrl;
            return;
        }
    } else if (response.status === 403) {
        localStorage.setItem('flash_message', 'You do not have permission to perform this action.');
        localStorage.setItem('flash_type', 'error');
    } else {
        localStorage.setItem('flash_message', 'Failed to perform action.');
        localStorage.setItem('flash_type', 'error');
    }
    
    window.location.reload();
}

function handleError(error) {
    localStorage.setItem('flash_message', `An error occurred: ${error}`);
    localStorage.setItem('flash_type', 'error');
    window.location.reload();
}

document.querySelector('#user-icon').addEventListener('click', function() {
    document.querySelector('.user-panel').classList.toggle('open');
});

const refresh_btn = document.getElementById('refresh-page-btn');
if (refresh_btn != null) {
    refresh_btn.addEventListener('click', function() {
        location.reload();
    });
}

function disableAllActions() {
    const disable_on_load = document.querySelectorAll('.disable-on-load');
    disable_on_load.forEach(element => {
        element.classList.add('disabled');
        element.setAttribute('disabled', 'disabled');
    });
}

function enableAllActions() {
    const disable_on_load = document.querySelectorAll('.disable-on-load');
    disable_on_load.forEach(element => {
        element.classList.remove('disabled');
        element.removeAttribute('disabled');
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const attachFilter = (selector, paramName, placeholder, search) => {
    if (!document.querySelector(selector)) return;

    new SlimSelect({
        select: selector,
        settings: {
            showSearch: search || false,
            placeholderText: placeholder,
        },
        events: {
            afterChange: async (newVal) => {
                const values = newVal.map(v => v.value).join(',');
                const url = new URL(window.location);
                
                if (values) {
                    url.searchParams.set(paramName, values);
                } else {
                    url.searchParams.delete(paramName);
                }
                
                // Wait to finish select animation
                await sleep(200); 
                window.location = url.toString();
            }
        }
    });
};