import { createFileRoute } from "@tanstack/react-router";
import { CookPage } from "@/components/cookai";

type CookSearch = {
  recipeId?: string;
};

export const Route = createFileRoute("/cook")({
  validateSearch: (search: Record<string, unknown>): CookSearch => ({
    recipeId: search.recipeId as string | undefined,
  }),
  head: () => ({ meta: [
    { title: "Smart Cooking Assistant — CookAI" }, { name: "description", content: "Hands-free, step-by-step cooking guidance." },
    { property: "og:title", content: "Smart Cooking Assistant — CookAI" }, { property: "og:description", content: "Hands-free, step-by-step cooking guidance." },
    { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" },
  ]}), component: CookPage,
});