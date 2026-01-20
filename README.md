# Gifts Exercise - Customer Churn Risk Dashboard

## 1. Executive Summary

This is a dashboard application for a prospective e-commerce provider to view wholesale customers that are at risk of churning (relative to customer historical behavior), and provides recommendations on outreach based on RFM clustering.

To view hosted URL, see: https://gifts-exercise.vercel.app/. Upload any parquet file -- for the one associated with this exercise, navigate to the `backend/data/raw folder` and download the `online_retail.parquet` file located there.

The application enables retailers to:
- Upload transaction data in parquet format
- Visualize customer segments and churn risk through interactive charts and tables
- View aggregate statistics by customer segment
- Access personalized recommendations for individual customers based on their RFM (Recency, Frequency, Monetary) metrics and segment classification
- Filter and sort customers by various risk factors and segment types

The system uses KMeans clustering to segment customers into three groups: Monthly High-Value Buyers, Seasonal Buyers, and Experimental/Hesitant Lower-Value Buyers. Churn risk is calculated based on the ratio of recency to median purchase days, with customers classified as Low, Medium, or High Risk.

## 2. Environment Setup

To view hosted URL, see: https://gifts-exercise.vercel.app/

If you want to deploy locally, follow the steps below...

### Prerequisites

- **Python 3.11+** installed on your system
- **Node.js and npm** installed on your system (for frontend)
- Terminal access

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create the virtual environment:**
   ```bash
   python3 -m venv gifts_exercise
   ```
   This creates a directory called `gifts_exercise` with the virtual environment files.

3. **Activate the virtual environment:**
   ```bash
   source gifts_exercise/bin/activate
   ```
   After activation, your prompt should show `(gifts_exercise)`.

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** `requirements.txt` includes all dependencies for local development including Jupyter notebooks. For production deployment, Railway uses `requirements-prod.txt` which contains only the minimal packages needed for the API (FastAPI, pandas, scikit-learn, etc.), resulting in much faster builds.

5. **Verify the installation:**
   ```bash
   which python
   ```
   This should point to a path inside the `gifts_exercise` directory.

6. **Start the FastAPI backend server:**
   ```bash
   python3 main.py
   ```
   The backend will start on `http://0.0.0.0:8000` (or `http://localhost:8000`). Keep this terminal window open.

### Frontend Setup

1. **Open a new terminal window** (keep the backend terminal running)

2. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```
   This will install all required packages listed in `package.json`.

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   The frontend will typically start on `http://localhost:5173` (or another port if 5173 is occupied). The terminal will display the exact URL.

