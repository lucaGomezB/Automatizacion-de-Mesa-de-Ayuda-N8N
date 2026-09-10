// ESLint flat config — permissive baseline (C-09)
// Rules that the existing code violates en masse are set to "warn" or "off"
// to ensure CI passes from day one. Hardening is deferred to a future change.
import js from "@eslint/js";
import globals from "globals";
import reactPlugin from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import tsEslint from "typescript-eslint";

export default tsEslint.config(
  // Base JS recommended
  js.configs.recommended,
  // TypeScript recommended (type-checked would need parserOptions.project)
  ...tsEslint.configs.recommended,
  {
    plugins: {
      react: reactPlugin,
      "react-hooks": reactHooks,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2020,
      },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    settings: {
      react: { version: "detect" },
    },
    rules: {
      // React rules
      "react/react-in-jsx-scope": "off", // Not needed with React 17+ new JSX transform
      "react/prop-types": "off", // TypeScript covers this
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      // Permissive overrides for existing code patterns
      // These will be tightened in a future change
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": "warn",
      "@typescript-eslint/no-empty-object-type": "warn",
      "@typescript-eslint/no-require-imports": "warn",
      "no-unused-vars": "off", // Defer to @typescript-eslint/no-unused-vars
    },
  },
  {
    // Test files — relax further
    files: ["src/test/**/*", "**/*.test.{ts,tsx}", "**/*.spec.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": "off",
    },
  },
  {
    // Ignore build outputs and CJS config files that use CommonJS 'module' global
    ignores: ["dist/**", "node_modules/**", "coverage/**", "*.config.cjs", "vite.config.*", "postcss.config.*", "tailwind.config.*"],
  },
);
