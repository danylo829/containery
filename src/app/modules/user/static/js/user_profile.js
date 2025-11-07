const deleteButton = document.getElementById('delete-btn');

const roleList = document.querySelector('.role-list');
const userId = roleList.getAttribute('data-user-id');

const slim = new SlimSelect({
    select: '#role-select',
    settings: {
        showSearch: false,
    }
});

deleteButton.addEventListener('click', function () {
    const id = this.getAttribute('data-id');
    openModal(`user/delete?id=${id}`, 'DELETE', 'Are you sure you want to delete this user?', 'user/list');
});

document.querySelectorAll('.delete-role').forEach(button => {
    button.addEventListener('click', function() {
        const roleId = this.getAttribute('data-role-id');

        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('role_id', roleId);

        fetch('/user/role/remove', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json'
            },
            body: formData
        })
        .then(response => {
            if (response.ok) {
                localStorage.setItem('flash_message', 'Role deleted successfully!');
                localStorage.setItem('flash_type', 'success');
                window.location.reload();
            } else if (response.status === 403) {
                localStorage.setItem('flash_message', 'You do not have permission to perform this action.');
                localStorage.setItem('flash_type', 'error');
            } else {
                localStorage.setItem('flash_message', 'Failed to delete the role.');
                localStorage.setItem('flash_type', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            localStorage.setItem('flash_message', 'An error occurred.');
            localStorage.setItem('flash_type', 'error');
        })
        .finally(() => {
            window.location.reload();
        });
    });
});