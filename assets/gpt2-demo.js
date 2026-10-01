const loadButton = document.getElementById('gpt-load');
const status = document.getElementById('gpt-status');
const messages = document.getElementById('gpt-messages');
const form = document.getElementById('gpt-form');
const input = document.getElementById('gpt-input');
const sendButton = document.getElementById('gpt-send');
const clearButton = document.getElementById('gpt-clear');

let worker = null;
let ready = false;
let busy = false;
let history = [];

function setControls() {
  loadButton.disabled = worker !== null;
  input.disabled = !ready || busy;
  sendButton.disabled = !ready || busy;
  clearButton.disabled = !ready || busy || history.length === 0;
}

function addMessage(role, text) {
  const item = document.createElement('div');
  item.className = `gpt-message ${role}`;
  const label = document.createElement('strong');
  label.textContent = role === 'user' ? 'You' : 'GPT-2';
  const body = document.createElement('span');
  body.textContent = text;
  item.append(label, body);
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
}

function resetWorker(message) {
  worker?.terminate();
  worker = null;
  ready = false;
  busy = false;
  status.textContent = message;
  loadButton.textContent = 'Retry loading GPT-2';
  setControls();
}

loadButton.addEventListener('click', () => {
  if (worker) return;
  status.textContent = 'Starting model download…';
  loadButton.textContent = 'Loading GPT-2…';
  try {
    worker = new Worker(new URL('./gpt2-worker.js', import.meta.url), { type: 'module' });
    worker.onmessage = ({ data }) => {
      if (data.type === 'progress') {
        status.textContent = `Downloading GPT-2: ${data.percent}%`;
      } else if (data.type === 'ready') {
        ready = true;
        status.textContent = 'GPT-2 is ready. Send a message.';
        loadButton.textContent = 'GPT-2 loaded';
        setControls();
        input.focus();
      } else if (data.type === 'result') {
        busy = false;
        const reply = data.text.trim();
        if (reply) {
          history.push({ role: 'model', text: reply });
          addMessage('model', reply);
          status.textContent = 'Ready for another message.';
        } else {
          status.textContent = 'GPT-2 produced no reply. Try a different message.';
        }
        setControls();
        input.focus();
      } else if (data.type === 'error') {
        if (data.stage === 'load') {
          resetWorker('Could not load GPT-2. Check your connection and try again.');
        } else {
          busy = false;
          status.textContent = 'Could not generate a reply. Try another message.';
          setControls();
        }
      }
    };
    worker.onerror = () => resetWorker('Could not load GPT-2. Check your connection and try again.');
    worker.postMessage({ type: 'load' });
    setControls();
  } catch {
    resetWorker('This browser could not start the GPT-2 demo.');
  }
});

form.addEventListener('submit', (event) => {
  event.preventDefault();
  if (!ready || busy) return;
  const text = input.value.trim();
  if (!text) return;
  history.push({ role: 'user', text });
  addMessage('user', text);
  input.value = '';
  busy = true;
  status.textContent = 'GPT-2 is writing…';
  setControls();
  const transcript = history.slice(-4)
    .map((turn) => `${turn.role === 'user' ? 'Human' : 'Assistant'}: ${turn.text}`)
    .join('\n');
  const prompt = `The following is a conversation.\n${transcript.slice(-900)}\nAssistant:`;
  worker.postMessage({ type: 'generate', prompt });
});

clearButton.addEventListener('click', () => {
  history = [];
  messages.replaceChildren();
  status.textContent = 'Conversation cleared. GPT-2 is ready.';
  setControls();
  input.focus();
});

setControls();
