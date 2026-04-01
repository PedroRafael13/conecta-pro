interface ChatSuggestionsProps {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
}

export function ChatSuggestions({ suggestions, onSuggestionClick }: ChatSuggestionsProps) {
  if (suggestions.length === 0) return null;

  return (
    <div className="px-5 pb-3 animate-in fade-in slide-in-from-bottom-4 delay-300">
      <p className="text-xs font-semibold text-amber-400/80 mb-2.5 flex items-center gap-2">
        <span className="w-1 h-1 rounded-full bg-amber-400 animate-pulse" />
        Sugestoes rapidas
      </p>
      <div className="flex flex-wrap gap-2">
        {suggestions.slice(0, 4).map((suggestion, idx) => (
          <button
            key={idx}
            onClick={() => onSuggestionClick(suggestion)}
            className="text-xs px-3.5 py-2 rounded-xl bg-slate-800/60 backdrop-blur-sm text-slate-300 hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-orange-500/20 hover:text-amber-300 transition-all duration-200 border border-slate-700/50 hover:border-amber-500/40 shadow-sm hover:shadow-lg hover:shadow-amber-500/10 font-medium"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
