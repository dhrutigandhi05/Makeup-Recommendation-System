import { useState } from "react";
import "./App.css";
import { getRecommendations } from "./services/api";
import type { RecommendationRequest, ProductRecommendation } from "./types/recommendation";

function App() {
  const [recommendations, setRecommendations] = useState<ProductRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sampleProfile: RecommendationRequest = {
    age_range: "Under 20",
    skin_type: "Oily",
    experience_level: "Beginner",
    coverage: "Light",
    max_price: 20,
    skin_tone: "Light",
    skin_concerns: ["Acne", "Dark Circles"],
  };

  async function handleTestRecommendation() {
    try {
      setLoading(true);
      setError("");

      const data = await getRecommendations(sampleProfile);
      setRecommendations(data.recommendations);
    } catch (err) {
      setError("Something went wrong while getting recommendations.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <h1>Makeup Recommendations</h1>
        <p>
          Personalized product recommendations based on skin type, skin tone,
          coverage preference, budget, and skin concerns.
        </p>

        <button onClick={handleTestRecommendation} disabled={loading}>
          {loading ? "Loading..." : "Test Recommendations"}
        </button>

        {error && <p className="error">{error}</p>}
      </section>

      {recommendations.length > 0 && (
        <section className="results">
          <h2>Recommended Products</h2>

          <div className="product-grid">
            {recommendations.map((product) => (
              <article className="product-card" key={product.product_name}>
                <p className="category">{product.category}</p>
                <h3>{product.product_name}</h3>
                <p>{product.brand}</p>
                <p>${product.price.toFixed(2)}</p>
                <p>Match Score: {(product.match_score * 100).toFixed(0)}%</p>
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