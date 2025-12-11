# BioFrench Android App - Copilot Instructions

## Overview
The BioFrench app is a pharmaceutical catalog Android application built with modern development practices. It features a comprehensive admin management system for maintaining a medicine catalog, using MVVM architecture with Jetpack Compose and Material Design 3.

## Technology Stack
- **Language**: Kotlin
- **UI Framework**: Material Design 3, Jetpack Compose
- **Architecture**: MVVM with Repository pattern
- **Database**: Room with TypeConverters for complex data
- **Authentication**: Simple credential-based (admin/Hayabusa@123)
- **Navigation**: Jetpack Navigation Component
- **Image Loading**: Coil for SVG/PNG assets
- **Async Programming**: Kotlin Coroutines and Flow
- **Dependency Injection**: Manual ViewModel factories (no Hilt)

## Core Features
- **Medicine Catalog**: Grid-based browsing with search and filtering
- **Medicine Cards**: Full-image display with configurable layouts
- **Detailed Views**: Complete medicine information with interactions
- **Admin System**: Full CRUD operations for medicine management
- **Responsive UI**: Material Design 3 with dark/light theme support
- **Data Persistence**: Room database with JSON serialization

## Screen Architecture

### MedicineCatalogScreen
- **Layout**: Configurable grid (default 3 columns, aspect ratio 1.55)
- **Search**: Filter by name, brand, or category
- **Cards**: Image fills card, name below
- **Navigation**: Tap for details, button for admin access

### AdminScreen
- **List**: Vertical scrollable medicine list with actions
- **Actions**: Toggle visibility (), edit (), delete ()
- **Forms**: Add/edit dialogs with validation
- **Navigation**: Back to catalog

### MedicineDetailScreen
- **Content**: Brand, generic, category, dosage, effects, interactions
- **Navigation**: Back button in top app bar

## Data Models

### MedicineEntity (Database)
`kotlin
data class MedicineEntity(
    val id: Long = 0,
    val genericName: String,
    val brandName: String,
    val category: String,
    val dosage: String,
    val imageName: String?,
    val isActive: Boolean = true,
    val sideEffects: List<String> = emptyList(),
    val contraindications: List<String> = emptyList(),
    val interactions: List<String> = emptyList()
)
`

### Medicine (UI Model)
`kotlin
data class Medicine(
    val id: String,
    val genericName: String,
    val brandName: String,
    val category: String,
    val dosage: String,
    val imageName: String? = null
)
`

## Development Guidelines
- **Architecture**: Strict MVVM with Repository abstraction
- **Data Flow**: Reactive updates using Kotlin Flow
- **Error Handling**: User-friendly feedback mechanisms
- **Code Organization**: Clear package structure and separation of concerns
- **Database**: Room with proper TypeConverters for list serialization
- **Navigation**: Single Activity with Compose Navigation
- **UI Design**: Material Design 3 components and consistent theming
- **Layout Control**: Parameterized grid configurations
- **Image Handling**: Coil with SVG support and fallbacks
- **API Usage**: Never use experimental APIs to prevent release build failures

## Project Structure
`
com.biofrench.catalog/
 data/
    database/       # Room entities, DAOs, converters
    model/          # Data models and mappings
    repository/     # MedicineRepository implementation
 ui/
    admin/          # AdminScreen, AdminViewModel
    catalog/        # Catalog screens, cards, ViewModel
    details/        # DetailScreen, ViewModel
    theme/          # Theming and colors
 MainActivity.kt     # Navigation host setup
`

## Database Design
- **Schema**: Medicine table with full CRUD operations
- **TypeConverters**: JSON serialization for list fields
- **Active Status**: Boolean flag for catalog visibility
- **Constraints**: Required fields validation

## Admin Features
### Medicine Management
- **Create**: Comprehensive form with all fields
- **Read**: Paginated list view
- **Update**: Inline editing with validation
- **Delete**: Confirmation dialogs

### Validation Rules
- **Required**: Brand name, generic name, category, dosage
- **Optional**: Image name
- **Real-time**: Form validation with submit button state

## Navigation Flow
`
Catalog Screen  Admin Screen
       
Detail Screen
`

## Recent Updates
- **Swipe Navigation**: Restored full-screen image swipe functionality using HorizontalPager
- **Card Layout**: Updated aspect ratio to 1.55f to match rectangular image dimensions (1224x792)
- **Grid Spacing**: Standardized spacing to 8dp uniformly for even card placement
- **Foundation Library**: Updated to version 1.6.0 for pager support

## Current Issues and Requirements

### Experimental API Usage (CRITICAL)
**Problem**: Current implementation uses HorizontalPager from ndroidx.compose.foundation:foundation:1.6.0, which is an experimental API. This violates the development guideline of never using experimental APIs.

**Impact**: Causes build warnings in development and potential failures in release builds.

**Requirement**: Replace HorizontalPager with stable API implementation for swipe navigation. Use pointerInput with detectHorizontalDragGestures and manual state management for swipe gestures.

### Card Layout Optimization
**Status**:  RESOLVED
- Card aspect ratio updated to 1.55f (matches 1224x792 image dimensions)
- Grid spacing standardized to 8dp uniform
- Cards now display as rectangles instead of squares

## Security & Validation
- **Authentication**: Hardcoded credentials (production unsuitable)
- **Input Sanitization**: Form validation and data integrity
- **Database Constraints**: Schema-level validation

## Code Quality Standards
- **Architecture**: Clean separation of concerns
- **Reactivity**: Flow-based data streams
- **Modularity**: Reusable composables
- **Type Safety**: Kotlin's compile-time guarantees
- **Naming**: Descriptive, consistent identifiers
