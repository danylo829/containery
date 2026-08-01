let modalOpened = false;

document.querySelectorAll('.settings-btn').forEach(button => {
    button.addEventListener('click', function() {
        openDraggableListModal();
    });
});

async function openDraggableListModal() {
    if (modalOpened) return;
    modalOpened = true;
    
    const url = '/container/list/settings';
    const method = 'GET';

    const disable_on_load = document.querySelector('.disable-on-load');

    showSpinner();

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

        hideSpinner();

        if (disable_on_load) {
            disable_on_load.classList.remove('disabled');
        }
    } else {
        handleError(new Error('Failed to fetch modal content'));
    }
}

function closeDraggableListModal() {
    const modal = document.getElementById('containerListSettingsModal');
    if (modal) {
        modal.classList.add('closing');
        modal.addEventListener('animationend', () => {
            modal.remove();
            modalOpened = false;
        }, { once: true });
    }
}

// === drag logic ===
function enableHorizontalDrag(container) {
    if (!container) return;
    if (typeof Sortable !== 'undefined') {
        Sortable.create(container, {
            animation: 150,
            direction: 'horizontal',
            draggable: '.item',
            filter: 'input, label',
            preventOnFilter: false,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag'
        });
    }
}

document.addEventListener('keydown', e => {
    if (e.key === 'm' && !modalOpened) openDraggableListModal();
});

document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && modalOpened) closeDraggableListModal();
});
