function createModal() {
    const modal = document.createElement('div');
    modal.id = 'confirmationModal';
    modal.className = 'modal';

    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';

    const header = document.createElement('h2');
    header.textContent = 'Confirmation';
    header.style.textAlign = 'center';

    const question = document.createElement('p');
    question.id = 'modalQuestion';
    question.textContent = 'Are you sure you want to perform this action?';

    const secondaryText = document.createElement('p');
    secondaryText.id = 'modalSecondaryText';
    secondaryText.className = 'modal-secondary-text';

    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'button-group';

    const cancelBtn = document.createElement('button');
    cancelBtn.id = 'cancelBtn';
    cancelBtn.className = 'btn cancel';
    cancelBtn.textContent = 'Cancel';

    const confirmBtn = document.createElement('button');
    confirmBtn.id = 'confirmBtn';
    confirmBtn.className = 'btn delete';
    confirmBtn.textContent = 'Confirm';

    // Build hierarchy
    modalContent.appendChild(header);
    modalContent.appendChild(question);
    modalContent.appendChild(secondaryText);
    
    buttonGroup.appendChild(cancelBtn);
    buttonGroup.appendChild(confirmBtn);
    modalContent.appendChild(buttonGroup);

    modal.appendChild(modalContent);

    return modal;
}

function closeModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.add('closing');
        modal.addEventListener('animationend', () => {
            modal.remove();
        }, { once: true });
    }
}

function openModal(url, method, question, returnUrl, secondaryText = null) {
    const confirmationModal = createModal();
    const confirmBtn = confirmationModal.querySelector('#confirmBtn');
    const cancelBtn = confirmationModal.querySelector('#cancelBtn');
    const modalQuestion = confirmationModal.querySelector('#modalQuestion');
    const modalSecondaryText = confirmationModal.querySelector('#modalSecondaryText');

    modalQuestion.textContent = question;
    
    if (secondaryText) {
        modalSecondaryText.textContent = secondaryText;
        modalSecondaryText.style.display = 'block';
    } else {
        modalSecondaryText.style.display = 'none';
    }

    confirmBtn.addEventListener('click', function () {
        const spinner = document.querySelector('.loading-spinner');
        spinner.classList.remove('hidden');

        disableAllActions();

        closeModal();

        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => handleResponse(response, returnUrl))
        .catch(error => handleError(error));
    });

    cancelBtn.addEventListener('click', closeModal);

    window.addEventListener('click', function (event) {
        if (event.target === confirmationModal) {
            closeModal();
        }
    });

    document.body.appendChild(confirmationModal);
}