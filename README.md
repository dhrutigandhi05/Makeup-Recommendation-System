# VanityAI

A makeup recommendation app that suggests products based on a user’s beauty profile, preferences, budget, and skin concerns.

## Project Overview

This project helps users discover personalized makeup and skincare products by filling out a simple profile form. The system uses a hybrid recommendation approach that combines rule-based filtering, machine learning, NLP text features, review data, and product-user similarity scoring.

The goal of this project is to build a portfolio-ready full-stack application that demonstrates frontend development, backend API design, data cleaning, machine learning, natural language processing, recommendation systems, and explainable AI.

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

* Product name
* Brand
* Category
* Price
* Product link
* Match score
* Explanation for why the product was recommended

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### Machine Learning and Data

* pandas
* numpy
* scikit-learn
* TF-IDF Vectorizer
* LinearSVC
* cosine similarity
* Jupyter notebooks

### Database

* PostgreSQL

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

`https://makeup-api.herokuapp.com/`

### Sephora Products and Skincare Reviews Dataset

Used for:

* Product reviews
* Ratings
* Skin type information
* Skin tone information
* Review text
* Product metadata
* Sentiment patterns

`https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews`

## Machine Learning Approach

The recommendation engine combines:

* Rule-based filtering
* LinearSVC classification
* TF-IDF text features
* Product-user similarity scoring
* Review and rating-based scoring
* Price-based scoring

The LinearSVC model is used as a product suitability classifier. It predicts whether a product is suitable for a user profile.

## User Workflow

1. User opens the web app.
2. User fills out the beauty profile form.
3. User clicks **Get Recommendations**.
4. React sends the profile data to the FastAPI backend.
5. Backend validates the input.
6. Recommendation engine filters and scores products.
7. Backend returns ranked product recommendations.
8. Frontend displays the recommendations as product cards.

## App Architecture

```text
React Frontend
    ↓
FastAPI Backend
    ↓
Recommendation Engine
    ↓
Cleaned Product Dataset
    ↓
LinearSVC + TF-IDF + Scoring Rules
    ↓
Ranked Product Recommendations
```