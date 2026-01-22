### 2026-01-22 12:00 - Keep analysis editor open on Save

Summary:
- Changed frontend save behavior so that pressing "Save" stores the analysis but keeps the Analysis Configuration editor open.

Files modified:
- app/static/js/dataset_analysis.js: removed call to `cancelAnalysisEdit()` inside `saveAnalysis()` so the editor remains open after saving. The analysis list is still refreshed.

Why:
- User asked that saving the analysis should not close the configuration section; they want it to remain open until they explicitly press Close.

What I changed:
- In `saveAnalysis()`, removed `this.cancelAnalysisEdit()` and left `this.loadAnalysisList()` so the saved item appears in the list without closing the editor.

Verification / Next steps:
- Open the application, go to Analysis Configuration, change something and press Save — the success alert should appear, the saved analysis will be visible in the list, and the editor should remain open.

Brief log of action:
- Performed minimal frontend edit to alter save handler behavior.

Final summary:
- Save now keeps the Analysis Configuration open; user closes it manually.
