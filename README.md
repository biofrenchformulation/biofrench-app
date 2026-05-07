# BioFrench App

Android medicine catalog app built with Kotlin, Jetpack Compose, MVVM, and Room.

## Quick Start

```bash
./gradlew assembleDebug
./gradlew test
```

## Tech Stack

- Kotlin + Jetpack Compose (Material 3)
- MVVM + Repository pattern
- Room database
- Navigation Compose
- Coil (SVG/PNG/JPG loading)
- Product flavors:
  - `biofrench`: BioFrench-branded app variant
  - `asvins`: partner-branded variant built from the same codebase

## Project Layout

```text
app/src/main/java/com/biofrench/catalog/
├── data/        # Room entities, DAO, repository, loaders
├── ui/          # catalog, admin, details, theme
└── MainActivity.kt
```

## Common Development Tasks

- Add screen: create composable under `ui/` and register route in `MainActivity.kt`.
- Update medicine model: change entity/model/mapper together and bump DB version if schema changes.
- Update catalog layout: adjust grid/card parameters in `ui/catalog/`.
- Add images: place files in `app/src/main/assets/images/` using `{stringId}-1.{ext}` naming.

## Release Workflow (GitHub Actions)

Use **Actions → Create Release → Run workflow** with:

- `version` (example: `v1.0.0`)
- `release_notes`

Workflow behavior:

1. Builds release APKs (`biofrench` and `asvins`)
2. Verifies release assets
3. Creates and pushes git tag
4. Publishes GitHub Release with:
   - `biofrench-android-app.apk`
   - `asvins-android-app.apk`
   - `medicines.json`

Version format: semantic versioning with `v` prefix (`vMAJOR.MINOR.PATCH`).

## Troubleshooting

- Build/release failure: run `./gradlew assembleBiofrenchRelease assembleAsvinsRelease` locally first.
- Gradle release task naming follows `assemble<Flavor><BuildType>` (e.g., `assembleBiofrenchRelease`).
- Existing tag error: remove existing local/remote tag, then re-run workflow.

## Related Files

- Workflow details: `.github/workflows/README.md`
- Workflow definition: `.github/workflows/release.yml`
- Legacy release script: `wnt_biofrench_app.bat`
