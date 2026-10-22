import { useState } from "react";
import UploadPanel from "./components/UploadPanel";
import ChatWindow from "./components/ChatWindow";
import SourceModal from "./components/SourceModal";

export default function App() {
  const [selectedCitation, setSelectedCitation] = useState(null);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <header className="max-w-6xl mx-auto mb-8">
        <h1 className="text-3xl font-extrabold text-blue-900">DocuCite 📚</h1>
        <p className="text-sm text-gray-600">RAG-enabled AI Chatbot with Document Citations</p>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <UploadPanel />
        </div>
        <div className="md:col-span-2">
          <ChatWindow onSelectCitation={setSelectedCitation} />
        </div>
      </main>

      <SourceModal citation={selectedCitation} onClose={() => setSelectedCitation(null)} />
    </div>
  );
}