# BioFrench Android App - Copilot Instructions

## Overview
BioFrench is a Kotlin Android medicine-catalog app using MVVM, Room, and Jetpack Compose.  
One shared codebase builds two product flavors: `biofrench` and `asvins`.

## Current Stack
- Kotlin 1.9.20
- Android Gradle Plugin 8.2.0
- Jetpack Compose + Material 3
- Room 2.6.1
- Navigation Compose 2.7.5
- Coil 2.5.0 (+ SVG)

## Architecture
- **UI**: `ui/` (catalog, admin, details, theme)
- **State**: ViewModels with Flow/StateFlow
- **Data**: Repository + Room DAO/entity
- **Entry point**: single-activity navigation in `MainActivity.kt`

## Product Behavior
- Catalog grid with search and source-based filtering
- Admin CRUD for medicines with active/inactive visibility control
- Full-screen image dialog with swipe + previous/next controls
- Assets from `app/src/main/assets/` (including `medicines.json` and images)

## v2.0-Aligned Recent Changes
- Swipe navigation in `FullScreenImageDialog` uses stable gesture handling:
  - `pointerInput` + `detectHorizontalDragGestures`
  - manual page state updates (no `HorizontalPager`)
- Catalog card layout tuned for rectangular images:
  - default aspect ratio: `1.55f`
  - grid spacing standardized to `8.dp`
- Release docs consolidated into root `README.md` for a single concise source.

## Release Workflow
- Manual GitHub Actions workflow: **Create Release**
- Builds both release APKs:
  - `biofrench-android-app.apk`
  - `asvins-android-app.apk`
- Publishes release assets with `medicines.json`.

## Development Guidance
- Keep MVVM boundaries clear (`UI -> ViewModel -> Repository -> DAO`)
- Prefer stable APIs; avoid introducing experimental APIs
- Reuse existing patterns and utilities before adding new abstractions
- Keep docs concise; update `README.md` when behavior/workflow changes

## Security Notes
- Admin authentication is credential-based and not production-grade
- Do not add new hardcoded secrets or credentials
