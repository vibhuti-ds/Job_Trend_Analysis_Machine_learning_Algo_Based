# Job_Trend_Analysis_Machine_learning_Algo_Based
---
A machine learning-powered project built to analyze real-time job listing data from **Naukri.com**, this model predicts a candidate’s **expected pay grade** based on their profile. It includes full data cleaning, EDA, model training with multiple algorithms, and a **user-friendly web dashboard** built using HTML and CSS.

---

## Project Objective

The aim of this project is to:
- Analyze job market trends across India.
- Study how various features (like qualification, stream, location, role, company type) affect salary.
- Predict the expected **salary/pay grade** based on a candidate’s profile.
- Build a dashboard interface where users can enter their profile and instantly get a salary prediction.

---

## Data Source

  - Data collected through web scraping of job listings including:
  - `job_title`, `experience_required`, `location`, `salary`, `qualification`, `stream`, `industry`, `company_type`, etc.
-

---

## Project Workflow

### 🧩 Step 1: Data Scraping & Storage
- Used `requests` + `BeautifulSoup` to extract job listings from Naukri.com.
- Stored in a CSV with over 5,000+ rows and 15+ features.

---

### Step 2: Data Cleaning & Preprocessing
- Removed nulls and duplicates
- Standardized string formats (e.g., "B.Tech", "B. Tech", etc.)
- Converted categorical features into numerical using:
  - Label Encoding
  - One-Hot Encoding
- Converted salary range strings to mean numeric value
- Extracted and converted experience like `2-5 years` → `mean = 3.5`

---

### Step 3: Exploratory Data Analysis (EDA)
- Visualized:
  - Top-paying cities
  - Salary trends per industry
  - Role vs Pay Grade
  - Qualification vs Salary
- Charts used:
  - Bar plots, Box plots, Heatmaps, Distribution plots

---

### Step 4: Model Training
- Models used:
  1. **Linear Regression** → For predicting numeric pay grade
  2. **Logistic Regression** → For classifying into low/medium/high salary group
  3. **Decision Tree** → For both regression & classification tasks

- Split: `Train 80% / Test 20%`
- Metrics:
  - For regression: `R² Score`, `RMSE`
  - For classification: `Accuracy`, `Precision`, `Recall`, `F1-score`

 Models saved using `joblib` or `pickle` in the `/models/` directory.

---

### Step 5: Front-End Dashboard (HTML/CSS)

- Form inputs for:
  - Qualification
  - Stream/Specialization
  - City
  - Company Type (Startup, MNC, Public, etc.)
  - Desired Role/Post

 On submission, the model predicts the **expected pay grade** (e.g., ₹6.5 LPA).

> *(Currently connected through backend model locally. Flask or Streamlit integration optional.)*

---

## Project Structure

Job_Trend_Analysis_ML/
├── data/
│ └── job_data_cleaned.csv
├── models/
│ ├── linear_regression.pkl
│ ├── decision_tree.pkl
│ └── logistic_regression.pkl
├── dashboard/
│ ├── index.html
│ └── style.css
├── notebooks/
│ ├── 01_data_cleaning.ipynb
│ ├── 02_eda.ipynb
│ └── 03_model_training.ipynb
├── utils/
│ └── salary_prediction.py
├── app.py # (Flask or Streamlit backend - optional)
├── requirements.txt
└── README.md

yaml
Copy
Edit

---

## Tools & Technologies Used

| Category               | Tools / Libraries                               |
|------------------------|--------------------------------------------------|
| Language               | Python 3.x                                       |
| Data Handling          | Pandas, NumPy                                    |
| Data Visualization     | Matplotlib, Seaborn                              |
| ML Algorithms          | scikit-learn (LinearRegression, DecisionTree, etc.) |
| Web Scraping           | BeautifulSoup, Requests                          |
| Dashboard UI           | HTML5, CSS3                                      |
| Model Deployment       | (Optional) Flask / Streamlit                     |
| File Serialization     | Pickle / Joblib                                  |

---

## Example Prediction

**User Input:**
- Qualification: M.Tech
- Stream: Data Science
- City: Bengaluru
- Company Type: MNC
- Desired Role: Data Analyst

**Predicted Pay Grade:**
-  ₹8.4 – ₹9.5 LPA

---

## Future Scope

- Live dashboard deployment using Streamlit or Flask
- Use ensemble models (Random Forest, XGBoost)
- Add real-time scraping and auto-retraining pipeline
- Include NLP for analyzing job descriptions
- Map-based insights for city-wise opportunities

---

## Author

**Vibhuti Awasthi**  
    Lucknow, India  
    MSc in Statistics (2025) – Dr. Shakuntala Mishra National Rehabilitation University  
    Interests: Data Science | Machine Learning | Predictive Modeling | Dashboarding  
https://github.com/vibhutiawasthi
vibhuti.awasthi@outlook.com 

---

## License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this project with attribution.

