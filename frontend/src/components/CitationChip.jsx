export default function CitationChip({ citation, onSelect }) {
  return (
    <button
      onClick={() => onSelect(citation)}
      className="inline-flex items-center gap-1 px-2 py-0.5 m-0.5 text-xs font-medium bg-blue-50 text-blue-700 rounded-md border border-blue-200 hover:bg-blue-100 transition"
    >
      <span>📄 {citation.file}</span>
      <span className="bg-blue-200 text-blue-800 px-1 rounded text-[10px]">p.{citation.page}</span>
    </button>
  );
}