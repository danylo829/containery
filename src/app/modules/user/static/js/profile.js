const slim = new SlimSelect({
    select: '#theme-select',
    settings: {
        showSearch: false,
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
        }
    }
});

const row = document.getElementById('glass-custom-url-row');
const sel = document.getElementById('glass-bg-select');
const toggle = document.getElementById('glassmorphism-toggle');
const bgRow = sel?.closest('tr');

function updateVisibility() {
    const glassOn = toggle?.checked;
    const isCustom = sel?.value === 'custom';

    if (bgRow) bgRow.style.display = glassOn ? '' : 'none';
    if (row) row.style.display = (glassOn && isCustom) ? '' : 'none';
}

toggle?.addEventListener('change', updateVisibility);
sel?.addEventListener('change', updateVisibility);

updateVisibility();