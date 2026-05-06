# Implementation Plan: Export Stock Data to Markdown

**Branch**: `002-export-stock-markdown` | **Date**: 2026-05-06 | **Spec**: [specs/002-export-stock-markdown/spec.md](spec.md)

## Summary

Implement a multi-file Markdown export feature for stock data. Users will select stocks via checkboxes in the `StockListPage`, and clicking the export button (enabled only when selection exists) will trigger individual `.md` file downloads for each selected stock. The export is handled entirely on the client-side for performance and simplicity.

## Technical Context

**Language/Version**: Python 3.12+ (Backend), React 18+ (Frontend)
**Primary Dependencies**: FastAPI, TanStack Query, Tailwind CSS, shadcn/ui
**Storage**: PostgreSQL (source of stock data)
**Testing**: pytest (Backend), Vitest/React Testing Library (Frontend)
**Target Platform**: Web Browser
**Project Type**: Web Application
**Performance Goals**: Instant file generation and download triggering
**Constraints**: Browser multiple-download limits/permissions
**Scale/Scope**: Handles selection from paginated stock list (current view)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **API-First Architecture**: Yes. Uses existing `/api/v1/stocks` endpoints.
2. **Data Integrity**: Yes. Formatting numeric values correctly in Markdown.
3. **Test-First**: Yes. Plan includes updating `DataTable` tests and adding export logic tests.
4. **Simplicity & YAGNI**: Yes. Client-side implementation avoids unnecessary backend complexity.
5. **Naming & Language**: Yes. Code in English, UI in Bahasa Indonesia ("Ekspor ke Markdown").

## Project Structure

### Documentation (this feature)

```text
specs/002-export-stock-markdown/
├── plan.md              # This file
├── research.md          # Research on browser downloads and MD format
├── data-model.md        # UI state and MD schema
├── quickstart.md        # User and developer guide
├── contracts/           
│   └── ui-contract.md   # DataTable and export utility contracts
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── DataTable.tsx       # To be updated with selection support
│   │   └── StockExportButton.tsx # New component
│   ├── lib/
│   │   └── export-utils.ts     # New utility for MD generation
│   ├── pages/
│   │   └── StockImport/
│   │       └── StockListPage.tsx # Updated to use selection and button
│   └── types/
│       └── index.ts            # Ensure Stock type is accurate
```

**Structure Decision**: Web application structure with updates to shared components and a new utility.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
