# VanityAI

VanityAI is a full-stack AI/ML makeup recommendation app that suggests products based on a user’s beauty profile, preferences, budget, and skin concerns. The app takes a user profile, scores available products using a hybrid recommendation system, and returns a curated makeup routine with product cards, match scores, ML suitability scores, and plain-English explanations.

## Project Overview

VanityAI helps users discover personalized makeup products by filling out a simple beauty profile form. The system combines rule-based recommendation logic with a trained machine learning model to rank products based on user preferences and product suitability.

The goal of this project is to demonstrate a complete portfolio-ready AI/ML application, including frontend development, backend API design, database integration, data cleaning, machine learning, NLP text features, recommendation logic, and explainable product recommendations.

## Features

Users can enter:

* Age range
* Skin type
* Skin tone
* Makeup experience level
* Coverage preference
* Skin concerns
* Maximum product price

The app returns recommended products with:

* Routine step
* Product name
* Brand
* Category
* Price
* Product image
* Product link
* Match score
* ML suitability score
* Explanation for why the product was recommended

## Tech Stack

### Frontend
* React
* TypeScript
* CSS

### Backend
* Python
* FastAPI
* Pydantic
* Uvicorn
* SQLAlchemy

### Database
* PostgreSQL
* Docker

### Machine Learning and Data
* pandas
* numpy
* scikit-learn
* TF-IDF Vectorizer
* LinearSVC
* CalibratedClassifierCV
* joblib

## Data Sources
### Makeup API

Used for makeup product information such as:

* Product names
* Brands
* Product types
* Prices
* Product links
* Product images
* Categories
* Descriptions
* Tags

Source: `https://makeup-api.herokuapp.com/`

### Sephora Products and Skincare Reviews Dataset

Used for model training and product-profile suitability learning.

The dataset provides:

* Product reviews
* Ratings
* Skin type information
* Skin tone information
* Review text
* Product metadata
* User recommendation indicators

Source: `https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews`

## Machine Learning Approach

VanityAI uses a hybrid recommendation approach that combines rule-based scoring with a trained ML suitability model.

The recommendation system considers:

* Product price
* Product category
* Product type
* Skin type compatibility
* Skin tone profile
* Coverage preference
* Makeup experience level
* Skin concerns
* Product descriptions and tags
* Review-based suitability patterns

The improved ML model is trained on an aggregated product-profile suitability dataset. Instead of training only on individual review text, the dataset groups reviews by:

* Product
* Skin type
* Skin tone

For each product-profile group, the system calculates:

* Review count
* Average rating
* Recommendation rate
* Suitability label

This allows the model to learn a more realistic recommendation task:

```text
Product + skin type + skin tone → suitable or not suitable
```
The model uses:

* TF-IDF text features
* Calibrated LinearSVC classification
* Product metadata
* Skin profile text
* Review-based suitability labels
* Model Performance

## Recommendation Workflow
1. The user opens the web app.
2. The frontend loads valid form options from the FastAPI backend.
3. The user fills out their beauty profile.
4. The user clicks Get Recommendations.
5. React sends the user profile to the FastAPI backend.
6. The backend validates the request using Pydantic.
7. The recommendation engine retrieves matching products from PostgreSQL.
8. Products are scored using rule-based logic.
9. The ML model predicts product-profile suitability.
10. Rule scores and ML scores are combined into a final match score.
11. The backend returns a curated product routine.
12. The frontend displays the recommendations as product cards.

## App Architecture
React Frontend
    ↓
FastAPI Backend
    ↓
PostgreSQL Database
    ↓
Recommendation Engine
    ↓
Rule-Based Scoring + ML Suitability Model
    ↓
Ranked Product Recommendations
    ↓
Product Cards with Explanations