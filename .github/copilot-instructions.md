# BioFrench Android App - Copilot Instructions

## Project Overview
BioFrench pharmaceutical catalog Android application built with modern Android development practices, featuring a complete admin management system for medicine catalog maintenance.

## Technology Stack
- **Language**: Kotlin
- **UI Framework**: Material Design 3, Jetpack Compose
- **Architecture**: MVVM with Repository pattern
- **Database**: Room for local data persistence
- **Authentication**: Simple credential-based admin system (admin/Hayabusa@123)
- **Navigation**: Navigation Component with catalog, admin, and detail screens
- **Image Loading**: Coil for SVG/PNG image handling from assets
- **Async**: Kotlin Coroutines and Flow for reactive data streams
- **Dependency Injection**: Manual ViewModel factory (no Hilt)

## Key Features
- **Medicine Catalog**: Grid-based browse with search functionality
- **Medicine Cards**: Icon display with name below, configurable grid layout
- **Detailed Medicine Information**: Complete medicine details with side effects, contraindications, and interactions
- **Admin Management System**:
  - Add new medicines with comprehensive forms
  - Edit existing medicine information
  - Toggle active/inactive status (eye icon)
  - Delete medicines with confirmation
  - Back navigation to catalog
- **Modern Material Design 3 UI**: Responsive layouts with rounded corners
- **Dark/Light Theme Support**: Automatic system theme detection
- **Database Persistence**: Room database with TypeConverters for complex data lists

## Screen Structure

### Catalog Screen (MedicineCatalogScreen)
- **Grid Layout**: Configurable columns (default 3) and card aspect ratio (default 0.9)
- **Search Bar**: Filter by generic name, brand name, or category
- **Medicine Cards**: Icon fills card (100%), name displayed below card
- **Admin Access**: Button to navigate to admin screen
- **Navigation**: Click cards to view medicine details

### Admin Screen (AdminScreen)
- **Medicine List**: Vertical list with action buttons per item
- **Actions per Medicine**:
  - 👁️ Toggle visibility (active/inactive status)
  - ✏️ Edit medicine details
  - 🗑️ Delete medicine
- **Add Medicine**: Button to create new medicines
- **Edit Dialog**: Form with fields for brand name, generic name, category, dosage, image name
- **Back Button**: Navigation back to catalog screen

### Detail Screen (MedicineDetailScreen)
- **Medicine Information**: Brand name, generic name, category, dosage
- **Additional Details**: Side effects, contraindications, drug interactions
- **Back Navigation**: Top app bar with back button

## Data Model

### MedicineEntity (Database)
```kotlin
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
```

### Medicine (UI Model)
```kotlin
data class Medicine(
    val id: String,
    val genericName: String,
    val brandName: String,
    val category: String,
    val dosage: String,
    val imageName: String? = null
)
```

## Development Guidelines
- **Architecture**: Follow MVVM pattern with Repository layer
- **Data Flow**: Use Kotlin Flow for reactive UI updates
- **Error Handling**: Basic error handling with user feedback
- **Code Organization**: Proper separation of concerns with clear package structure
- **Database**: Use Room with TypeConverters for JSON serialization of lists
- **Navigation**: Single Activity with Jetpack Navigation Component
- **UI**: Material Design 3 components with consistent theming
- **Layout Control**: Configurable grid columns and card aspect ratios
- **Image Handling**: SVG support via Coil with fallback to text placeholder

## Code Structure
```
com.biofrench.catalog/
├── data/
│   ├── database/       # Room database, DAOs, entities
│   ├── model/          # Data models and converters
│   └── repository/     # MedicineRepository implementation
├── ui/
│   ├── admin/          # AdminScreen and AdminViewModel
│   ├── catalog/        # Catalog screens, cards, and ViewModel
│   ├── details/        # DetailScreen and ViewModel
│   └── theme/          # App theming and colors
└── MainActivity.kt     # Navigation setup
```

## Database Schema
- **Medicine Table**: Complete medicine information with Room annotations
- **TypeConverters**: JSON serialization for lists (side effects, contraindications, interactions)
- **CRUD Operations**: Full database operations through DAO layer
- **Active Status**: Boolean field for showing/hiding medicines in catalog

## Admin Functionality
### Medicine Management
- **Create**: Add new medicines with all required fields
- **Read**: View all medicines in admin list
- **Update**: Edit medicine details and toggle active status
- **Delete**: Remove medicines from database

### Form Validation
- **Required Fields**: Brand name, generic name, category, dosage
- **Optional Fields**: Image name
- **Real-time Validation**: Button enabled only when required fields filled

## Navigation Flow
```
Catalog Screen ←→ Admin Screen
    ↓
Detail Screen
```

## Recent Updates
- **Configurable Layout**: Grid columns and card aspect ratios adjustable via parameters
- **Icon Display**: Medicine icons fill entire cards (100%) with names below
- **Back Navigation**: Admin screen includes back button to catalog
- **Improved UI**: Clean card design with action buttons in admin list

## Security Considerations
- **Simple Authentication**: Hardcoded admin credentials (not for production)
- **Input Validation**: Basic validation for medicine data entry
- **Data Integrity**: Database constraints and required field validation

## Maintainability Features
- **Clean Architecture**: Clear separation of UI, business logic, and data
- **Reactive Programming**: Flow-based data streams for real-time updates
- **Composable UI**: Modular, reusable components
- **Type Safety**: Kotlin's type system for compile-time safety
- **Consistent Naming**: Clear, descriptive function and variable names