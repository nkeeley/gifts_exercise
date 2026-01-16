import { useState } from "react";
import { Shield, RefreshCw } from "lucide-react";
import { FileUploadZone } from "@/components/FileUploadZone";
import { Dashboard } from "@/components/Dashboard";
import { ProcessDataResponse } from "@/types/api";
import { processData } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<ProcessDataResponse | null>(null);
  const { toast } = useToast();

  const handleFileSelect = async (file: File) => {
    setIsLoading(true);
    try {
      const response = await processData(file);
      setDashboardData(response);
      toast({
        title: "Data processed successfully",
        description: `Analyzed ${response.total_customers.toLocaleString()} customers across ${response.segment_statistics.length} segments.`,
      });
    } catch (error) {
      toast({
        title: "Error processing file",
        description: error instanceof Error ? error.message : "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setDashboardData(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary">
                <Shield className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">Churn Prevention Tracker</h1>
                <p className="text-sm text-muted-foreground">Customer retention analytics</p>
              </div>
            </div>
            {dashboardData && (
              <button
                onClick={handleReset}
                className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground hover:bg-accent transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                Upload New Data
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {!dashboardData ? (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="w-full max-w-2xl">
              <FileUploadZone onFileSelect={handleFileSelect} isLoading={isLoading} />
            </div>
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 text-center max-w-4xl">
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent mx-auto mb-4">
                  <span className="text-xl font-bold text-primary">1</span>
                </div>
                <h3 className="font-semibold text-foreground mb-2">Upload Data</h3>
                <p className="text-sm text-muted-foreground">
                  Drop your customer transaction parquet file
                </p>
              </div>
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent mx-auto mb-4">
                  <span className="text-xl font-bold text-primary">2</span>
                </div>
                <h3 className="font-semibold text-foreground mb-2">Analyze Segments</h3>
                <p className="text-sm text-muted-foreground">
                  Automatic RFM analysis and churn prediction
                </p>
              </div>
              <div>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent mx-auto mb-4">
                  <span className="text-xl font-bold text-primary">3</span>
                </div>
                <h3 className="font-semibold text-foreground mb-2">Take Action</h3>
                <p className="text-sm text-muted-foreground">
                  Identify at-risk customers and prevent churn
                </p>
              </div>
            </div>
          </div>
        ) : (
          <Dashboard data={dashboardData} />
        )}
      </main>
    </div>
  );
};

export default Index;
