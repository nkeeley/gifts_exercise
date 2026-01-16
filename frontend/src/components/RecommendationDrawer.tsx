import { useEffect, useState } from "react";
import { X, Loader2, AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { CustomerRecord } from "@/types/api";
import { getCustomerRecommendation } from "@/lib/api";

interface RecommendationDrawerProps {
  customer: CustomerRecord | null;
  open: boolean;
  onClose: () => void;
}

export const RecommendationDrawer = ({
  customer,
  open,
  onClose,
}: RecommendationDrawerProps) => {
  const [recommendation, setRecommendation] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (customer && open) {
      setIsLoading(true);
      setError(null);
      setRecommendation(null);

      getCustomerRecommendation(customer.customer_id)
        .then((response) => {
          setRecommendation(response.recommendation);
        })
        .catch((err) => {
          setError(err.message || "Failed to load recommendation");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [customer, open]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getRiskIcon = (label: string | null) => {
    if (label === "High Risk") {
      return <AlertTriangle className="h-5 w-5 text-red-500" />;
    }
    if (label === "Medium Risk") {
      return <AlertCircle className="h-5 w-5 text-amber-500" />;
    }
    return <CheckCircle className="h-5 w-5 text-green-500" />;
  };

  const getRiskBadgeClass = (label: string | null) => {
    if (label === "High Risk") {
      return "bg-red-100 text-red-700 border-red-200";
    }
    if (label === "Medium Risk") {
      return "bg-amber-100 text-amber-700 border-amber-200";
    }
    return "bg-green-100 text-green-700 border-green-200";
  };

  // Parse recommendation text - split on numbered parentheses like (1), (2), (3)
  const parseRecommendation = (text: string) => {
    // Split on pattern like "(1)", "(2)", etc. but keep the delimiter
    const parts = text.split(/(?=\(\d+\))/).filter((part) => part.trim().length > 0);
    return parts.map((part) => part.trim());
  };

  return (
    <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader className="space-y-4">
          <div className="flex items-center justify-between">
            <SheetTitle className="text-xl font-bold">
              Customer Recommendation
            </SheetTitle>
          </div>
        </SheetHeader>

        {customer && (
          <div className="mt-6 space-y-6">
            {/* Customer Details */}
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Customer ID</p>
                  <p className="text-lg font-semibold">{customer.customer_id}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Segment</p>
                  <span className="inline-flex items-center rounded-md bg-secondary px-2.5 py-1 text-sm font-medium text-secondary-foreground">
                    {customer.segment}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Risk Level</p>
                  <div
                    className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium border ${getRiskBadgeClass(
                      customer.churn_label
                    )}`}
                  >
                    {getRiskIcon(customer.churn_label)}
                    {customer.churn_label || "Unknown"}
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Annual Customer Value</p>
                  <p className="text-lg font-semibold text-primary">
                    {formatCurrency(customer.monetary)}
                  </p>
                </div>
              </div>
            </div>

            <div className="border-t border-border" />

            {/* Recommendation Section */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold">Recommended Actions</h3>

              {isLoading && (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">
                    Loading recommendation...
                  </span>
                </div>
              )}

              {error && (
                <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-4 text-destructive">
                  <p className="text-sm">{error}</p>
                </div>
              )}

              {recommendation && !isLoading && (
                <div className="space-y-4">
                  {parseRecommendation(recommendation).map((point, index) => (
                    <p
                      key={index}
                      className="text-sm text-foreground leading-relaxed"
                    >
                      {point}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
};
