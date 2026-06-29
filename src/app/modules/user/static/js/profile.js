const settingsForm = document.getElementById('settings-form');
const settingsSubmitBtn = settingsForm?.querySelector('.settings-form-submit');

function submitSettingsForm() {
    if (settingsSubmitBtn) {
        settingsSubmitBtn.click();
    }
}

let isInitialized = false;

const slim = new SlimSelect({
    select: '#theme-select',
    settings: {
        showSearch: false,
    },
    events: {
        afterChange: function () {
            if (isInitialized) {
                submitSettingsForm();
            }
        }
    }
});

const slimBg = new SlimSelect({
    select: '#glass-bg-select',
    settings: {
        showSearch: false,
    },
    events: {
        afterChange: function (newVal) {
            var row = document.getElementById('glass-custom-url-row');
            if (row) row.style.display = newVal[0].value === 'custom' ? '' : 'none';
            if (isInitialized) {
                submitSettingsForm();
            }
        }
    }
});

const row = document.getElementById('glass-custom-url-row');
const sel = document.getElementById('glass-bg-select');
const toggle = document.getElementById('glassmorphism-toggle');
const bgUrlInput = document.getElementById('glass-bg-url');

function updateVisibility() {
    const glassOn = toggle?.checked;
    const isCustom = sel?.value === 'custom';

    if (glassOn) {
        slimBg.enable();
        if (bgUrlInput) bgUrlInput.disabled = false;
    } else {
        slimBg.disable();
        if (bgUrlInput) bgUrlInput.disabled = true;
    }

    if (row) {
        row.style.display = isCustom ? '' : 'none';
    }
}

toggle?.addEventListener('change', () => {
    updateVisibility();
    if (isInitialized) {
        submitSettingsForm();
    }
});

sel?.addEventListener('change', () => {
    if (isInitialized) {
        submitSettingsForm();
    }
});

if (bgUrlInput) {
    bgUrlInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            if (isInitialized) {
                submitSettingsForm();
            }
        }
    });
    bgUrlInput.addEventListener('blur', () => {
        if (isInitialized) {
            submitSettingsForm();
        }
    });
}

updateVisibility();
isInitialized = true;

// Edit Profile Modal logic
const editProfileModal = document.getElementById('edit-profile-modal');
const openEditProfileBtn = document.getElementById('open-edit-profile-btn');
const closeEditProfileModalBtn = document.getElementById('close-edit-profile-modal');
const cancelEditProfileBtn = document.getElementById('cancel-edit-profile');

function openEditProfileModal() {
    if (editProfileModal) {
        editProfileModal.style.display = 'flex';
        editProfileModal.classList.remove('closing');
    }
}

function closeEditProfileModal() {
    if (editProfileModal) {
        editProfileModal.classList.add('closing');
        editProfileModal.addEventListener('animationend', () => {
            editProfileModal.style.display = 'none';
            editProfileModal.classList.remove('closing');
        }, { once: true });
    }
}

if (openEditProfileBtn) {
    openEditProfileBtn.addEventListener('click', openEditProfileModal);
}

if (closeEditProfileModalBtn) {
    closeEditProfileModalBtn.addEventListener('click', closeEditProfileModal);
}

if (cancelEditProfileBtn) {
    cancelEditProfileBtn.addEventListener('click', closeEditProfileModal);
}

window.addEventListener('click', (event) => {
    if (event.target === editProfileModal) {
        closeEditProfileModal();
    }
});

if (editProfileModal && editProfileModal.classList.contains('has-errors')) {
    editProfileModal.style.display = 'flex';
}