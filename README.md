# Gifts Exercise - Customer Churn Risk Dashboard

## 1. Executive Summary

This is a dashboard application for a prospective e-commerce provider to view wholesale customers that are at risk of churning (relative to customer historical behavior), and provides recommendations on outreach based on RFM clustering.

The application enables retailers to:
- Upload transaction data in parquet format
- Visualize customer segments and churn risk through interactive charts and tables
- View aggregate statistics by customer segment
- Access personalized recommendations for individual customers based on their RFM (Recency, Frequency, Monetary) metrics and segment classification
- Filter and sort customers by various risk factors and segment types

The system uses KMeans clustering to segment customers into three groups: Monthly High-Value Buyers, Seasonal Buyers, and Experimental/Hesitant Lower-Value Buyers. Churn risk is calculated based on the ratio of recency to median purchase days, with customers classified as Low, Medium, or High Risk.

## 2. Environment Setup

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
│   │   └── processed/          # Processed output data (CSV files)
│   ├── notebooks/              # Jupyter notebooks for data exploration
│   │   └── data_exploration.ipynb
│   ├── tests/                  # Comprehensive pytest test suite
│   │   ├── conftest.py         # Shared test fixtures
│   │   ├── test_endpoints.py   # API endpoint tests
│   │   ├── test_pipelines.py   # Data pipeline function tests
│   │   ├── test_recommendations.py  # Recommendation logic tests
│   │   └── test_schemas.py     # Pydantic schema validation tests
│   ├── utils/                  # Utility modules
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
│   │   │   └── ui/             # shadcn/ui component library
│   │   ├── lib/
│   │   │   ├── api.ts          # API client for backend communication
│   │   │   └── utils.ts        # Utility functions
│   │   ├── types/
│   │   │   └── api.ts          # TypeScript type definitions
│   │   ├── pages/              # Page components
│   │   └── hooks/              # Custom React hooks
│   ├── public/                 # Static assets
│   ├── package.json            # Node.js dependencies and scripts
│   └── vite.config.ts          # Vite build configuration
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

## 4. Production Deployment

This application can be deployed to production using a split deployment strategy: frontend on Vercel and backend on Railway or Render.

### Prerequisites

- GitHub account (for connecting repositories)
- Vercel account (free tier available)
- Railway account (free tier available) OR Render account (free tier available)

### Backend Deployment (Railway or Render)

#### Option A: Railway (Recommended)

