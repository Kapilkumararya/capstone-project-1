# Kitchen AI Magic

Design a modern, warm, food-focused web app called CookAI — an AI-powered cooking platform that detects ingredients from a photo, recommends recipes, guides users step-by-step while cooking, hosts a public recipe community, and supports collaborative cooking sessions over video call.

Overall style direction: Clean UI, rounded cards, beautiful food photography, soft subtle animations, warm and fresh — not overly techy or cold. Feels modern, approachable, and AI-powered without looking like generic SaaS. Color palette: forest green as primary/brand color, cream/off-white background, warm accent colors (mustard yellow, terracotta orange, brick red) used sparingly for tags, badges, and highlights. Generous whitespace, soft shadows, pill-shaped buttons and tags, hand-drawn leaf/plant doodle accents in empty corners for warmth. Typography: a clean modern sans-serif, bold confident headlines, friendly body text.

Left sidebar navigation (persistent across all screens): Logo "CookAI" with a chef-hat icon, then Home, AI Recipes, Community, Cook Together, Saved, a divider labeled "Your Pantry," then Dietary Preferences and Settings. Active item highlighted with a soft green pill background.

Generate the following 5 screens:

1. Home / Landing

Large friendly headline "What's in your kitchen?" with a subheadline about snapping a photo to detect ingredients and get recipe help. A prominent drag-and-drop / "Upload a photo" card with a camera icon, plus quick-try ingredient chips (tomatoes, eggs, spinach, chicken). Beside it, a warm lifestyle photo of fresh produce in a basket with a small annotation callout "AI detects your ingredients" pointing at the produce. Below the fold, four feature highlight cards in a row: AI Recipe Recommendations, Cooking Assistant, Recipe Community, Cook Together (Google Meet) — each with a small icon and one-line description.

2. AI Recipe Discovery

Header "AI Recipe Discovery." Left panel "Detected Ingredients" showing a food photo thumbnail plus a tag list of detected items (tomato, egg, spinach, onion, garlic), each removable. Right panel "Your Preferences" showing active filter chips (Vegetarian, Quick <30 mins, High Protein, Easy) with an Edit link. Below, a "Top Recipe Recommendations" section with an "AI Verified" badge and a sort dropdown ("Best Match"), showing a horizontal row of recipe cards — each with a food photo, save/heart icon, title, time + difficulty metadata, and a match-percentage badge (e.g. "90% match") in green.

3. Cooking Assistant (step-by-step + chat)

Split-screen layout. Left: active recipe card (photo, title, dietary tag, time, difficulty) with tabs for Ingredients / Steps / Nutrition, an ingredient checklist, and a step progress header ("Step 3 of 7") with Previous/Next buttons and the current step's instructions. Right: a chat panel labeled "AI Cooking Assistant" with a conversational back-and-forth (user question, AI response with a helpful sparkle icon), quick suggestion chips ("What can I substitute?", "Next step", "Tips for better flavour"), and a message input bar at the bottom.

4. Community

Header "Community" with tabs (For You / Following / Trending) and a green "Create Post" button top-right. Center feed: recipe post cards showing author avatar + name + time + a dietary tag + follow button, a short caption, a large recipe photo, and an engagement row (upvote count, comment count, save icon) plus a couple of visible comment previews. Right sidebar: "Popular Creators" list (avatar, name, follower count, follow button) and a "Trending Recipes" list (small thumbnail, title, upvote count).

5. Cook Together (collaborative session via Google Meet)

Header showing session name ("Pasta Night with Friends"), date/time, duration, and a green "Join Meet" button linked to a Google Meet URL. Left: a video-call grid of 3–4 participant tiles with names and mute/camera icons, plus call controls (mic, camera, end-call) along the bottom. Right: a "Shared Recipe" card (photo, title, time, difficulty) with a checklist of shared steps that participants can tick off together, and below it a live group chat panel with a message input.

Global notes for Stitch:

Keep the sidebar and header consistent across all 5 screens.

Use realistic-looking food photography placeholders (fresh vegetables, plated pasta, salads, egg dishes).

Badges/tags (match %, AI Verified, dietary labels, difficulty) should use small rounded pill shapes in the accent colors.

Make it responsive-friendly: sidebar collapses on smaller widths.

This is a web app (desktop-first), not a native mobile app.

Why these screens/details were included

Pulled directly from your project blueprint so the generated UI actually maps to real backend features (not just decoration):

ScreenMaps to blueprint moduleHome / LandingEntry point to ingredient upload → YOLOv8 detection flowAI Recipe DiscoveryIngredient Intelligence + Recommendation Engine + LLM Double-Check ("AI Verified" badge = the LLM verification layer)Cooking AssistantContext-Aware Cooking Assistant module (LLM + structured recipe/session context)CommunityPublic Community module — posts, votes, comments, follows, feed viewsCook TogetherCollaborative Cooking module — Google Calendar/Meet integration, session participants, shared recipe steps

I have attached the Inspo images. Keep the theme and elements exactly like them. Also build this project in Vite

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/7d1e553b-558c-4e4a-93bd-5a0806bc4526).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
