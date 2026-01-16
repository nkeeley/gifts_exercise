export interface CustomerRecord {
  customer_id: number;
  recency: number;
  frequency: number;
  monetary: number;
  median_purchase_days: number;
  churn_ratio: number | null;
  churn_label: string | null;
  monetary_log: number;
  cluster_assignment: number;
  segment: string;
}

export interface SegmentStatistics {
  segment: string;
  high_risk_count: number;
  medium_risk_count: number;
  med_high_ratio: number;
  med_high_monetary_sum: number;
}

export interface ProcessDataResponse {
  status: string;
  message: string;
  data: CustomerRecord[];
  total_customers: number;
  segment_statistics: SegmentStatistics[];
}

export interface CustomerRecommendationResponse {
  customer: CustomerRecord;
  recommendation: string;
}
