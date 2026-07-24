import { useEffect, useState } from "react";
import "./App.css";
import { getFormOptions, getRecommendations } from "./services/api";
import type {
  FormOptions,
  ProductRecommendation,
  RecommendationRequest,
} from "./types/recommendation";

function App() {
  const [formOptions, setFormOptions] = useState<FormOptions | null>(null);

  const [formData, setFormData] = useState<RecommendationRequest>({
    age_range: "",
    skin_type: "",
    experience_level: "",
    coverage: "",
    max_price: 50,
    skin_tone: "",
    skin_concerns: [],
  });

  const [recommendations, setRecommendations] = useState<
    ProductRecommendation[]
  >([]);

  const [loading, setLoading] = useState(false);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [error, setError] = useState("");
  const [hasSubmitted, setHasSubmitted] = useState(false);

  useEffect(() => {
    async function loadFormOptions() {
      try {
        setOptionsLoading(true);
        setError("");

        const options = await getFormOptions();

        setFormOptions(options);

        setFormData((previousData) => ({
          ...previousData,
          age_range: options.age_ranges[0] ?? "",
          skin_type: options.skin_types[0] ?? "",
          experience_level: options.experience_levels[0] ?? "",
          coverage: options.coverage_preferences[0] ?? "",
          skin_tone: options.skin_tones[0] ?? "",
        }));
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("Failed to load form options.");
        }

        console.error(err);
      } finally {
        setOptionsLoading(false);
      }
    }

    loadFormOptions();
  }, []);

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

  const formIsReady =
    formOptions !== null &&
    formData.age_range !== "" &&
    formData.skin_type !== "" &&
    formData.experience_level !== "" &&
    formData.coverage !== "" &&
    formData.skin_tone !== "" &&
    formData.max_price > 0;

  return (
    <main className="app">
      <section className="hero">
        <h1>Makeup Recommendations</h1>
        <p>
          Get personalized product recommendations based on your skin profile,
          coverage preference, budget, and skin concerns.
        </p>
      </section>

      {optionsLoading && <p className="no-results">Loading form options...</p>}

      {!optionsLoading && formOptions && (
        <form className="recommendation-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Age Range
              <select
                name="age_range"
                value={formData.age_range}
                onChange={handleInputChange}
              >
                {formOptions.age_ranges.map((ageRange) => (
                  <option key={ageRange} value={ageRange}>
                    {ageRange}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Skin Type
              <select
                name="skin_type"
                value={formData.skin_type}
                onChange={handleInputChange}
              >
                {formOptions.skin_types.map((skinType) => (
                  <option key={skinType} value={skinType}>
                    {skinType}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Experience Level
              <select
                name="experience_level"
                value={formData.experience_level}
                onChange={handleInputChange}
              >
                {formOptions.experience_levels.map((experienceLevel) => (
                  <option key={experienceLevel} value={experienceLevel}>
                    {experienceLevel}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Coverage Preference
              <select
                name="coverage"
                value={formData.coverage}
                onChange={handleInputChange}
              >
                {formOptions.coverage_preferences.map((coveragePreference) => (
                  <option key={coveragePreference} value={coveragePreference}>
                    {coveragePreference}
                  </option>
                ))}
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
                {formOptions.skin_tones.map((skinTone) => (
                  <option key={skinTone} value={skinTone}>
                    {skinTone}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <fieldset className="concerns-section">
            <legend>Skin Concerns</legend>

            <div className="concern-grid">
              {formOptions.skin_concerns.map((concern) => (
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

          <button type="submit" disabled={loading || !formIsReady}>
            {loading ? "Generating..." : "Get Recommendations"}
          </button>

          {error && <p className="error">{error}</p>}
        </form>
      )}

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

                <p className="category">
                  {product.routine_step ? product.routine_step : product.category}
                </p>

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