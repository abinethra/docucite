import { useState } from "react";
import { uploadDocument } from "../api";

export default function UploadPanel() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    setSuccessMsg("");

    try {
      const res = await uploadDocument(file);
      setSuccessMsg(`Successfully uploaded ${res.filename} (${res.chunks_stored} chunks stored).`);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 className="text-lg font-bold text-gray-800 mb-4">Upload Document</h2>
      <form onSubmit={handleUpload} className="space-y-4">
        <div>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        {successMsg && <p className="text-sm text-green-600">{successMsg}</p>}
        <button
          type="submit"
          disabled={loading || !file}
          className="w-full py-2 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 transition text-sm"
        >
          {loading ? "Uploading & Embedding..." : "Upload & Process"}
        </button>
      </form>
    </div>
  );
}