5. **Access the application:**
   Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:5173`).

### Notes

- The `gifts_exercise/` virtual environment directory is already included in `.gitignore` and will not be committed to version control.
- Make sure to activate the virtual environment before running the backend.
- Both the backend and frontend servers must be running simultaneously for the application to work.
- To stop either server, press `Ctrl+C` in the respective terminal window.
- To deactivate the Python virtual environment when done:
   ```bash
   deactivate
   ```

## 3. Repository Structure

```
gifts_exercise/
├── backend/                    # FastAPI backend application
│   ├── data/                   # Data storage
│   │   ├── raw/                # Raw input data (parquet files)
│   │   │   └── online_retail.parquet
│   │   └── processed/          # Processed output data (CSV files)
│   │       ├── customer_df.csv
│   │       ├── invoice_df.csv
│   │       └── full_df.csv
│   ├── notebooks/              # Jupyter notebooks for data exploration
│   │   └── data_exploration.ipynb
│   ├── tests/                  # Comprehensive pytest test suite
│   │   ├── __init__.py
│   │   ├── conftest.py         # Shared test fixtures
│   │   ├── test_endpoints.py   # API endpoint tests
│   │   ├── test_pipelines.py   # Data pipeline function tests
│   │   ├── test_recommendations.py  # Recommendation logic tests
│   │   ├── test_schemas.py     # Pydantic schema validation tests
│   │   └── README.md           # Test suite documentation
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── pipelines.py        # Data processing pipeline functions
│   │   └── recommendations.py  # Customer recommendation generation
│   ├── main.py                 # FastAPI application entry point
│   ├── schemas.py              # Pydantic models for API validation
│   ├── requirements.txt         # Full Python dependencies (for local dev with Jupyter)
│   ├── requirements-prod.txt    # Minimal production dependencies (for Railway deployment)
│   ├── Dockerfile               # Docker configuration for optimized production builds
│   ├── Procfile                 # Process definition for Railway/Render
│   ├── railway.json             # Railway deployment configuration
│   ├── render.yaml              # Render deployment configuration
│   └── pytest.ini              # Pytest configuration
│
├── frontend/                   # React + TypeScript frontend application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── Dashboard.tsx   # Main dashboard component
│   │   │   ├── ChurnTable.tsx  # Customer data table
│   │   │   ├── ChurnScatterPlot.tsx  # Churn visualization
│   │   │   ├── FileUploadZone.tsx    # File upload component
│   │   │   ├── RecommendationDrawer.tsx  # Customer recommendations
│   │   │   ├── SegmentFilter.tsx    # Segment filtering component
│   │   │   ├── StatCard.tsx    # Statistics display card
│   │   │   ├── NavLink.tsx     # Navigation link component
│   │   │   └── ui/             # shadcn/ui component library
│   │   ├── lib/
│   │   │   ├── api.ts          # API client for backend communication
│   │   │   └── utils.ts        # Utility functions
│   │   ├── types/
│   │   │   └── api.ts          # TypeScript type definitions
│   │   ├── pages/              # Page components
│   │   │   ├── Index.tsx       # Main page
│   │   │   └── NotFound.tsx   # 404 page
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── use-mobile.tsx
│   │   │   └── use-toast.ts
│   │   ├── test/               # Test files
│   │   ├── App.tsx             # Root App component
│   │   ├── App.css             # App styles
│   │   ├── main.tsx             # Application entry point
│   │   └── index.css           # Global styles
│   ├── public/                 # Static assets
│   │   ├── favicon.ico
│   │   ├── placeholder.svg
│   │   └── robots.txt
│   ├── package.json            # Node.js dependencies and scripts
│   ├── vite.config.ts          # Vite build configuration
│   ├── vercel.json             # Vercel deployment configuration
│   ├── vitest.config.ts        # Vitest test configuration
│   ├── tailwind.config.ts      # Tailwind CSS configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── components.json         # shadcn/ui components configuration
│   └── postcss.config.js       # PostCSS configuration
│
└── README.md                   # This file
```

### Key Directories Explained

- **`backend/data/raw/`**: Contains the input parquet file with transaction data
- **`backend/data/processed/`**: Contains processed CSV outputs (customer_df, invoice_df, full_df)
- **`backend/notebooks/`**: Jupyter notebook for exploratory data analysis and visualization
- **`backend/tests/`**: Comprehensive test suite covering endpoints, pipelines, schemas, and recommendations
- **`backend/utils/pipelines.py`**: Core data processing functions (ingest, transform, feature engineering, segmentation)
- **`backend/utils/recommendations.py`**: Logic for generating customer-specific recommendations
- **`frontend/src/components/`**: React components for the dashboard UI
- **`frontend/src/lib/api.ts`**: API client handling communication with the FastAPI backend


## 4. Approach / Methodology

### Business logic
- Originally I wanted to work on upsell conversions from lower to higher value customer segments (experience with this in real consulting world), but your prompt specified this is a B2B relationship between an e-commerce provider selling to wholesale customers. Wholesale customers are behaviorally different than retail or consumer-level customers (eg more sensitive to price, not necessarily as basket sensitive as retailers due to long term quotas/contracts with retailers). Ultimately, I ended up choosing to identify churn likelihood instead, and generate recommendations based on wholesale customer segmentation (using RFM KMeans clustering).
- Hypothesis: churn indicators for wholesalers are likely based on purchase recency/frequency, which will vary based on wholesale customer archetype (e.g. seasonal, regular/monthly buyers)

### Key design decisions
- Ideally, we'd have multiple years' worth of data to classify/label true churn. In the real world, businesses typically have their own definitions of what churn means based on the industry. Since we only have one year's worth of data, I opted to classify customers within churn propensity buckets (Low, Medium, High), rather than labeling definintive churn (if this existed, we'd have 0s/1s within a churn feature, and subsequently two types of "actions" for marketing end users: reactivate, or prevent churn). In this exercise, I kept it simple and assumed no customers had truly churned *yet*, with the objective of helping the marketing team identify where churn was most likely (i.e. assuming no customers had fully churned yet, but all had a churn propensity)
- I classified churn risk on a customer-relative basis, using a churn ratio. This was calculated by dividing the number of days since a customer's last purchase by the median days between historical purchases for that customer. Therefore, churn ratios lower than 1 were "Low Risk", anything between 1-2 (2x number of days it normally takes to purchase) was "Medium Risk". Anything greater was "High Risk". I chose median purchase days over average purchase days to account for seasonal/infrequent buyers -- an average would have skewed the  distribution.
- Decided to remove 100K transaction line items from dataset where no customer ID existed, since no attribution back to churn likelihood/customer behavior possible. That said, in real world, services like Amperity can stitch together personas based on other variables like credit card number, etc. I also removed an additional 10K rows containing negative prices and quantities (likely refunds). This shouldn't affect our analysis meaningfully, and also are accounting aberrations.
- NOTE: I did not notice there weren't any canceled invoices in the mock dataset, despite data dictionary indicating there would be. I checked multiple times using regex. This would have been a valuabe feature, but I'm assuming this was just a mock dataset glitch.
- NOTE: prices/quantities seemed extremely low for wholesalers (even for gifts and souvenirs), but I once again assumed it’s just the mock dataset. Did doublecheck raw data to confirm this.
- For KMeans, I ended up taking logarithm of monetary to account for skew, to help normalize the clustering process.
- Segmentation yielded three broad archetypes of customer behavior (along the RFM feature dimensions): Seasonal Buyers, Experimental / Hesitant Lower-Value Buyers, and Monthly High-Value Buyers. 

## 5. Next Steps (With More Time)

- In a real-world scenario, we would ask for more historical data and label true churn based on the business' definition. We would redo the analysis and have more robust features/action items.
- For the sake of time, I created static/deterministic recommendations for marketers to take for individual high-risk churn candidates, based on their segment labels (incorporating several key metrics for the customer). With more time, I would have either created personalized statistics (e.g. monthly basket size, purchase plotting by month), or run individual customer data through an LLM endpoint (didn't want to pay for LLM provider tokens and didn't have time to build this out) to provide highly personalized recommendations. If we had customer contact data, we could also generate outreach tailored to the customer.
- Because the raw dataset was so small (500K rows), we didn't need a DBMS hooked up. But if the customer wanted to scale this use case, we would hook up the upload to a DBMS and ingest data periodically/update the dashboard periodically using batching.
- Normally would look for customer differences by country, but decided to ignore this feature for the sake of time
- Right now, the CORS middleware accepts multiple origins. I left this for the sake of your ease/local deployment. In production, we would have to specify hosting routes.
- I used Cursor to produce a hypothetical test suite, which can be run via pytest. Some of the tests currently don't pass, which I would spend time addressing if this weren't a practice exercise.
