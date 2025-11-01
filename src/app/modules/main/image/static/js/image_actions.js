document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        openModal(`/image/api/${id}/delete`, 'DELETE', 'Are you sure you want to delete this image?', '/image/list');
    });
});