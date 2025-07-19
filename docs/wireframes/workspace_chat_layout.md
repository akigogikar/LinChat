# Workspace Chat Layout

This wireframe describes the interface for chats inside a workspace. It covers how to organize private vs. shared threads, export features, and how to display results from the Rust-based analysis service while keeping generated source code hidden.

## Thread List

```
+-------------------------------------------------------+
| [Workspace name]                   [Create Thread +] |
+-------------------------------------------------------+
|  Private Threads                                       |
|    > Research idea                                     |
|    > Meeting notes                                     |
|                                                       |
|  Shared Threads                                        |
|    # Market analysis                                   |
|    # Design review                                     |
+-------------------------------------------------------+
```

- The sidebar shows two sections: **Private Threads** and **Shared Threads**.
- Private threads appear with a `>` prefix. Shared threads use a `#` prefix.
- Clicking a thread loads its messages in the main area.
- A `Create Thread` button lets users start a new thread and choose whether it is private or shared with the workspace.

## Chat Window

```
+-------------------------------------------------------+
| Thread title                          [Share/Private] |
+-------------------------------------------------------+
|                                                       |
|  [Messages scroll here]                               |
|                                                       |
|  [Results Panel]                                      |
|  +-----------------------------------------------+    |
|  |  Charts / tables from Rust analysis service   |    |
|  +-----------------------------------------------+    |
|                                                       |
|  [Message input field ___________________________]    |
|  [Send]  [Export PDF] [Export Excel]                  |
+-------------------------------------------------------+
```

- The main pane shows the chat messages and a bottom input field.
- The **Results Panel** embeds charts or tables produced by the Rust service. Only the rendered output is shown—no generated code is visible to the user.
- Export buttons allow downloading the current conversation in **PDF** or **Excel** format.
- A toggle next to the thread title switches between private and shared status.

## Export Behavior

1. **Export PDF** – Creates a PDF containing the chat transcript and results panel.
2. **Export Excel** – Generates an XLSX file with any tables from the analysis service. If no tables are present, the file contains a summary of messages instead.

Use the existing `/export/pdf` and `/export/excel` backend endpoints to implement these features. The frontend `ExportButtons` component can be extended to support Excel in addition to PDF.

## Results from the Rust Service

- Charts and tables are served as images or HTML from `/analysis/results`. The client inserts these into the **Results Panel**.
- Raw code snippets returned by the Rust service must be filtered out on the backend. Only the visual output or plain-text explanations should be sent to the browser.
- Errors from the analysis service should display inline in the panel with a clear message.

These wireframes provide guidance on updating the frontend to support workspaces and integrate results from the Rust analysis engine securely.

