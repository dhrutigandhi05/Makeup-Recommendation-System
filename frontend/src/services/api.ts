import type { RecommendationRequest, RecommendationResponse } from "../types/recommendation";

export async function getRecommendations(
  profile: RecommendationRequest
): Promise<RecommendationResponse> {
  const response = await fetch("/api/recommendations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch recommendations");
  }

  return response.json();
}