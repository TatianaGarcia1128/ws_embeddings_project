// Connect to WebSocket server
const socket = new WebSocket('ws://127.0.0.1:8000/message');

// Event handler for WebSocket open
socket.onopen = function(event) {
    console.log('WebSocket connection established.');
};

// Event handler for WebSocket messages received
socket.onmessage = function(event) {
    const message = event.data;
    displayMessage(message);
};

// Function to display a message in the chat box
function displayMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
}

// Event listener for send button click
document.getElementById('send-button').addEventListener('click', function() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;
    // Verificar si el estado del WebSocket es OPEN antes de intentar enviar el mensaje
    if (socket.readyState === WebSocket.OPEN) {
        // Verificar si el mensaje no está vacío
        if (message.trim() !== '') {
            // Enviar el mensaje a través del WebSocket
            socket.send(message);

            // Limpiar el input de mensaje después de enviarlo
            messageInput.value = '';
        }
    } else {
        console.error('WebSocket is not open yet.');
    }
});

// Event listener for pressing Enter key in the message input field
document.getElementById('message-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        document.getElementById('send-button').click();
    }
});

document.getElementById("file-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append("file", document.getElementById("file-input").files[0]);

    try {
        const response = await fetch("/file", {
            method: "POST",
            body: formData
        });
        
        const data = await response.json();
        if (response.ok) {
            showMessage("File saved successfully!");
        } else {
            showMessage("Error saving file: " + data.detail);
        }
    } catch (error) {
        showMessage("Error: " + error.message);
    }
});

function showMessage(message) {
    document.getElementById("message").innerText = message;
}