import { useState } from "react";
import { sendChatMessage } from "../api";
import CitationChip from "./CitationChip";

export default function ChatWindow({ onSelectCitation }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuery = input;
    setInput("");
    setLoading(true);
    setError("");

    setMessages((prev) => [...prev, { role: "user", question: userQuery }]);

    try {
      const res = await sendChatMessage(userQuery, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", answer: res.answer, citations: res.citations },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", answer: "Error: Failed to fetch response.", citations: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-md border border-gray-200">
      <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg flex justify-between items-center">
        <h2 className="text-lg font-bold text-gray-800">DocuCite Chat Assistant</h2>
        {sessionId && <span className="text-xs text-gray-500 font-mono">Session: {sessionId.slice(0, 8)}...</span>}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-center text-gray-400 mt-20 text-sm">Upload a document and ask a question to get started!</p>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
            <div
              className={`max-w-[80%] p-3 rounded-lg text-sm ${
                msg.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.role === "user" ? msg.question : msg.answer}</p>
            </div>
            {msg.citations && msg.citations.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1.5 max-w-[80%]">
                {msg.citations.map((cit, cIdx) => (
                  <CitationChip key={cIdx} citation={cit} onSelect={onSelectCitation} />
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2 text-gray-500 text-sm italic">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            <span>Thinking & searching documents...</span>
          </div>
        )}
      </div>

      {error && <div className="px-4 py-2 bg-red-50 text-red-600 text-xs">{error}</div>}

      <form onSubmit={handleSend} className="p-4 border-t border-gray-200 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm transition"
        >
          Send
        </button>
      </form>
    </div>
  );
}