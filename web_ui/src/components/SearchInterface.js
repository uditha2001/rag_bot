import React, { useState } from "react";
import { Search, FileText, ExternalLink } from "lucide-react";
import { ragAPI } from "../api";

const SearchInterface = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    try {
      const response = await ragAPI.searchDocuments(searchQuery, 10);
      setSearchResults(response.results);
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const highlightText = (text, query) => {
    if (!query.trim()) return text;

    const regex = new RegExp(
      `(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
      "gi"
    );
    const parts = text.split(regex);

    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="space-y-6">
      {/* Search input */}
      <div className="flex space-x-4">
        <div className="flex-1 relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search through your documents..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            disabled={isSearching}
          />
          <Search className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" />
        </div>
        <button
          onClick={handleSearch}
          disabled={!searchQuery.trim() || isSearching}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {isSearching ? "Searching..." : "Search"}
        </button>
      </div>

      {/* Search results */}
      {hasSearched && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              Search Results
            </h3>
            <span className="text-sm text-gray-500">
              {searchResults.length} result
              {searchResults.length !== 1 ? "s" : ""} found
            </span>
          </div>

          {searchResults.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-500">
                No documents found matching your search query.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <div
                  key={index}
                  className="card p-4 hover:shadow-lg transition-shadow duration-200"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <FileText className="h-5 w-5 text-primary-600" />
                      <h4 className="font-medium text-gray-900">
                        {result.source}
                      </h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500">
                        Similarity: {(result.score * 100).toFixed(1)}%
                      </span>
                      <div
                        className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden"
                        title={`Similarity score: ${(
                          result.score * 100
                        ).toFixed(1)}%`}
                      >
                        <div
                          className="h-full bg-primary-600 transition-all duration-300"
                          style={{ width: `${result.score * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="text-gray-700 leading-relaxed">
                    {highlightText(result.content, searchQuery)}
                  </div>

                  {result.metadata &&
                    result.metadata.chunk_id !== undefined && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <span className="text-xs text-gray-500">
                          Chunk ID: {result.metadata.chunk_id}
                        </span>
                      </div>
                    )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Search tips */}
      {!hasSearched && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Search Tips:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Use specific keywords related to your documents</li>
            <li>
              • Try different phrasings if you don't find what you're looking
              for
            </li>
            <li>• Search results are ranked by semantic similarity</li>
            <li>• You can search for concepts, not just exact matches</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default SearchInterface;
