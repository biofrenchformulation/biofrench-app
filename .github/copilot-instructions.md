# BioFrench Android App - Copilot Instructions

## Overview
The BioFrench app is a pharmaceutical catalog Android application built with modern development practices. It features a comprehensive admin management system for maintaining a medicine catalog, using MVVM architecture with Jetpack Compose and Material Design 3.

One shared codebase builds two product flavors: `biofrench` and `asvins`.

## Technology Stack
- **Language**: Kotlin 1.9.20
- **UI Framework**: Material Design 3, Jetpack Compose
- **Architecture**: MVVM with Repository pattern
- **Database**: Room 2.6.1 with TypeConverters for complex data
- **Authentication**: Simple credential-based (admin screen, not production-grade)
- **Navigation**: Jetpack Navigation Compose 2.7.5
- **Image Loading**: Coil 2.5.0 for SVG/PNG/JPG assets
- **Async Programming**: Kotlin Coroutines and Flow
- **Dependency Injection**: Manual ViewModel factories (no Hilt)
- **Build**: Android Gradle Plugin 8.2.0

## Core Features
- **Medicine Catalog**: Grid-based browsing with search and source-based filtering
- **Medicine Cards**: Full-image display with configurable aspect ratio and layout
- **Full-Screen Viewer**: Swipe + previous/next navigation between medicine images
- **Admin System**: Full CRUD operations for medicine management
- **JSON Import**: Admin can import medicines from a JSON file via file picker
- **Flavor-Aware UI**: Separate branding and source tabs for `biofrench` and `asvins` builds
- **Responsive UI**: Material Design 3 with dark/light theme support
- **Data Persistence**: Room database with JSON serialization

## Screen Architecture

### WelcomeScreen
- Shown on app launch before navigating to the catalog
- Navigates to catalog on "Continue"

### MedicineCatalogScreen
- **Layout**: Configurable grid (default 3 columns, aspect ratio 1.55f)
- **Search**: Filter by brand name (case-insensitive)
- **Source tabs**: `Biofrench` / `Affiliate` / `Other` (BioFrench build); `Asvins` (Asvins build)
- **Other tab**: Hidden by default, toggled via Star icon in the header
- **Cards**: Image fills card using `MedicineCard` composable; broken-image fallback icon shown when no asset found
- **Navigation**: Tap card opens `FullScreenImageDialog`; Settings icon goes to admin; Favorite icon goes to ThankYouScreen

### FullScreenImageDialog
- Full-screen `Dialog` with black background
- **Swipe navigation**: `pointerInput` + `detectHorizontalDragGestures`; swipe threshold is 100px; manual `currentPage` state (no `HorizontalPager`)
- **Button navigation**: Previous/Next `IconButton`s at the bottom when more than one medicine
- **Page indicator**: `"N / total"` text between nav buttons
- **Close**: X `IconButton` at top-right; also dismisses on back press or tap outside
- **Image loading**: `findMedicineImageAsset()` from `ImageUtils.kt`; SVG decoder added conditionally via Coil

### AdminScreen
- **List**: `LazyColumn` of all medicines (including inactive), searchable by brand name or `stringId`
- **Actions per item**: Toggle visibility (eye icon), set preferred-affiliate (star icon), edit (pencil icon), delete (trash icon)
- **Add/Edit dialog**: Form with `brandName`, `stringId`, `source`, `isActive`, `preferredAffiliate` fields
- **JSON import**: File picker (`GetContent`) → `MedicineDataLoader.loadMedicinesFromFile()` → bulk insert

### ThankYouScreen
- Informational screen reachable from catalog header or footer

## Data Models

### MedicineEntity (Database)
```kotlin
@Entity(tableName = "medicines")
data class MedicineEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val stringId: String = "",        // used for image file naming, e.g. "med001"
    val brandName: String,
    val isActive: Boolean = true,     // catalog visibility flag
    val source: String = "Biofrench", // determines source tab
    val preferredAffiliate: Boolean = false // true = Affiliate tab, false = Other tab
)
```

### Medicine (UI Model)
```kotlin
data class Medicine(
    val id: String,       // maps from MedicineEntity.stringId
    val brandName: String
)
```

## Source Filtering Logic
```kotlin
private fun isAffiliateMedicine(med: MedicineEntity): Boolean =
    med.preferredAffiliate && !med.source.equals("Biofrench", ignoreCase = true)
```
- **Biofrench tab**: `source == "Biofrench"`
- **Affiliate tab**: `preferredAffiliate == true && source != "Biofrench"`
- **Other tab**: `source != "Biofrench" && preferredAffiliate == false`
- **Asvins primary tab**: same as Affiliate tab logic (shows preferred-affiliate non-Biofrench medicines)

## Image Asset Convention
- All medicine images live in `app/src/main/assets/images/`
- Naming pattern: `{stringId}-1.{ext}` (e.g., `med001-1.svg`)
- Supported extensions (checked in order): `svg`, `png`, `jpg`, `jpeg`
- `findMedicineImageAsset(context, medicineId)` in `ImageUtils.kt` returns the first matching asset name or `null`

