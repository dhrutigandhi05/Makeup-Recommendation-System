import type {
  FormOptions,
  RecommendationRequest,
  RecommendationResponse,
} from "../types/recommendation";

type FastApiValidationError = {
  detail?: {
    loc?: string[];
    msg?: string;
    type?: string;
  }[];
};

function formatApiError(errorData: unknown): string {
  const parsedError = errorData as FastApiValidationError;

  if (Array.isArray(parsedError.detail)) {
    return parsedError.detail
      .map((error) => {
        const fieldName = error.loc?.slice(1).join(".") || "field";
        return `${fieldName}: ${error.msg}`;
      })
      .join(" ");
  }

  if (
    typeof errorData === "object" &&
    errorData !== null &&
    "detail" in errorData
  ) {
    const detail = (errorData as { detail: unknown }).detail;

    if (typeof detail === "string") {
      return detail;
    }
  }

  return "Failed to fetch recommendations.";
}

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
    let errorMessage = "Failed to fetch recommendations.";

    try {
      const errorData = await response.json();
      errorMessage = formatApiError(errorData);
    } catch {
      errorMessage = "Failed to fetch recommendations.";
    }

    throw new Error(errorMessage);
  }

  return response.json();
}

export async function getFormOptions(): Promise<FormOptions> {
  const response = await fetch("/api/form-options");

  if (!response.ok) {
    throw new Error("Failed to fetch form options.");
  }

  return response.json();
}