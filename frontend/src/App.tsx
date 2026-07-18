import { useState } from "react";
import "./App.css";
import { getRecommendations } from "./services/api";
import type { ProductRecommendation, RecommendationRequest } from "./types/recommendation";

const skinConcernOptions = [
  "Acne",
  "Dark Circles",
  "Hyperpigmentation",
  "Redness/Rosacea",
  "Wrinkles",
  "Sensitive Skin",
];

function App() {
  const [formData, setFormData] = useState<RecommendationRequest>({
    age_range: "Under 20",
    skin_type: "Oily",
    experience_level: "Beginner",
    coverage: "Light",
    max_price: 20,
    skin_tone: "Light",
    skin_concerns: [],
  });

  const [recommendations, setRecommendations] = useState<ProductRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSubmitted, setHasSubmitted] = useState(false);

  function handleInputChange(
    event: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>
  ) {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: name === "max_price" ? Number(value) : value,
    }));
  }

  function handleConcernChange(concern: string) {
    setFormData((previousData) => {
      const alreadySelected = previousData.skin_concerns.includes(concern);

      return {
        ...previousData,
        skin_concerns: alreadySelected
          ? previousData.skin_concerns.filter((item) => item !== concern)
          : [...previousData.skin_concerns, concern],
      };
    });
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");
      setHasSubmitted(true);
      const data = await getRecommendations(formData);
      setRecommendations(data.recommendations);
    } catch (err) {
      setRecommendations([]);

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong while getting recommendations.");
      }

      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <h1>VanityAI</h1>
        <p>
          Get personalized product recommendations based on your skin profile,
          coverage preference, budget, and skin concerns.
        </p>
      </section>

      <form className="recommendation-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Age Range
            <select
              name="age_range"
              value={formData.age_range}
              onChange={handleInputChange}
            >
              <option>Under 20</option>
              <option>20-30</option>
              <option>30-40</option>
              <option>40+</option>
            </select>
          </label>

          <label>
            Skin Type
            <select
              name="skin_type"
              value={formData.skin_type}
              onChange={handleInputChange}
            >
              <option>Oily</option>
              <option>Dry</option>
              <option>Combination</option>
              <option>Normal</option>
              <option>Sensitive</option>
            </select>
          </label>

          <label>
            Experience Level
            <select
              name="experience_level"
              value={formData.experience_level}
              onChange={handleInputChange}
            >
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
          </label>

          <label>
            Coverage Preference
            <select
              name="coverage"
              value={formData.coverage}
              onChange={handleInputChange}
            >
              <option>Light</option>
              <option>Medium</option>
              <option>Full</option>
            </select>
          </label>

          <label>
            Maximum Price Per Product
            <input
              type="number"
              name="max_price"
              min="1"
              max="500"
              step="1"
              value={formData.max_price}
              onChange={handleInputChange}
            />
          </label>

          <label>
            Skin Tone
            <select
              name="skin_tone"
              value={formData.skin_tone}
              onChange={handleInputChange}
            >
              <option>Light</option>
              <option>Medium</option>
              <option>Deep</option>
            </select>
          </label>
        </div>

        <fieldset className="concerns-section">
          <legend>Skin Concerns</legend>

          <div className="concern-grid">
            {skinConcernOptions.map((concern) => (
              <label className="checkbox-label" key={concern}>
                <input
                  type="checkbox"
                  checked={formData.skin_concerns.includes(concern)}
                  onChange={() => handleConcernChange(concern)}
                />
                {concern}
              </label>
            ))}
          </div>
        </fieldset>

        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Get Recommendations"}
        </button>

        {error && <p className="error">{error}</p>}
      </form>

      {hasSubmitted && !loading && recommendations.length === 0 && !error && (
        <p className="no-results">
          No products matched your current filters. Try increasing your max price
          or selecting fewer concerns.
        </p>
      )}

      {recommendations.length > 0 && (
        <section className="results">
          <h2>Recommended Products</h2>

          <div className="product-grid">
            {recommendations.map((product) => (
              <article className="product-card" key={product.product_name}>
                {product.image_link && (
                  <img
                    className="product-image"
                    src={product.image_link}
                    alt={product.product_name}
                  />
                )}

                <p className="category">{product.routine_step ? product.routine_step : product.category}</p>
                <h3>{product.product_name}</h3>
                <p className="brand">{product.brand}</p>
                <p className="price">${product.price.toFixed(2)}</p>
                <p className="score">
                  Match Score: {(product.match_score * 100).toFixed(0)}%
                </p>
                {product.ml_score !== undefined && product.ml_score !== null && (
                  <p className="score">
                    ML Suitability: {(product.ml_score * 100).toFixed(0)}%
                  </p>
                )}
                <p>{product.reason}</p>
                <a href={product.url} target="_blank" rel="noreferrer">
                  View Product
                </a>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

export default App;