import { useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";
import { CustomerRecord } from "@/types/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ChurnScatterPlotProps {
  data: CustomerRecord[];
  onCustomerClick?: (customer: CustomerRecord) => void;
}

export const ChurnScatterPlot = ({ data, onCustomerClick }: ChurnScatterPlotProps) => {
  // Cap X-axis at 5 to make thresholds visible (outliers still shown but capped)
  const maxXAxis = 5;

  const scatterData = useMemo(() => {
    return data
      .filter((customer) => customer.churn_ratio !== null)
      .map((customer) => ({
        x: Math.min(customer.churn_ratio!, maxXAxis), // Cap at maxXAxis for display
        y: customer.monetary,
        originalX: customer.churn_ratio,
        customerId: customer.customer_id,
        segment: customer.segment,
        churnLabel: customer.churn_label,
        customer, // Store full customer object for click handler
      }));
  }, [data]);

  const getPointColor = (churnRatio: number) => {
    if (churnRatio >= 2) return "hsl(0, 84%, 60%)"; // High risk - red
    if (churnRatio >= 1) return "hsl(38, 92%, 50%)"; // Medium risk - orange/amber
    return "hsl(142, 71%, 45%)"; // Low risk - green
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value.toFixed(0)}`;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
          <p className="font-semibold text-foreground">Customer #{data.customerId}</p>
          <p className="text-sm text-muted-foreground">Segment: {data.segment}</p>
          <p className="text-sm text-muted-foreground">
            Churn Ratio: <span className="font-medium text-foreground">{data.originalX.toFixed(2)}</span>
          </p>
          <p className="text-sm text-muted-foreground">
            Annual Value: <span className="font-medium text-foreground">{formatCurrency(data.y)}</span>
          </p>
          <p className="text-sm text-muted-foreground">
            Risk: <span className="font-medium text-foreground">{data.churnLabel || "N/A"}</span>
          </p>
          <p className="text-xs text-muted-foreground mt-2 italic">Click for recommendations</p>
        </div>
      );
    }
    return null;
  };

  const handleScatterClick = (data: any) => {
    if (data && data.customer && onCustomerClick) {
      onCustomerClick(data.customer);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Churn Risk vs. Annual Customer Value</CardTitle>
        <p className="text-sm text-muted-foreground">
          Churn ratio = days since last purchase ÷ median days between purchases. Click a point for recommendations. Vertical lines indicate medium (1.0) and high (2.0) risk thresholds.
        </p>
      </CardHeader>
      <CardContent>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis
                type="number"
                dataKey="x"
                name="Churn Ratio"
                domain={[0, maxXAxis]}
                tickLine={false}
                axisLine={false}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                label={{
                  value: "Churn Ratio",
                  position: "bottom",
                  offset: 0,
                  fill: "hsl(var(--muted-foreground))",
                  fontSize: 12,
                }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="Annual Customer Value"
                tickFormatter={formatCurrency}
                tickLine={false}
                axisLine={false}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                label={{
                  value: "Annual Customer Value",
                  angle: -90,
                  position: "insideLeft",
                  fill: "hsl(var(--muted-foreground))",
                  fontSize: 12,
                }}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* Medium risk threshold line at x=1 */}
              <ReferenceLine
                x={1}
                stroke="hsl(38, 92%, 50%)"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: "Medium Risk",
                  position: "top",
                  fill: "hsl(38, 92%, 50%)",
                  fontSize: 11,
                }}
              />
              
              {/* High risk threshold line at x=2 */}
              <ReferenceLine
                x={2}
                stroke="hsl(0, 84%, 60%)"
                strokeWidth={2}
                strokeDasharray="5 5"
                label={{
                  value: "High Risk",
                  position: "top",
                  fill: "hsl(0, 84%, 60%)",
                  fontSize: 11,
                }}
              />
              
              <Scatter
                name="Customers"
                data={scatterData}
                onClick={handleScatterClick}
                cursor="pointer"
              >
                {scatterData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getPointColor(entry.x)}
                    fillOpacity={0.7}
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-center gap-6 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "hsl(142, 71%, 45%)" }} />
            <span className="text-muted-foreground">Low Risk (&lt;1.0)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "hsl(38, 92%, 50%)" }} />
            <span className="text-muted-foreground">Medium Risk (1.0-2.0)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "hsl(0, 84%, 60%)" }} />
            <span className="text-muted-foreground">High Risk (&gt;2.0)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
