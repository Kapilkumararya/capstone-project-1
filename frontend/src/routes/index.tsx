import { createFileRoute } from "@tanstack/react-router";
import { HomePage } from "@/components/cookai";

// No head() here: the home route inherits title/description/og/twitter from
// __root.tsx, and ships no og:image so serve-time hosting can inject the
// project's social preview (explicit og:image or latest screenshot).
export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "CookAI — What's in your kitchen?" },
    { name: "description", content: "Photograph your pantry, discover matching recipes, and cook with intelligent guidance." },
    { property: "og:title", content: "CookAI — What's in your kitchen?" },
    { property: "og:description", content: "Photograph your pantry, discover matching recipes, and cook with intelligent guidance." },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary_large_image" },
  ]}),
  component: HomePage,
});