1. **Sign up for Railway:**
   - Go to [railway.app](https://railway.app) and sign up with GitHub

2. **Create a new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `gifts_exercise` repository

3. **Configure the service:**
   - Railway will auto-detect the `backend/` directory
   - Set the root directory to `backend` in project settings
   - Railway will automatically detect and use the `Dockerfile` for building
   - The Dockerfile uses `requirements-prod.txt` (minimal production dependencies) for faster builds

4. **Set environment variables:**
   - Go to the Variables tab in your Railway project
   - Add `CORS_ORIGINS` (leave empty for now, we'll update after frontend deployment)
   - Railway will automatically set `PORT` variable

5. **Deploy:**
   - Railway will automatically deploy on push to your main branch
   - Note your deployment URL (e.g., `https://your-app.railway.app`)

6. **Test the backend:**
   - Visit `https://your-app.railway.app/docs` to see the FastAPI docs
   - Test the `/api/process-data` endpoint

#### Option B: Render

1. **Sign up for Render:**
   - Go to [render.com](https://render.com) and sign up with GitHub

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `gifts_exercise` repository

3. **Configure the service:**
   - **Name**: `gifts-exercise-backend` (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

4. **Set environment variables:**
   - Go to the Environment tab
   - Add `CORS_ORIGINS` (leave empty for now)
   - Render will automatically set `PORT` variable

5. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Note your deployment URL (e.g., `https://your-app.onrender.com`)

6. **Test the backend:**
   - Visit `https://your-app.onrender.com/docs` to see the FastAPI docs
   - Test the `/api/process-data` endpoint

### Frontend Deployment (Vercel)

1. **Sign up for Vercel:**
   - Go to [vercel.com](https://vercel.com) and sign up with GitHub

2. **Import your repository:**
   - Click "Add New..." → "Project"
   - Import your `gifts_exercise` repository

3. **Configure the project:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Set environment variables:**
   - Go to Settings → Environment Variables
   - Add `VITE_API_BASE_URL` with your backend URL:
     - Railway: `https://your-app.railway.app`
     - Render: `https://your-app.onrender.com`
   - Make sure to set it for Production, Preview, and Development environments

5. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy your frontend
   - Note your deployment URL (e.g., `https://your-app.vercel.app`)

6. **Update backend CORS:**
   - Go back to Railway/Render
   - Update the `CORS_ORIGINS` environment variable with your Vercel URL:
     - Example: `https://your-app.vercel.app`
     - For multiple environments: `https://your-app.vercel.app,https://your-app-git-main.vercel.app`
   - Redeploy the backend (Railway auto-redeploys, Render may need manual trigger)

### Verification

1. **Test the full flow:**
   - Visit your Vercel frontend URL
   - Upload a parquet file
   - Verify data processing works
   - Check that recommendations load correctly

2. **Monitor logs:**
   - Railway: View logs in the Deployments tab
   - Render: View logs in the Logs tab
   - Vercel: View logs in the Deployments tab

### Environment Variables Summary

**Backend (Railway/Render):**
- `CORS_ORIGINS`: Comma-separated list of allowed frontend URLs (e.g., `https://your-app.vercel.app`)
- `PORT`: Automatically set by the platform

**Frontend (Vercel):**
- `VITE_API_BASE_URL`: Backend API URL (e.g., `https://your-app.railway.app`)

### Troubleshooting

- **CORS errors**: Ensure `CORS_ORIGINS` includes your exact Vercel URL (with `https://`)
- **API connection errors**: Verify `VITE_API_BASE_URL` is set correctly in Vercel
- **Build failures**: 
  - Railway uses `Dockerfile` with `requirements-prod.txt` (minimal production dependencies) for faster builds
  - For local development, use `requirements.txt` which includes Jupyter and other dev tools
  - Check that all dependencies are in the appropriate requirements file
- **Build timeouts on Railway**: The Dockerfile approach with `requirements-prod.txt` significantly reduces build time (only ~12 packages vs 264)
- **Port errors**: Ensure backend uses `$PORT` environment variable (already configured in Dockerfile)

### Continuous Deployment

Both Railway and Vercel support automatic deployments:
- **Railway**: Automatically deploys on push to your main branch
- **Render**: Can be configured to auto-deploy on push
- **Vercel**: Automatically deploys on push to your main branch

## 5. Approach / Methodology

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

## 6. Next Steps (With More Time)

- In a real-world scenario, we would ask for more historical data and label true churn based on the business' definition. We would redo the analysis and have more robust features/action items.
- For the sake of time, I created static/deterministic recommendations for marketers to take for individual high-risk churn candidates, based on their segment labels (incorporating several key metrics for the customer). With more time, I would have either created personalized statistics (e.g. monthly basket size, purchase plotting by month), or run individual customer data through an LLM endpoint (didn't want to pay for LLM provider tokens and didn't have time to build this out) to provide highly personalized recommendations. If we had customer contact data, we could also generate outreach tailored to the customer.
- Because the raw dataset was so small (500K rows), we didn't need a DBMS hooked up. But if the customer wanted to scale this use case, we would hook up the upload to a DBMS and ingest data periodically/update the dashboard periodically using batching.
- Normally would look for customer differences by country, but decided to ignore this feature for the sake of time
- Right now, the CORS middleware accepts multiple origins. I left this for the sake of your ease/local deployment. In production, we would have to specify hosting routes.
- I used Cursor to produce a hypothetical test suite, which can be run via pytest. Some of the tests currently don't pass, which I would spend time addressing if this weren't a practice exercise.
