import React, { useState, useRef } from "react";
import {
  Upload,
  File,
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { ragAPI } from "../api";

const DocumentUpload = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const fileInputRef = useRef(null);

  const supportedTypes = [".txt", ".pdf", ".docx"];

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const validFiles = selectedFiles.filter((file) => {
      const extension = "." + file.name.split(".").pop().toLowerCase();
      return supportedTypes.includes(extension);
    });

    setFiles((prev) => [...prev, ...validFiles]);
    setUploadStatus(null);
  };

  const removeFile = (indexToRemove) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const response = await ragAPI.uploadDocuments(files);

      setUploadStatus({
        type: "success",
        message: response.message,
        details: `${response.files_processed} files processed, ${response.chunks_added} chunks added`,
      });

      setFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (error) {
      setUploadStatus({
        type: "error",
        message: "Upload failed",
        details: error.response?.data?.detail || error.message,
      });
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* Upload area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors duration-200">
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-700 mb-2">
          Upload Documents
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Supported formats: {supportedTypes.join(", ")}
        </p>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={supportedTypes.join(",")}
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Choose Files
        </label>
      </div>

      {/* Selected files */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-700">Selected Files:</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <File className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors duration-200"
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={isUploading || files.length === 0}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isUploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                <span>
                  Upload {files.length} file{files.length !== 1 ? "s" : ""}
                </span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Upload status */}
      {uploadStatus && (
        <div
          className={`p-4 rounded-lg flex items-start space-x-3 ${
            uploadStatus.type === "success"
              ? "bg-green-50 border border-green-200"
              : "bg-red-50 border border-red-200"
          }`}
        >
          {uploadStatus.type === "success" ? (
            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          )}
          <div>
            <p
              className={`font-medium ${
                uploadStatus.type === "success"
                  ? "text-green-800"
                  : "text-red-800"
              }`}
            >
              {uploadStatus.message}
            </p>
            <p
              className={`text-sm mt-1 ${
                uploadStatus.type === "success"
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {uploadStatus.details}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
