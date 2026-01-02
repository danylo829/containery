const flashMessage = localStorage.getItem('flash_message');
const flashType = localStorage.getItem('flash_type');

if (flashMessage) {
    showFlashMessage(flashMessage, flashType);
}

function showFlashMessage(message, type) {
    let flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
        flashContainer = document.createElement('div');
        flashContainer.className = 'flash-messages';
        document.body.appendChild(flashContainer);
    }

    const flashElement = document.createElement('div');
    flashElement.className = `flash-message ${type}`;
    flashElement.textContent = message;

    flashContainer.appendChild(flashElement);

    localStorage.removeItem('flash_message');
    localStorage.removeItem('flash_type');

    setTimeout(() => {
        flashElement.remove();
    }, 10000);
}