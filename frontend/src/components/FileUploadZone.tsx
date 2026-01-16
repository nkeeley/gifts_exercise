import { useCallback, useState } from "react";
import { Upload, FileUp } from "lucide-react";

interface FileUploadZoneProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

export const FileUploadZone = ({ onFileSelect, isLoading }: FileUploadZoneProps) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file && file.name.endsWith(".parquet")) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  if (isLoading) {
    return (
      <div className="upload-zone min-h-[320px]">
        <div className="loading-spinner h-16 w-16 mb-6" />
        <p className="text-lg font-medium text-foreground">Processing your data...</p>
        <p className="text-sm text-muted-foreground mt-2">
          Analyzing customer segments and churn risk
        </p>
      </div>
    );
  }

  return (
    <div
      className={`upload-zone min-h-[320px] cursor-pointer ${isDragging ? "dragging" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => document.getElementById("file-input")?.click()}
    >
      <input
        id="file-input"
        type="file"
        accept=".parquet"
        onChange={handleFileInput}
        className="hidden"
      />
      <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10 mb-6">
        {isDragging ? (
          <FileUp className="h-10 w-10 text-primary" />
        ) : (
          <Upload className="h-10 w-10 text-primary" />
        )}
      </div>
      <p className="text-xl font-semibold text-foreground mb-2">
        {isDragging ? "Drop your file here" : "Upload Customer Data"}
      </p>
      <p className="text-sm text-muted-foreground mb-6 text-center max-w-sm">
        Drag and drop your parquet file here, or click to browse
      </p>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <div className="h-1 w-1 rounded-full bg-primary" />
        <span>Supports .parquet files</span>
      </div>
    </div>
  );
};
