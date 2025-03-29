const ws = new WebSocket('ws://localhost:8000/ws/websocket');
const messagesDiv = document.getElementById('chat-messages');
const messageInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-button');

ws.onopen = () => {
	ws.send('SUBSCRIBE destination:/topic/chat'); // TODO
};

ws.onmessage = (event) => {
	console.log(event);
	const data = parseMsg(event.data);
	if (data.type === 'Message') {
		console.log(data)
		console.log(data.data)
		console.log(data.data.message)
		for (let msg of data.data) {
			appendMessage(msg.message);
		}
	}
};

sendBtn.onclick = () => {
	const message = messageInput.value.trim();
	if (message) {
		const msg = {
			content: message,
		};
		sendMessage(JSON.stringify(msg));
		messageInput.value = '';
	}
};

function appendMessage(msg) {
	const messageDiv = document.createElement('div');
	messageDiv.className = 'message';

	messageDiv.classList.add(msg.username == "user" ? 'user-message' : 'bot-message');
	messageDiv.textContent = msg.content
	messagesDiv.appendChild(messageDiv);
	messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function sendMessage(msg) {
	fetch("http://localhost:8000/send/chat", {
		method: "POST",
		body: msg,
		headers: {
			"Content-type": "application/json; charset=UTF-8"
		}
	});
}

function parseMsg(data) {
	console.log(data)
	if (data.startsWith("SEND")) {
		start = data.indexOf("\n\n")
		if (start == -1) {
			return {'type': 'Error'}
		}
		start += 2 

		end = data.indexOf("\x00")
		if (end == -1) {
			return {'type': 'Error'}
		}

		msg=  data.substring(start, end);
		return {'type': 'Message', 'data': JSON.parse(msg)};
	}

	return {'type': 'Not implemented'}
}

document.addEventListener('DOMContentLoaded', function() {
	const sidebarToggle = document.getElementById('sidebar-toggle');
	const sidebarPanel = document.getElementById('sidebar-panel');
	const closeSidebar = document.getElementById('close-sidebar');

	sidebarToggle.addEventListener('click', () => {
		sidebarPanel.classList.toggle('open');
	});

	closeSidebar.addEventListener('click', () => {
		sidebarPanel.classList.remove('open');
	});
});

