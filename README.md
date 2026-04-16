# Breast Cancer Prediction

A machine learning system for classifying breast tumors as malignant or benign based on fine needle aspirate (FNA) features extracted from digitized cell images.

---

## App Interface

![Streamlit App](figures/app_screenshot.png)

The web application provides a physician-facing login interface with role-based access and real-time tumor classification powered by the trained Logistic Regression model.

---

## Dataset

- **Source:** Wisconsin Breast Cancer Dataset
- **Samples:** 569 records
- **Features:** 30 numerical features (mean, SE, worst values of radius, texture, perimeter, area, smoothness, compactness, concavity, etc.)
- **Target:** Binary classification — Malignant (1) / Benign (0)

---

## Machine Learning Approach

**Preprocessing**
- Dropped irrelevant columns (`id`, `Unnamed: 32`)
- Removed low-correlation features (`symmetry_se`, `texture_se`, `fractal_dimension_mean`, `smoothness_se`)
- Encoded target labels: Malignant = 1, Benign = 0
- Applied `StandardScaler` for feature normalization
- Train/test split: 70% / 30%

**Modeling**
- Primary model: Logistic Regression
- Additional explored: Decision Tree, Random Forest
- Dimensionality reduction: PCA (Part 2 notebook)
- Validation: 5-Fold Cross-Validation

**Evaluation Metrics**
- Accuracy, Precision, Recall, F1-Score
- Confusion Matrix
- ROC Curve / AUC Score

---

## Project Structure

```
Breast_Cancer_Prediction/
├── data/
│   └── breast_cancer.csv                        # Raw dataset
├── figures/
│   ├── app_screenshot.png                       # Streamlit app interface
│   ├── plot_1.png                               # Feature histograms
│   ├── plot_2.png                               # Diagnosis distribution
│   ├── plot_3.png                               # Correlation heatmap
│   ├── plot_4.png                               # Correlation with target
│   ├── plot_5.png                               # Confusion matrix
│   ├── plot_6.png                               # ROC curve
│   └── plot_7.png                               # Additional evaluation plot
├── BreastCancerPrediction_part1.ipynb           # EDA, preprocessing, modeling
├── breast-cancer-classification_part2.ipynb     # PCA analysis
├── Model.py                                     # Training pipeline script
├── app.py                                       # Streamlit web application
├── test_model.py                                # Model inference test script
├── save_figures_auto.py                         # Figure export utility
├── logistic_model.pkl                           # Serialized trained model
├── scaler.pkl                                   # Serialized StandardScaler
├── feature_names.json                           # Feature names used during training
├── patient_records.csv                          # Sample patient records
└── requirements.txt                             # Python dependencies
```


