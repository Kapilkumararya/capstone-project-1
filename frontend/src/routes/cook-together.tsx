import { createFileRoute } from "@tanstack/react-router";
import { CookTogetherPage } from "@/components/cookai";
export const Route = createFileRoute("/cook-together")({
  head: () => ({ meta: [
    { title: "Cook Together — CookAI" }, { name: "description", content: "Cook one recipe together in a shared live kitchen session." },
    { property: "og:title", content: "Cook Together — CookAI" }, { property: "og:description", content: "Cook one recipe together in a shared live kitchen session." },
    { property: "og:type", content: "website" }, { name: "twitter:card", content: "summary_large_image" },
  ]}), component: CookTogetherPage,
});