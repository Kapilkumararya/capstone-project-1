<<<<<<< HEAD
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.
=======
# AI Cooking Platform 2.0

An intelligent cooking ecosystem combining computer vision, recipe recommendation, generative AI assistance, social recipe sharing, and collaborative cooking.

## Project Structure
- `frontend/`: The React application (Vite).
- `backend/`: The FastAPI backend with ML integration, database connections, and business logic.

## Setup Instructions

### Environment Variables
1. Copy the `.env.example` in the root folder to `.env` and fill in the necessary keys (like your LLM API Key).
2. Follow the setup instructions in the `backend/README.md` and `frontend/README.md` to configure their respective environments.

### Core Features
- **Phase 1**: Auth & Recipe Domain
- **Phase 2**: Ingredient Detection (YOLOv8)
- **Phase 3**: Recommendation Engine
- **Phase 4**: LLM Double-Check
- **Phase 5**: Cooking Assistant
- **Phase 6**: Public Community (Later)
- **Phase 7**: Collaborative Cooking with Google Meet (Later)
>>>>>>> 8be58c04d3cea44bd326ca9e8e20b4fcde8ac3fe
