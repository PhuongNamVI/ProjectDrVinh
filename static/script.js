async function loadChatHistory() {
  try {
    const response = await fetch("/get-chat-history");
    const data = await response.json();
    const chatHistoryDiv = document.getElementById("chat-history");

    data.history.forEach((entry) => {
      const entryDiv = document.createElement("div");
      entryDiv.classList.add("chat-entry");

      const questionDiv = document.createElement("div");
      questionDiv.classList.add("chat-question");
      questionDiv.innerHTML = `<span class="user-label">User:</span> ${entry.question}`;

      const answerDiv = document.createElement("div");
      answerDiv.classList.add("chat-answer");
      answerDiv.innerHTML = `<span class="bot-label">AI:</span> ${entry.answer}`;

      entryDiv.appendChild(questionDiv);
      entryDiv.appendChild(answerDiv);
      chatHistoryDiv.appendChild(entryDiv);
    });

    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
  } catch (error) {
    console.error("Error when loading conversation", error);
  }
}

window.onload = loadChatHistory;

async function askQuestion() {
  const query = document.getElementById("query").value;
  const chatHistoryDiv = document.getElementById("chat-history");

  if (!query) {
    alert("Please enter a question.");
    return;
  }

  try {
    // Gửi câu hỏi đến API FastAPI
    const response = await fetch("/get-answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: query }),
    });

    const data = await response.json();

    const entryDiv = document.createElement("div");
    entryDiv.classList.add("chat-entry");

    const questionDiv = document.createElement("div");
    questionDiv.classList.add("chat-question");
    questionDiv.innerHTML = `<span class="user-label">User:</span> ${query}`;

    const answerDiv = document.createElement("div");
    answerDiv.classList.add("chat-answer");
    answerDiv.innerHTML = `<span class="bot-label">AI:</span> ${data.answer}`;

    entryDiv.appendChild(questionDiv);
    entryDiv.appendChild(answerDiv);
    chatHistoryDiv.appendChild(entryDiv);


    chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;

    document.getElementById("query").value = "";
  } catch (error) {
    console.error("Error when sending the QUESTION:", error);
    alert("Error when sending the QUESTION. Please try again.");
  }
}




