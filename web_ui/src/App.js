import React, { useState, useEffect } from "react";
import {
  MessageSquare,
  Search,
  Upload,
  BarChart3,
  Bot,
  Menu,
  X,
  Github,
  ExternalLink,
} from "lucide-react";

import ChatInterface from "./components/ChatInterface";
import SearchInterface from "./components/SearchInterface";
import DocumentUpload from "./components/DocumentUpload";
import SystemStats from "./components/SystemStats";
import { ragAPI } from "./api";

const App = () => {
  const [activeTab, setActiveTab] = useState("chat");
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Check API connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await ragAPI.healthCheck();
        setIsConnected(true);
        setConnectionError(null);
      } catch (error) {
        setIsConnected(false);
        setConnectionError(error.message);
      }
    };

    checkConnection();
  }, []);

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const tabs = [
    { id: "chat", label: "Chat", icon: MessageSquare },
    { id: "search", label: "Search", icon: Search },
    { id: "upload", label: "Upload", icon: Upload },
    { id: "stats", label: "Statistics", icon: BarChart3 },
  ];

  const renderActiveTab = () => {
    switch (activeTab) {
      case "chat":
        return <ChatInterface />;
      case "search":
        return <SearchInterface />;
      case "upload":
        return <DocumentUpload onUploadSuccess={handleUploadSuccess} />;
      case "stats":
        return <SystemStats refreshTrigger={refreshTrigger} />;
      default:
        return <ChatInterface />;
    }
  };

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Connection Failed
          </h2>
          <p className="text-gray-600 mb-4">
            Unable to connect to the RAG Bot server. Please make sure the
            backend is running.
          </p>
          <div className="bg-gray-50 rounded-lg p-3 mb-4">
            <p className="text-sm text-gray-700 font-mono">
              Error: {connectionError}
            </p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary w-full"
          >
            Retry Connection
          </button>
          <div className="mt-4 text-xs text-gray-500">
            <p>
              Make sure to run:{" "}
              <code className="bg-gray-100 px-1 rounded">
                python web_server.py
              </code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">RAG Bot</h1>
                <p className="text-xs text-gray-500">
                  Retrieval-Augmented Generation
                </p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                      activeTab === tab.id
                        ? "bg-primary-100 text-primary-700"
                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>

            {/* Connection status */}
            <div className="hidden md:flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-500">Connected</span>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => {
                        setActiveTab(tab.id);
                        setIsMobileMenuOpen(false);
                      }}
                      className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                        activeTab === tab.id
                          ? "bg-primary-100 text-primary-700"
                          : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-[calc(100vh-8rem)]">{renderActiveTab()}</div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-2 md:space-y-0">
            <p className="text-sm text-gray-500">
              RAG Bot - Powered by Hugging Face & FastAPI
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Built with React & Tailwind CSS</span>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 hover:text-gray-700 transition-colors duration-200"
              >
                <Github className="w-4 h-4" />
                <span>Source Code</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
