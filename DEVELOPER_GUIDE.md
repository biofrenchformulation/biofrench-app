# BioFrench Catalog - Developer Guide

## Project Overview
BioFrench pharmaceutical catalog Android application built with modern Android development practices, featuring a complete admin management system for medicine catalog maintenance.

## Quick Start for Editing

### Building the Project
```bash
./gradlew assembleDebug
```

### Running Tests
```bash
./gradlew test
```

## Project Structure

```
app/src/main/java/com/biofrench/catalog/
├── MainActivity.kt                 # Single activity with navigation setup
├── BioFrenchApplication.kt        # Application class for initialization
├── data/
│   ├── model/
│   │   └── MedicineEntity.kt      # Database entity for medicines
│   ├── database/
│   │   ├── AppDatabase.kt         # Room database configuration
│   │   └── MedicineDao.kt         # Database access object
│   ├── repository/
│   │   └── MedicineRepository.kt  # Repository pattern implementation
│   └── MedicineDataLoader.kt      # JSON import functionality
└── ui/
    ├── admin/
    │   ├── AdminScreen.kt         # Medicine management UI
    │   ├── AdminViewModel.kt      # Admin business logic
    │   └── FileUtils.kt           # File picker utilities
    ├── catalog/
    │   ├── MedicineCatalogScreen.kt    # Main catalog display
    │   ├── MedicineCatalogViewModel.kt # Catalog business logic
    │   ├── MedicineCard.kt             # Individual medicine card
    │   ├── Medicine.kt                 # UI model
    │   ├── MedicineMapper.kt           # Entity to UI model conversion
    │   ├── ImageUtils.kt               # Image loading utilities
    │   ├── FullScreenImageDialog.kt    # Image viewer
    │   └── ThankYouScreen.kt           # Thank you page
    ├── welcome/
    │   └── WelcomeScreen.kt       # Initial welcome screen
    └── theme/
        ├── Theme.kt               # Material 3 theme configuration
        ├── Color.kt               # Color palette
        └── Type.kt                # Typography settings
```

## Key Concepts

### Medicine Data Flow
1. **Database (MedicineEntity)** - Persistent storage using Room
2. **Repository** - Abstraction layer for data access
3. **ViewModel** - Manages UI state and business logic
4. **UI Model (Medicine)** - Simplified model for display

### Image Loading
Images are stored in `assets/images/` with naming convention: `{stringId}-1.{ext}`
- Supported formats: svg, png, jpg, jpeg
- Example: `med001-1.svg`

### Tabs and Filtering
- **Biofrench Tab** - Shows medicines where source = "Biofrench"
- **Affiliate Tab** - Shows medicines with preferredAffiliate = true
- **Other Tab** - Shows non-Biofrench medicines with preferredAffiliate = false

## Common Editing Tasks

### Adding a New Screen
1. Create a new composable function in `ui/` directory
2. Add navigation route in `MainActivity.kt` > `BioFrenchNavHost`
3. Add navigation calls from other screens

### Modifying Medicine Data Model
1. Update `MedicineEntity.kt` for database changes
2. Update `Medicine.kt` for UI changes
3. Update `MedicineMapper.kt` for conversion logic
4. Increment database version in `AppDatabase.kt`

### Changing Colors
1. Edit color definitions in `ui/theme/Color.kt`
2. Apply colors in `ui/theme/Theme.kt` color schemes

### Adjusting Layout
- **Grid columns**: Change `columns` parameter in `MedicineCatalogScreen`
- **Card aspect ratio**: Change `cardAspectRatio` parameter
- **Card height**: Modify `fixedHeight` in MedicineCard

## Important Notes

### Database Migrations
When changing `MedicineEntity`:
1. Increment version in `@Database` annotation
2. Add migration strategy or use `fallbackToDestructiveMigration()`

### Image Assets
- Place images in `app/src/main/assets/images/`
- Use stringId from database for file naming
- SVG files require Coil SVG decoder (already included)

### State Management
- Use `remember { mutableStateOf() }` for UI state
- Use `StateFlow` in ViewModels for data streams
- Use `collectAsState()` to observe Flow in Composables

## Dependencies

### Core
- Kotlin 1.9.20
- Compose BOM 2023.10.01
- Material 3

### Database
- Room 2.6.1

### Image Loading
- Coil 2.5.0 (with SVG support)

### Navigation
- Navigation Compose 2.7.5

## Build Configuration

### Minimum Requirements
- Min SDK: 24 (Android 7.0)
- Target SDK: 34 (Android 14)
- Compile SDK: 34

### Signing
Release builds use keystore at `app/keystore/release_new.keystore`

## Tips for Success

1. **Use ViewModels** - Keep business logic out of Composables
2. **Remember Dependencies** - Use `remember { }` for expensive objects
3. **Flow for Data** - Use StateFlow/Flow for reactive data
4. **Clean Architecture** - Maintain separation: UI → ViewModel → Repository → DAO
5. **Test Changes** - Build and run after modifications

## Getting Help

- Check existing code patterns before implementing new features
- Use the same naming conventions as existing code
- Follow Material 3 design guidelines for UI components
- Test on multiple screen sizes and orientations
