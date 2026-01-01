const input = document.getElementById("input");
const messages = document.getElementById("messages");

function add(role, text) {
  const d = document.createElement("div");
  d.textContent = role + ": " + text;
  messages.appendChild(d);
}

input.addEventListener("keydown", async e => {
  if (e.key !== "Enter") return;

  add("You", input.value);

  const res = await fetch("/chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ message: input.value })
  });

  const data = await res.json();
  add("Bot", data.reply);
  input.value = "";
});
