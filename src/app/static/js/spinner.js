const spinnerElement = document.querySelector('.loading-spinner');
let hideSpinnerTimeoutId = null;

function showSpinner() {
    if (!spinnerElement) return;

    if (hideSpinnerTimeoutId) {
        clearTimeout(hideSpinnerTimeoutId);
        hideSpinnerTimeoutId = null;
    }

    spinnerElement.classList.add('spinning');
    spinnerElement.classList.remove('hidden');
}

function hideSpinner() {
    if (!spinnerElement) return;

    spinnerElement.classList.add('hidden');

    if (hideSpinnerTimeoutId) {
        clearTimeout(hideSpinnerTimeoutId);
    }

    hideSpinnerTimeoutId = setTimeout(() => {
        spinnerElement.classList.remove('spinning');
        hideSpinnerTimeoutId = null;
    }, 300);
}

window.showSpinner = showSpinner;
window.hideSpinner = hideSpinner;