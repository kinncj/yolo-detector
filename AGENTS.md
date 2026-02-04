# Agents and Skills

## Agents
1. DetectionAgent
   - Loads YOLO models and runs inference.
   - Owns device selection and inference parameters.
   - Provides structured logging for model resolution and loading.
   - Implemented in yolodetector/models/detector.py.

2. AnnotationAgent
   - Renders bounding boxes, labels, and critical markers.
   - Owns palette selection and styling.
   - Logs frame annotation statistics for observability.
   - Implemented in yolodetector/annotation/renderer.py.

3. VideoIOAgent
   - Discovers input files and manages output paths.
   - Owns video reader/writer setup and validation.
   - Logs file operations and FPS fallback decisions.
   - Implemented in yolodetector/video/io.py.

4. ReportingAgent
   - Aggregates detection statistics and critical findings.
   - Produces per-video and global summaries.
   - Exports structured JSON reports for programmatic consumption.
   - Logs summary statistics for monitoring integration.
   - Implemented in yolodetector/reporting/summary.py.

5. ConfigAgent
   - Manages configuration models and validation.
   - Owns dataclass definitions and factory methods.
   - Validates thresholds and file paths.
   - Implemented in yolodetector/config.py.

## Skills
- Model selection (YOLO26 family, COCO constraints)
- Performance tuning (imgsz, device, frame handling)
- Robust IO handling (missing files, FPS fallbacks)
- Structured logging and observability (DEBUG/INFO/WARNING levels)
- JSON export for programmatic report consumption
- Comprehensive test coverage (unit + integration tests)
- Clear telemetry and summaries
- SOLID refactoring and clean separation of concerns

## Update Policy
- When adding new pipeline responsibilities, extend the Agents list first.
- Keep skills aligned with real capabilities in main.py.

## Shared Standards (Keep in Sync with CLAUDE.md)
- Keep responsibilities separated (config, inference, annotation, IO, reporting).
- Prefer dependency injection for model and config usage.
- Avoid hard-coded paths in logic; expose them via CLI flags with sane defaults.
- Preserve stable CLI behavior for existing users.
- BusinessRepo lens for decisions unless clearly not applicable.
- Clean Architecture, SOLID, composition over inheritance.
- Testability, observability, reliability, security by default.

## Communication Preferences (Summary)
- Prefer clear, concise, and practical responses.
- Use short sentences and structured formatting.
- Avoid marketing language, hype, filler, or motivational tone.
- Be direct about assumptions, constraints, and trade-offs.
- Optimize for clarity and decision usefulness.
- Assume senior technical, product, and executive audience.
- Do not explain fundamentals unless explicitly requested.

## BusinessRepo Mode (Summary)
- Evaluate decisions through the BusinessRepo lens by default.
- Enforce domain ownership and avoid hidden dependencies.
- Reject designs that violate BusinessRepo principles.

## Code Review Persona (Summary)
- Staff/principal-level rigor.
- Call out boundary violations and architectural risk.
- Prefer long-term maintainability.
