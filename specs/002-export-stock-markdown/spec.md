# Feature Specification: Export Stock Data to Markdown

**Feature Branch**: `002-export-stock-markdown`  
**Created**: 2026-05-06  
**Status**: Draft  
**Input**: User description: "I’d like a new feature that adds an export button to export specific (selected) stock data into a Markdown file containing neatly formatted tables."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Export Selected Stocks Individually (Priority: P1)

As a user viewing a list of stocks, I want to select specific stocks and export each one into its own separate Markdown file so that I have organized documentation for every individual stock I research.

**Why this priority**: Core functionality of the feature. It defines the selection-based export logic and the multi-file generation requirement.

**Independent Test**: Select two stocks from a list, click the export button, and verify that two separate `.md` files are downloaded, each containing the data for exactly one of the selected stocks.

**Acceptance Scenarios**:

1. **Given** a list of stocks with selection checkboxes, **When** no stocks are selected, **Then** the "Export to Markdown" button MUST be disabled.
2. **Given** a list of stocks, **When** I select 1 stock and click "Export to Markdown", **Then** 1 file named `[SYMBOL]-export-[timestamp].md` is downloaded.
3. **Given** a list of stocks, **When** I select 3 stocks and click "Export to Markdown", **Then** 3 separate Markdown files are triggered for download, one for each selected stock.

---

### Edge Cases

- **Multiple concurrent downloads**: How does the browser handle triggering 10+ downloads simultaneously? (System should handle this gracefully, perhaps with a slight delay or batching if necessary).

- **No stocks in list**: What happens when the user tries to export from an empty list? (The button should be disabled or show an error).
- **Large number of stocks**: How does the system handle exporting 100+ stocks? (Should be handled gracefully, perhaps with a loading indicator if processing takes time).
- **Special characters in stock names**: Ensure Markdown table formatting doesn't break if a stock name contains characters like `|` or `*`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a way for users to select specific stocks (e.g., checkboxes).
- **FR-002**: System MUST display an "Export" button prominently near the stock list, which is ONLY enabled when at least one stock is selected.
- **FR-003**: System MUST generate a separate Markdown file for EACH selected stock, containing a formatted table of its data.
- **FR-004**: System MUST include key data fields in the export: Symbol, Company Name, Current Price, Day Change (%), and Volume.
- **FR-005**: System MUST trigger individual browser downloads for each generated `.md` file.
- **FR-006**: The Markdown table MUST use standard GitHub Flavored Markdown (GFM) syntax for tables.
- **FR-007**: System MUST escape special Markdown characters in data values to prevent table breakage.

### Key Entities *(include if feature involves data)*

- **StockData**: Represents the information for a single stock (Symbol, Name, Price, etc.).
- **ExportJob**: Represents the transient state of an export operation (Selected IDs, generated content).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the export process (selection to download) in under 10 seconds.
- **SC-002**: Generated Markdown files are valid GFM and render correctly in standard viewers (e.g., VS Code, GitHub).
- **SC-003**: Exported data exactly matches the values displayed in the UI at the time of export.

## Assumptions

- **Assumption 1**: The export is handled entirely on the client-side using available state.
- **Assumption 2**: Standard browser download mechanisms are sufficient (no server-side generation required unless data is too large).
- **Assumption 3**: The user prefers individual files over a single consolidated file when multiple stocks are selected.

