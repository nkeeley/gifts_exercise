import { useState } from "react";
import { ChevronDown, ChevronUp, AlertTriangle, AlertCircle } from "lucide-react";
import { CustomerRecord } from "@/types/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ChurnTableProps {
  data: CustomerRecord[];
  onCustomerClick?: (customer: CustomerRecord) => void;
}

export const ChurnTable = ({ data, onCustomerClick }: ChurnTableProps) => {
  const [showAll, setShowAll] = useState(false);

  // Filter to only at-risk customers (Medium or High)
  const atRiskData = data.filter(
    (customer) =>
      customer.churn_label === "High Risk" || customer.churn_label === "Medium Risk"
  );

  const displayData = showAll ? atRiskData : atRiskData.slice(0, 10);
  const hasMore = atRiskData.length > 10;

  const getRiskBadge = (label: string | null) => {
    if (label === "High Risk") {
      return (
        <span className="at-risk-badge">
          <AlertTriangle className="h-3 w-3" />
          High Risk
        </span>
      );
    }
    if (label === "Medium Risk") {
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium bg-amber-100 text-amber-700">
          <AlertCircle className="h-3 w-3" />
          Medium Risk
        </span>
      );
    }
    return <span className="text-muted-foreground text-sm">{label || "—"}</span>;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="data-table">
      <div className="border-b border-border px-6 py-4">
        <h3 className="text-lg font-semibold text-foreground">At-Risk Churn Candidates</h3>
        <p className="text-sm text-muted-foreground mt-1">
          Showing {displayData.length} of {atRiskData.length} at-risk customers • Click a row for recommendations
        </p>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="data-table-header">
              <TableHead className="font-semibold">Customer ID</TableHead>
              <TableHead className="font-semibold">Segment</TableHead>
              <TableHead className="font-semibold">Risk Level</TableHead>
              <TableHead className="font-semibold text-right">Churn Ratio</TableHead>
              <TableHead className="font-semibold text-right">Recency (days)</TableHead>
              <TableHead className="font-semibold text-right">Frequency</TableHead>
              <TableHead className="font-semibold text-right">Annual Customer Value</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayData.map((customer) => (
              <TableRow
                key={customer.customer_id}
                className="data-table-row cursor-pointer hover:bg-accent/50 transition-colors"
                onClick={() => onCustomerClick?.(customer)}
              >
                <TableCell className="font-medium">{customer.customer_id}</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground">
                    {customer.segment}
                  </span>
                </TableCell>
                <TableCell>{getRiskBadge(customer.churn_label)}</TableCell>
                <TableCell className="text-right font-mono">
                  {customer.churn_ratio?.toFixed(2) ?? "—"}
                </TableCell>
                <TableCell className="text-right font-mono">{customer.recency}</TableCell>
                <TableCell className="text-right font-mono">{customer.frequency}</TableCell>
                <TableCell className="text-right font-mono">
                  {formatCurrency(customer.monetary)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {hasMore && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="flex w-full items-center justify-center gap-2 border-t border-border py-4 text-sm font-medium text-primary hover:bg-accent transition-colors"
        >
          {showAll ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Show Less
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              Show All {atRiskData.length} Customers
            </>
          )}
        </button>
      )}
    </div>
  );
};
