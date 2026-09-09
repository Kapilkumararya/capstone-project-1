# CookAI web app

## Overview
Build a desktop-first CookAI experience closely matching the supplied references: warm cream surfaces, forest-green navigation and actions, realistic food imagery, soft cards, compact pill badges, and responsive collapsing navigation.

## Screens
- **Home** at `/`: ingredient-photo upload, produce image with AI callout, kitchen stats, four feature cards, and trending recipes.
- **AI Recipes** at `/recipes`: detected ingredients, preferences, AI-verified recommendations, save controls, and a refinement bar.
- **Cooking Assistant** at `/cook`: active recipe summary, tabs, ingredient checklist, step progress, instructions, and contextual assistant chat.
- **Community** at `/community`: feed tabs, post composer action, recipe posts, engagement controls, comments, popular creators, and trending recipes.
- **Cook Together** at `/cook-together`: session header, participant video grid, call controls, shared recipe checklist, and live chat.
- Add simple Saved, Dietary Preferences, and Settings screens so every persistent navigation item works.

## Shared experience
- Persistent responsive sidebar with the CookAI chef-hat mark, active-page pill, pantry grouping, and compact mobile drawer.
- Shared top search bar, notifications, and chef profile area across primary screens.
- Reusable recipe cards, tags, icon controls, sidebar, top bar, and food-image treatments.
- Local interactions for tabs, checklist items, saving, upload selection, chat inputs, feed filters, and call controls.

## Visual system
- Define all colors, typography, shadows, radii, and animation timing as semantic tokens.
- Use a warm off-white and mint canvas, dark forest green, plus restrained mustard, terracotta, and brick accents.
- Use generated food and cooking photography rather than embedding the supplied reference screenshots.
- Add subtle leaf doodles and gentle motion while respecting reduced-motion preferences.

## Technical details
- Keep the existing TanStack Start application running through Vite and use file-based routes for every screen.
- Add route-specific page titles, descriptions, Open Graph metadata, and accessible image descriptions.
- Verify the responsive layout and key interactions in the running preview on desktop and mobile widths.
