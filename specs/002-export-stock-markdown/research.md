# Research: Export Stock Data to Markdown

## Decision: Client-Side Multi-File Export

We will implement the export logic entirely on the client-side. When multiple stocks are selected, the system will iterate through the selection and trigger a separate download for each stock.

### Rationale
- **Efficiency**: Since the stock list data is already present in the frontend state, there's no need to hit the backend for a simple metadata export.
- **Responsiveness**: Immediate feedback for the user without network latency.
- **Simplicity**: No need for complex server-side file generation and temporary storage.

### Alternatives Considered

#### Server-Side Export (Rejected)
- **Reason**: Overkill for exporting simple metadata. Requires managing temporary files or complex streaming logic to handle multiple files (e.g., zipping them).
- **Complexity**: Adds backend load for a task the client can easily handle.

#### Consolidated Markdown (Rejected)
- **Reason**: Explicitly requested by the user to have individual files per stock.

## Decision: Browser Download Management

To handle multiple downloads, we will use a small delay (e.g., 100ms) between triggering each download. 

### Rationale
- **Browser Limits**: Triggering many downloads at once can sometimes cause browsers to ignore some of them or trigger security warnings. A small delay helps "spread" the requests.
- **User Experience**: Allows the browser's download manager to process them sequentially.

## Technical Details

### Markdown Table Format
We will use standard GFM (GitHub Flavored Markdown) format:
```markdown
| Kode | Nama Perusahaan | Sektor | Status Data |
| :--- | :--- | :--- | :--- |
| BBCA | Bank Central Asia Tbk. | Financials | 1250 data (2020-01-01 s/d 2024-05-01) |
```

### File Naming Convention
`[TICKER]-export-[YYYYMMDD-HHMMSS].md`

### Special Character Handling
We will use a simple regex to escape `|` characters in stock names or sectors to prevent table breakage.
