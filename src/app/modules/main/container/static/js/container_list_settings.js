let modalOpened = false;

document.querySelectorAll('.settings-btn').forEach(button => {
    button.addEventListener('click', function() {
        openDraggableListModal();
    });
});

async function openDraggableListModal() {
    const url = '/container/list/settings';
    const method = 'GET';

    const spinner = document.querySelector('.loading-spinner');
    const disable_on_load = document.querySelector('.disable-on-load');

    spinner.classList.remove('hidden');

    if (disable_on_load) {
        disable_on_load.classList.add('disabled');
    }

    const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .catch(error => handleError(error));

    if (response.ok) {
        const html = await response.text();
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        const modalContent = tempDiv.querySelector('#containerListSettingsModal');
        document.body.appendChild(modalContent);
        
        const draggableList = modalContent.querySelector('.draggable-list');
        enableHorizontalDrag(draggableList);
        
        const saveBtn = modalContent.querySelector('.btn.confirm');
        saveBtn.addEventListener('click', () => {
            const colomns = Array.from(draggableList.querySelectorAll('.item')).map(item => ({
                name: item.querySelector('span').textContent,
                enabled: item.querySelector('input').checked
            }));
            const quick_actions = Array.from(modalContent.querySelectorAll('.quick-action-item input')).map(input => ({
                name: input.dataset.action,
                enabled: input.checked,
                url: input.dataset.url || false
            }));


            const data = {
                columns: colomns,
                quick_actions: quick_actions
            };
            
            fetch('/container/list/settings', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => handleResponse(response))
            .catch(error => handleError(error));
        });

        const cancelBtn = modalContent.querySelector('.btn.cancel');
        cancelBtn.addEventListener('click', closeDraggableListModal);

        window.addEventListener('click', function (event) {
            if (event.target === modalContent) closeDraggableListModal();
        });

        spinner.classList.add('hidden');

        if (disable_on_load) {
            disable_on_load.classList.remove('disabled');
        }
    } else {
        handleError(new Error('Failed to fetch modal content'));
    }

    modalOpened = true;
}

function closeDraggableListModal() {
    const modal = document.getElementById('containerListSettingsModal');
    if (modal) {
        modal.classList.add('closing');
        modal.addEventListener('animationend', () => {
            modal.remove();
        }, { once: true });
    }
    modalOpened = false;
}

// === drag logic ===
function enableHorizontalDrag(container) {
    let draggingEl = null;

    container.addEventListener('dragstart', e => {
        if (!e.target.classList.contains('item')) return;
        draggingEl = e.target;
        draggingEl.style.opacity = '0.5';
    });

    container.addEventListener('dragend', () => {
        if (draggingEl) draggingEl.style.opacity = '1';
        draggingEl = null;
    });

    container.addEventListener('dragover', e => {
        e.preventDefault();
        const afterElement = getDragAfterElement(container, e.clientX);
        if (!draggingEl) return;
        if (afterElement == null) container.appendChild(draggingEl);
        else container.insertBefore(draggingEl, afterElement);
    });

    function getDragAfterElement(container, x) {
        const draggableElements = [...container.querySelectorAll('.item:not([style*="opacity: 0.5"])')];
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = x - box.left - box.width / 2;
            if (offset < 0 && offset > closest.offset) return { offset, element: child };
            else return closest;
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
}

document.addEventListener('keydown', e => {
    if (e.key === 'm' && !modalOpened) openDraggableListModal();
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && modalOpened) closeDraggableListModal();
});