## Centralized Configuration (`AppConfig.kt`)
```kotlin
object AppConfig {
    object UI {
        const val CATALOG_GRID_COLUMNS = 3
        const val MEDICINE_CARD_ASPECT_RATIO = 1.55f  // matches 1224x792 images
        const val MEDICINE_CARD_HEIGHT_DP = 50
    }
    object Database {
        const val NAME = "biofrench-db"
        const val VERSION = 2  // increment on schema changes
    }
    object Images {
        const val ASSETS_DIR = "images"
        val SUPPORTED_EXTENSIONS = listOf("svg", "png", "jpg", "jpeg")
        const val IMAGE_SUFFIX = "-1"
    }
}
```

## Navigation Flow
```
WelcomeScreen → CatalogScreen ⇄ AdminScreen
                     ↓
               ThankYouScreen
```
Routes: `"welcome"` (start) → `"catalog"` → `"admin"` / `"thankyou"`

## Project Structure
```
com.biofrench.catalog/
├── AppConfig.kt             # Centralized UI/DB/image constants
├── BioFrenchApplication.kt  # Application class
├── MainActivity.kt          # Single-activity navigation host
├── data/
│   ├── MedicineDataLoader.kt  # JSON file → List<MedicineEntity>
│   ├── database/              # Room AppDatabase, MedicineDao
│   ├── model/                 # MedicineEntity, MedicineJson
│   └── repository/            # MedicineRepository (DAO wrapper)
└── ui/
    ├── admin/                 # AdminScreen, AdminViewModel
    ├── catalog/               # MedicineCatalogScreen, MedicineCard,
    │                          #   FullScreenImageDialog, ImageUtils, MedicineCatalogViewModel
    ├── screens/               # WelcomeScreen, ThankYouScreen
    └── theme/                 # BioFrenchTheme, Color, Type
```

## Database Design
- **Schema**: `medicines` table with CRUD operations
- **Active Status**: `isActive` boolean flag controls catalog visibility
- **Source + Affiliate**: `source` + `preferredAffiliate` drive tab filtering
- **Auto-increment PK**: `id: Long`; string identity for images: `stringId`
- **Version**: currently `2`; bump and add migration on schema changes

## Admin Features

### Medicine Management
- **Create**: Dialog form with all fields; `stringId` used to link images
- **Read**: Scrollable list; searchable by brand name or `stringId`
- **Update**: Inline edit dialog with pre-filled values
- **Delete**: Confirmation dialog before removal
- **Toggle visibility**: `isActive` flag toggled per item
- **Toggle preferred-affiliate**: `preferredAffiliate` flag toggled per item (star icon)
- **JSON import**: Pick `.json` file → parse via `MedicineDataLoader` → bulk `insertMedicines()`

### Validation Rules
- **Required**: `brandName`, `stringId`
- **Optional**: `source`, `isActive`, `preferredAffiliate`
- **Real-time**: Submit button disabled until required fields are filled

## Development Guidelines
- **Architecture**: Strict MVVM with Repository abstraction (`UI → ViewModel → Repository → DAO`)
- **Data Flow**: Reactive updates via Kotlin `Flow` / `StateFlow`; collect with `collectAsState()` in composables
- **Error Handling**: User-friendly feedback (Toast messages in Admin)
- **Code Organization**: Clear package structure; reuse existing utilities before adding abstractions
- **Database**: Room with TypeConverters; bump `AppConfig.Database.VERSION` and add migration on schema changes
- **Navigation**: Single Activity with Compose Navigation
- **UI Design**: Material Design 3 components and consistent theming
- **Image Handling**: Always use `findMedicineImageAsset()` from `ImageUtils.kt`; never duplicate asset-lookup logic
- **API Usage**: Never use experimental APIs (no `@OptIn(ExperimentalFoundationApi::class)`)
- **Configuration**: Use `AppConfig` constants for grid columns, aspect ratios, image paths

## Product Flavor Differences
| Feature | `biofrench` | `asvins` |
|---|---|---|
| Logo / title | BioFrench logo + "BioFrench Catalog" | Asvins logo + "Catalog" |
| Primary tab | Biofrench | Asvins (shows affiliate medicines) |
| Affiliate tab | Shown | Hidden |
| `is_asvins_brand` bool resource | `false` | `true` |

## Release Workflow (GitHub Actions)
- Manual workflow: **Create Release** (`Actions → Create Release → Run workflow`)
- Inputs: `version` (e.g., `v1.0.0`), `release_notes`
- Builds release APKs for both flavors: `biofrench-android-app.apk`, `asvins-android-app.apk`
- Creates git tag, publishes GitHub Release with both APKs + `medicines.json`
- Troubleshoot: run `./gradlew assembleBiofrenchRelease assembleAsvinsRelease` locally first

## Security & Validation
- **Authentication**: Hardcoded credentials (admin screen is not production-grade)
- **Input Sanitization**: Form validation and data integrity in Admin dialogs
- **Database Constraints**: Schema-level validation via Room annotations
- **No new secrets**: Do not add hardcoded credentials or API keys to the codebase
