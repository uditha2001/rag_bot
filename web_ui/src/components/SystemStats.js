import React, { useState, useEffect } from "react";
import {
  BarChart3,
  FileText,
  Database,
  Cpu,
  Trash2,
  RefreshCw,
} from "lucide-react";
import { ragAPI } from "../api";

const SystemStats = ({ refreshTrigger }) => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isClearing, setIsClearing] = useState(false);

  const fetchStats = async () => {
    setIsLoading(true);
    try {
      const response = await ragAPI.getStats();
      setStats(response);
    } catch (error) {
      console.error("Failed to fetch stats:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [refreshTrigger]);

  const handleClearDocuments = async () => {
    if (
      !window.confirm(
        "Are you sure you want to clear all documents? This action cannot be undone."
      )
    ) {
      return;
    }

    setIsClearing(true);
    try {
      await ragAPI.clearDocuments();
      await fetchStats(); // Refresh stats after clearing
    } catch (error) {
      console.error("Failed to clear documents:", error);
      alert("Failed to clear documents. Please try again.");
    } finally {
      setIsClearing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Failed to load system statistics.</p>
        <button onClick={fetchStats} className="mt-2 btn-primary">
          Try Again
        </button>
      </div>
    );
  }

  const statCards = [
    {
      title: "Total Documents",
      value: stats.total_documents,
      icon: FileText,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "Vector Embeddings",
      value: stats.total_vectors,
      icon: Database,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "Unique Sources",
      value: stats.unique_sources,
      icon: BarChart3,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      title: "Embedding Model",
      value: stats.embedding_model?.split("/").pop() || "N/A",
      icon: Cpu,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
      isText: true,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">System Statistics</h3>
        <div className="flex space-x-2">
          <button
            onClick={fetchStats}
            className="btn-secondary flex items-center space-x-2"
            disabled={isLoading}
          >
            <RefreshCw
              className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
            />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleClearDocuments}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 flex items-center space-x-2"
            disabled={isClearing || stats.total_documents === 0}
          >
            <Trash2 className="h-4 w-4" />
            <span>{isClearing ? "Clearing..." : "Clear All"}</span>
          </button>
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <div key={index} className="card p-4">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">
                  {stat.title}
                </p>
                <p
                  className={`text-lg font-semibold ${
                    stat.isText ? "text-sm" : "text-2xl"
                  } text-gray-900`}
                >
                  {stat.isText ? stat.value : stat.value.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Sources list */}
      {stats.sources && stats.sources.length > 0 && (
        <div className="card p-4">
          <h4 className="font-medium text-gray-900 mb-3">Document Sources</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
            {stats.sources.map((source, index) => (
              <div
                key={index}
                className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg"
              >
                <FileText className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-700">{source}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System info */}
      <div className="card p-4">
        <h4 className="font-medium text-gray-900 mb-3">System Information</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-600">Embedding Model:</span>
            <p className="text-gray-900 mt-1">{stats.embedding_model}</p>
          </div>
          <div>
            <span className="font-medium text-gray-600">Vector Dimension:</span>
            <p className="text-gray-900 mt-1">{stats.embedding_dimension}</p>
          </div>
        </div>
      </div>

      {/* Empty state */}
      {stats.total_documents === 0 && (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">
            No Documents Loaded
          </h4>
          <p className="text-gray-500">
            Upload some documents to get started with your RAG system.
          </p>
        </div>
      )}
    </div>
  );
};

export default SystemStats;
