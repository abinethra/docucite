const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_URL}/documents`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Failed to upload document");
  }
  return response.json();
}

export async function sendChatMessage(question, sessionId = null) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, session_id: sessionId }),
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Failed to get chat response");
  }
  return response.json();
}