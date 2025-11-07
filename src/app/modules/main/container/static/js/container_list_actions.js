if (typeof SlimSelect !== 'undefined') {
    const slim = new SlimSelect({
        select: '#compose',
        settings: {
            showSearch: true,
            placeholderText: 'Filter by compose',
        },
        events: {
            afterChange: (newVal) => {
                const values = newVal.map(v => v.value).join(',') || '';
                const url = new URL(window.location);
                if (values) {
                    url.searchParams.set('compose', values);
                } else {
                    url.searchParams.delete('compose');
                }
                window.location = url.toString();
            }
        }
    });
}

document.querySelectorAll('.prune-btn').forEach(button => {
    button.addEventListener('click', function() {
        const url = new URL(window.location);
        const hasFilter = url.searchParams.has('compose');
        const message = hasFilter
            ? 'Delete all stopped containers across all composes (filters not applied)?'
            : 'Delete all stopped containers?';
        openModal('/container/api/prune', 'POST', message, '/container/list');
    });
});