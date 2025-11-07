const form = document.getElementById('start-form');
const terminalWrapper = document.getElementById('terminal-wrapper');
const container = document.getElementById('terminal-container');
const xterm = new Terminal();
const commandSelect = document.getElementById('command-select');
const commandInput = document.getElementById('command-input');
const submitBtn = document.getElementById('submit-btn');

const slim = new SlimSelect({
    select: '#command-select',
    settings: {
        showSearch: false,
    }
});

const charWidth = 9 + 0.2; //a small offset so vertical scroll slider does not overlap text
const charHeight = 17;

let socket;
let execId;

function getContainerSize() {
    const { width, height } = container.getBoundingClientRect();

    const cols = Math.floor(width / charWidth);

    const rows = Math.floor(height / charHeight);

    return { cols, rows };
}

const resizeTerminalObserver = new ResizeObserver(entries => {
    for (let entry of entries) {
        if (!execId) {
            return;
        }
        const { cols, rows } = getContainerSize();

        socket.emit('resize_session', {
            exec_id: execId,
            cols: cols,
            rows: rows
        });

        xterm.resize(cols, rows);
    }
});

// Disable select when there is any input in custom command
commandInput.addEventListener('input', function () {
    if (commandInput.value.length > 0) {
        commandSelect.disabled = true;
    } else {
        commandSelect.disabled = false;
    }
});

form.addEventListener('submit', (event) => {
    event.preventDefault();

    resizeTerminalObserver.observe(container);

    const user = document.getElementById('user-field').value;
    const containerId = submitBtn.getAttribute('data-container-id');

    const command = commandInput.value.length > 0 ? commandInput.value : commandSelect.value;

    form.style.display = 'none';
    terminalWrapper.style.display = 'block';

    xterm.open(container);

    socket = io();

    const { cols, rows } = getContainerSize();

    socket.emit('start_session', {
        container_id: containerId,
        user: user,
        command: command,
        consoleSize: [rows, cols]
    });

    xterm.resize(cols, rows);

    xterm.onData(e => {
        socket.emit('input', {
            command: e
        });
    });

    socket.on('output', function(data) {
        const output = data.data;
        xterm.write(output);
    });

    socket.on('exec_id', function(data) {
        execId = data.execId;
    });
});
