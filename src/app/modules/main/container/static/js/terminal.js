const form = document.getElementById('start-form');
const terminalWrapper = document.getElementById('terminal-wrapper');
const container = document.getElementById('terminal-container');
const commandSelect = document.getElementById('command-select');
const commandInput = document.getElementById('command-input');
const submitBtn = document.getElementById('submit-btn');

const xterm = new Terminal();
const fitAddon = new FitAddon.FitAddon();

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


let resizeTimeout = null;
let observerInitialized = false;
function handleResize() {
    if (!execId) return;

    xterm.write('\x1b[2J\x1b[H');
    fitAddon.fit();

    const cols = xterm.cols;
    const rows = xterm.rows;

    socket.emit('resize_session', { exec_id: execId, cols, rows });
}

const resizeTerminalObserver = new ResizeObserver(() => {
    if (!observerInitialized) {
        observerInitialized = true;
        return; // skip initial fire on .observe()
    }
    if (resizeTimeout) clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(handleResize, 100);
});

commandInput.addEventListener('input', function () {
    if (commandInput.value.length > 0) {
        commandSelect.disabled = true;
    } else {
        commandSelect.disabled = false;
    }
});

form.addEventListener('submit', (event) => {
    event.preventDefault();

    const user = document.getElementById('user-field').value;
    const containerId = submitBtn.getAttribute('data-container-id');

    const command = commandInput.value.length > 0 ? commandInput.value : commandSelect.value;

    form.style.display = 'none';
    terminalWrapper.style.display = 'block';

    xterm.loadAddon(fitAddon);
    fitAddon.fit();
    xterm.open(container);
    resizeTerminalObserver.observe(container);

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

    socket.on('disconnect', () => {
        xterm.write('\r\n\x1b[31mConnection lost.\x1b[0m\r\n');
    });
});
