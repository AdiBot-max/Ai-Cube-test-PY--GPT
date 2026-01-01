const input = document.getElementById("input");
const messages = document.getElementById("messages");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = role.toLowerCase(); // add class: 'you' or 'bot'
  div.textContent = role + ": " + text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight; // auto scroll
}

async function sendMessage(text) {
  if (!text.trim()) return; // ignore empty messages
  addMessage("You", text);
  input.disabled = true;

  const botPlaceholder = document.createElement("div");
  botPlaceholder.className = "bot";
  botPlaceholder.textContent = "Bot: typing...";
  messages.appendChild(botPlaceholder);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();
    botPlaceholder.textContent = "Bot: " + data.reply;
  } catch (err) {
    botPlaceholder.textContent = "Bot: [Error connecting to server]";
    console.error(err);
  } finally {
    input.value = "";
    input.disabled = false;
    input.focus();
    messages.scrollTop = messages.scrollHeight;
  }
}

// handle Enter key
input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage(input.value);
});
