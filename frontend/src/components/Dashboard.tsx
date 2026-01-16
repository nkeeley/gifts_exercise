import { useMemo, useState } from "react";
import { Users, TrendingDown, DollarSign } from "lucide-react";
import { ProcessDataResponse, CustomerRecord } from "@/types/api";
import { StatCard } from "./StatCard";
import { SegmentFilter } from "./SegmentFilter";
import { ChurnTable } from "./ChurnTable";
import { ChurnScatterPlot } from "./ChurnScatterPlot";
import { RecommendationDrawer } from "./RecommendationDrawer";

interface DashboardProps {
  data: ProcessDataResponse;
}

export const Dashboard = ({ data }: DashboardProps) => {
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerRecord | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Filter out "Total" segment from statistics - it's a summary row, not a real segment
  const realSegments = useMemo(() => {
    return data.segment_statistics.filter((s) => s.segment.toLowerCase() !== "total");
  }, [data.segment_statistics]);

  const filteredStats = useMemo(() => {
    if (selectedSegment === null) {
      // Aggregate all real segments - calculate actual totals
      const totalCustomers = data.data.length;
      const totalAtRiskCount = realSegments.reduce(
        (sum, seg) => sum + seg.high_risk_count + seg.medium_risk_count,
        0
      );
      const totalMonetaryAtRisk = realSegments.reduce(
        (sum, seg) => sum + seg.med_high_monetary_sum,
        0
      );
      return {
        totalCustomers,
        atRiskPercentage: totalCustomers > 0 ? (totalAtRiskCount / totalCustomers) * 100 : 0,
        monetaryAtRisk: totalMonetaryAtRisk,
      };
    }

    const segment = data.segment_statistics.find((s) => s.segment === selectedSegment);
    if (!segment) {
      return { totalCustomers: 0, atRiskPercentage: 0, monetaryAtRisk: 0 };
    }

    // Count customers in this segment
    const customersInSegment = data.data.filter((c) => c.segment === selectedSegment).length;

    return {
      totalCustomers: customersInSegment,
      atRiskPercentage: segment.med_high_ratio * 100,
      monetaryAtRisk: segment.med_high_monetary_sum,
    };
  }, [data, selectedSegment, realSegments]);

  const filteredData = useMemo(() => {
    if (selectedSegment === null) {
      return data.data;
    }
    return data.data.filter((customer) => customer.segment === selectedSegment);
  }, [data.data, selectedSegment]);

  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    }
    if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
  };

  const handleCustomerClick = (customer: CustomerRecord) => {
    setSelectedCustomer(customer);
    setDrawerOpen(true);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
  };

  return (
    <div className="space-y-8">
      {/* Segment Filter */}
      <SegmentFilter
        segments={realSegments}
        selectedSegment={selectedSegment}
        onSegmentChange={setSelectedSegment}
      />

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          label="Total Customers"
          value={filteredStats.totalCustomers.toLocaleString()}
          icon={<Users className="h-5 w-5 text-primary" />}
          subtext={selectedSegment ? `In "${selectedSegment}"` : "Across all segments"}
        />
        <StatCard
          label="At-Risk Customers"
          value={`${filteredStats.atRiskPercentage.toFixed(1)}%`}
          icon={<TrendingDown className="h-5 w-5 text-primary" />}
          subtext="Medium & High risk combined"
        />
        <StatCard
          label="Value at Risk"
          value={formatCurrency(filteredStats.monetaryAtRisk)}
          icon={<DollarSign className="h-5 w-5 text-primary" />}
          subtext="Potential revenue at stake"
        />
      </div>

      {/* Scatter Plot */}
      <ChurnScatterPlot data={filteredData} onCustomerClick={handleCustomerClick} />

      {/* Churn Table */}
      <ChurnTable data={filteredData} onCustomerClick={handleCustomerClick} />

      {/* Recommendation Drawer */}
      <RecommendationDrawer
        customer={selectedCustomer}
        open={drawerOpen}
        onClose={handleDrawerClose}
      />
    </div>
  );
};
