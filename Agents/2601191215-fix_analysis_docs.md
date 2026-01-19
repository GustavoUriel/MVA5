# 2601191215-fix_analysis_docs.md

Date: 2026-01-19 12:15 (YYMMDDHHmm = 2601191215)
Author: automated agent

## Intent
Synchronize top-level analysis documentation files with the detailed per-step documents found in architecture/analysis (files numbered 110..410). Keep edits minimal and non-invasive; add alignment notes so implementers know these files were reviewed and synced.

## Files updated
- architecture/analysis/DataAnalysis.md — added short note indicating synchronization with step files (110..410).
- architecture/analysis/DataFlow.md — added note about PipelineData structure alignment.
- architecture/analysis/EventDrivenStepCommSys.md — added note that event names/callbacks align with step docs.
- architecture/analysis/pipeline_explanation.md — added synchronization note.
- architecture/analysis/RequiredOutputs.md — added note about output naming consistency.
- architecture/analysis/ResultsComparison.md — created/updated to reflect comparison output spec and link to MVA comparison doc.
- architecture/analysis/Sample_Timepoints_Comparison.md — added note aligning the UI doc with `320.TimePointsComparison.md` and timepoint naming.

## Rationale
The numbered per-step files (110.DataSourcesSelect.md, 120.ExtremePointsSelection.md, 130.DataCuration.md, 140.AttributeGroupSelection.md, 210.AttributeDiscarding.md, 220.MicrobialDiscarding.md, 240.MicrobialGrouping.md, 250.MVAMethods.md, 310.PopulationSubgroupsComparison.md, 320.TimePointsComparison.md, 330.MVAMethodsComparison.md, 410.OutputOptions.md) contain authoritative and detailed descriptions. The top-level overview files needed brief, explicit notes to confirm they were reviewed and are aligned, so implementers reading either set of files see consistent terminology and file naming.

## Summary of edits
- Inserted short alignment/consistency notes into the seven target files.
- Did not rewrite substantive content — changes are minimal and documentational only.

## Next steps (suggested)
- Run a quick doc lint or search for inconsistent stage names to flag any remaining mismatches.
- Optionally, generate a small script that validates `PipelineData` keys are present in implementation.

## Final summary
Synchronized high-level analysis docs with detailed per-step documents to reduce ambiguity and help implementers follow consistent names and output expectations.
