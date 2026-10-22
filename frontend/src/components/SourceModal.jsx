export default function SourceModal({ citation, onClose }) {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6 m-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-800">Source Citation Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 font-bold text-xl">&times;</button>
        </div>
        <div className="space-y-3 text-sm text-gray-700">
          <p><strong>File:</strong> {citation.file}</p>
          <p><strong>Page:</strong> {citation.page}</p>
          <div>
            <strong className="block mb-1">Snippet Preview:</strong>
            <div className="p-3 bg-gray-50 rounded border border-gray-200 italic font-mono text-xs">
              "{citation.snippet}"
            </div>
          </div>
        </div>
        <div className="mt-6 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}