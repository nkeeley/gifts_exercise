import { ProcessDataResponse, CustomerRecommendationResponse } from "@/types/api";

// Old code that was yielding errors on Vercel
//const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// TEMP: log API base URL to confirm Vercel env variable
console.log("API_BASE_URL:", API_BASE_URL);

export async function processData(file: File): Promise<ProcessDataResponse> {
  const formData = new FormData();
  formData.append("file", file, file.name);

  const response = await fetch(`${API_BASE_URL}/api/process-data`, {
    method: "POST",
    body: formData,
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  });

  const text = await response.text();
  
  let data;
  try {
    data = JSON.parse(text);
  } catch (e) {
    console.error("API returned non-JSON response:", text.substring(0, 500));
    throw new Error("Server returned invalid response. Check if the backend is accessible.");
  }

  if (!response.ok) {
    throw new Error(data.detail || data.message || "Failed to process data");
  }

  return data;
}

export async function getCustomerRecommendation(
  customerId: number
): Promise<CustomerRecommendationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/customer/${customerId}/recommendation`,
    {
      headers: {
        "ngrok-skip-browser-warning": "true",
      },
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || "Failed to get recommendation");
  }

  return response.json();
}
