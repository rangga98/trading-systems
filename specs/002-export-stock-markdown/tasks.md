# Tasks: Export Stock Data to Markdown

**Input**: Design documents from `/specs/002-export-stock-markdown/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 [P] Create export utility file in `frontend/src/lib/export-utils.ts`
- [x] T002 [P] Create export button component in `frontend/src/components/StockExportButton.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Implement Markdown table generation logic in `frontend/src/lib/export-utils.ts`
- [x] T004 Implement multi-file download trigger with delay in `frontend/src/lib/export-utils.ts`
- [x] T005 Update `frontend/src/components/DataTable.tsx` to support row selection (checkboxes, select all)
- [x] T006 [P] Add selection state management support to `frontend/src/components/DataTable.tsx` via props

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Export Selected Stocks Individually (Priority: P1) 🎯 MVP

**Goal**: Select stocks via checkboxes and export each to an individual Markdown file.

**Independent Test**: Select multiple stocks in the list, click the export button, and verify that multiple `.md` files are downloaded, each containing one stock's data.

### Implementation for User Story 1

- [x] T007 [US1] Implement selection state management in `frontend/src/pages/StockImport/StockListPage.tsx`
- [x] T008 [US1] Pass selection props to `DataTable` in `frontend/src/pages/StockImport/StockListPage.tsx`
- [x] T009 [US1] Implement `StockExportButton` with disabled state logic in `frontend/src/components/StockExportButton.tsx`
- [x] T010 [US1] Add `StockExportButton` to the header of `frontend/src/pages/StockImport/StockListPage.tsx`
- [x] T011 [US1] Connect `StockExportButton` to the export utility in `frontend/src/pages/StockImport/StockListPage.tsx`
- [x] T012 [US1] Ensure special characters are escaped in Markdown generation in `frontend/src/lib/export-utils.ts`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T013 [P] Update frontend types to ensure `Stock` includes all fields needed for export in `frontend/src/types/index.ts`
- [x] T014 Run validation against `specs/002-export-stock-markdown/quickstart.md`
- [x] T015 [P] Add loading indicator to export button for large selections in `frontend/src/components/StockExportButton.tsx`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: Depends on Foundational phase completion.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2).

### Parallel Opportunities

- T001 and T002 can be created in parallel.
- T013 and T015 can be done in parallel.

---

## Parallel Example: Setup & Foundational

```bash
# Initialize components and utils:
Task: "Create export utility file in frontend/src/lib/export-utils.ts"
Task: "Create export button component in frontend/src/components/StockExportButton.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (MVP)
4. **STOP and VALIDATE**: Test selection and multi-file export.

---

## Notes

- All implementation is client-side as per `research.md`.
- No new backend endpoints or models are required.
- Standard GFM table syntax must be used.
