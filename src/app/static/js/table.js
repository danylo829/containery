function updateUrlParams(params) {
    const url = new URL(window.location.href);
    for (const [key, value] of Object.entries(params)) {
        if (value === null || value === '') {
            url.searchParams.delete(key);
        } else {
            url.searchParams.set(key, value);
        }
    }
    window.location.href = url.toString();
}



function initServerSideTable(tableElement) {
    // Set initial sort direction based on URL
    const urlParams = new URLSearchParams(window.location.search);
    const currentSortCol = urlParams.get('sort_col');
    const currentSortDir = urlParams.get('sort_dir');
    
    const headers = tableElement.querySelectorAll('th[data-sort]');
    headers.forEach(th => {
        const sortKey = th.getAttribute('data-sort');
        if (sortKey === currentSortCol) {
            th.classList.add(currentSortDir === 'desc' ? 'descending' : 'ascending');
        }
        
        th.addEventListener('click', function() {
            const isAscending = th.classList.contains('ascending');
            const newSortDir = isAscending ? 'desc' : 'asc';
            
            updateUrlParams({
                sort_col: sortKey,
                sort_dir: newSortDir,
                page: 1 // reset to page 1 on sort
            });
        });
    });

    // Check if table is empty
    const tbody = tableElement.querySelector('tbody');
    if (tbody && tbody.children.length === 0) {
        let noRowsMessage = document.createElement('tr');
        noRowsMessage.id = 'no-rows-message';
        noRowsMessage.innerHTML = `<td colspan="100%" style="text-align: center; padding: 20px;"><p>No matching records found</p></td>`;
        tbody.appendChild(noRowsMessage);
    }
}

function initClientSideTable(tableElement) {
    const headers = tableElement.querySelectorAll('th[data-sort]');
    headers.forEach(th => {
        th.addEventListener('click', function() {
            const tbody = tableElement.querySelector('tbody');
            if (!tbody) return;
            const rows = Array.from(tbody.querySelectorAll('tr:not(#no-rows-message)'));
            const index = Array.from(th.parentNode.children).indexOf(th);
            const isAscending = th.classList.contains('ascending');

            // Remove sorting indicators from all columns
            headers.forEach(otherTh => {
                otherTh.classList.remove('ascending', 'descending');
            });

            // Toggle ascending/descending classes on the clicked column
            if (isAscending) {
                th.classList.remove('ascending');
                th.classList.add('descending');
            } else {
                th.classList.remove('descending');
                th.classList.add('ascending');
            }

            const sortAscending = th.classList.contains('ascending');

            // Sort rows based on the selected column
            rows.sort((a, b) => {
                const cellA = a.children[index] ? a.children[index].textContent.trim() : '';
                const cellB = b.children[index] ? b.children[index].textContent.trim() : '';

                if (cellA !== '' && cellB !== '' && !isNaN(cellA) && !isNaN(cellB)) {
                    return sortAscending ? cellA - cellB : cellB - cellA;
                }

                return sortAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });

            // Re-append rows to the tbody in the new order
            rows.forEach(row => tbody.appendChild(row));
            
            const noRowsMessage = tbody.querySelector('#no-rows-message');
            if (noRowsMessage) {
                tbody.appendChild(noRowsMessage);
            }
        });
    });

    // Handle search field client-side
    const searchField = document.getElementById('search');
    const searchReset = document.getElementById('search-reset');

    if (searchField) {
        searchField.addEventListener('input', function() {
            const searchValue = this.value.toLowerCase();
            const tbody = tableElement.querySelector('tbody');
            if (!tbody) return;
            const rows = tbody.querySelectorAll('tr:not(#no-rows-message)');
            let visibleRowCount = 0;

            rows.forEach(row => {
                let match = false;
                Array.from(row.cells).forEach(cell => {
                    if (cell.textContent.toLowerCase().includes(searchValue)) {
                        match = true;
                    }
                });

                if (match) {
                    row.style.display = '';
                    visibleRowCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            let noRowsMessage = tbody.querySelector('#no-rows-message');
            if (visibleRowCount === 0) {
                if (!noRowsMessage) {
                    noRowsMessage = document.createElement('tr');
                    noRowsMessage.id = 'no-rows-message';
                    noRowsMessage.innerHTML = `<td colspan="100%" style="text-align: center; padding: 20px;"><p>No matching records found</p></td>`;
                    tbody.appendChild(noRowsMessage);
                }
                noRowsMessage.style.display = '';
            } else if (noRowsMessage) {
                noRowsMessage.style.display = 'none';
            }
        });

        if (searchReset) {
            searchReset.addEventListener('click', function() {
                searchField.value = '';
                searchField.dispatchEvent(new Event('input'));
            });
        }
    }
}

// Initialize tables
const serverSideTable = document.querySelector('table[data-total-pages]');
if (serverSideTable) {
    initServerSideTable(serverSideTable);

    // Handle search field server-side
    const searchField = document.getElementById('search');
    const searchReset = document.getElementById('search-reset');

    if (searchField) {
        const urlParams = new URLSearchParams(window.location.search);
        const currentSearch = urlParams.get('search');
        if (currentSearch) {
            searchField.value = currentSearch;
        }

        let searchTimeout = null;
        searchField.addEventListener('input', function() {
            const val = this.value;
            if (searchTimeout) clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                updateUrlParams({ search: val, page: 1 });
            }, 500);
        });

        if (searchReset) {
            searchReset.addEventListener('click', function() {
                searchField.value = '';
                updateUrlParams({ search: '', page: 1 });
            });
        }
    }
} else {
    document.querySelectorAll('table').forEach(table => {
        initClientSideTable(table);
    });
}