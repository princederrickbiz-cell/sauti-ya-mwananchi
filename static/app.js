const phone = "+254700000000";

const messages = document.querySelector("#messages");
const chatForm = document.querySelector("#chatForm");
const chatInput = document.querySelector("#chatInput");
const quickPrompt = document.querySelector("#quickPrompt");
const lookupForm = document.querySelector("#lookupForm");
const lookupInput = document.querySelector("#lookupInput");
const lookupOutput = document.querySelector("#lookupOutput");
const factForm = document.querySelector("#factForm");
const factInput = document.querySelector("#factInput");
const factOutput = document.querySelector("#factOutput");
const ussdOutput = document.querySelector("#ussdOutput");

function addMessage(role, text, isError = false) {
  const bubble = document.createElement("article");
  bubble.className = `bubble ${role} ${isError ? "error" : ""}`;

  const label = document.createElement("strong");
  label.textContent = role === "user" ? "You" : "Msaidizi";

  const body = document.createElement("p");
  body.textContent = text;

  bubble.append(label, body);
  messages.appendChild(bubble);
  messages.scrollTop = messages.scrollHeight;
}

async function askAgent(message) {
  const response = await fetch("/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, message }),
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

async function submitChat(message) {
  addMessage("user", message);
  chatInput.value = "";
  chatInput.disabled = true;

  try {
    const data = await askAgent(message);
    addMessage("agent", data.reply);
  } catch (error) {
    addMessage("agent", "The agent could not respond. Check the server terminal.", true);
  } finally {
    chatInput.disabled = false;
    chatInput.focus();
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (message) {
    submitChat(message);
  }
});

quickPrompt.addEventListener("change", () => {
  if (quickPrompt.value) {
    chatInput.value = quickPrompt.value;
    chatInput.focus();
  }
});

lookupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  lookupOutput.textContent = "Searching...";
  try {
    const data = await askAgent(`Wapi nipigie kura ${lookupInput.value.trim()}?`);
    lookupOutput.textContent = data.reply;
  } catch (error) {
    lookupOutput.textContent = "Lookup failed. Check the server terminal.";
  }
});

factForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  factOutput.textContent = "Checking...";
  try {
    const data = await askAgent(`Is it true that ${factInput.value.trim()}?`);
    factOutput.textContent = data.reply;
  } catch (error) {
    factOutput.textContent = "Fact-check failed. Check the server terminal.";
  }
});

document.querySelectorAll("[data-ussd]").forEach((button) => {
  button.addEventListener("click", async () => {
    ussdOutput.textContent = "Loading...";
    try {
      const response = await fetch("/ussd", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: "demo-ui-session",
          phone,
          text: button.dataset.ussd,
        }),
      });
      const data = await response.json();
      ussdOutput.textContent = data.reply;
    } catch (error) {
      ussdOutput.textContent = "USSD preview failed. Check the server terminal.";
    }
  });
});

document.querySelector("[data-ussd='']").click();
