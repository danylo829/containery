const textarea = document.getElementById('log-textarea');
const logInput = document.getElementById('log-lines');

attachFilter('#stream', 'stream', 'Filter by docker host');

if (textarea) {
	textarea.scrollTop = textarea.scrollHeight;
}

logInput.addEventListener('blur', () => {
  const value = logInput.value.trim();
  if (value) {
    const url = new URL(window.location.href);
    url.searchParams.set('tail', value);
    window.location.href = url.toString();
  }
});

logInput.addEventListener('keyup', e => {
  if (e.key === 'Enter') logInput.blur();
});