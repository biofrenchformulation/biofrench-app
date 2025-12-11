package com.biofrench.catalog

/**
 * Application-wide configuration constants.
 * Edit these values to customize the app behavior.
 */
object AppConfig {
    
    /**
     * UI Configuration
     */
    object UI {
        /** Number of columns in the medicine grid (increase for more columns, decrease for fewer) */
        const val CATALOG_GRID_COLUMNS = 3
        
        /** Aspect ratio for medicine cards (1.0 = square, < 1.0 = portrait, > 1.0 = landscape) 
         *  1.55 matches the image dimensions (1224x792) for rectangular cards */
        const val MEDICINE_CARD_ASPECT_RATIO = 1.55f
        
        /** Fixed height for medicine cards in dp */
        const val MEDICINE_CARD_HEIGHT_DP = 50
    }
    
    /**
     * Database Configuration
     */
    object Database {
        /** Database name */
        const val NAME = "biofrench-db"
        
        /** Database version - increment this when schema changes */
        const val VERSION = 2
    }
    
    /**
     * Image Configuration
     */
    object Images {
        /** Directory in assets where medicine images are stored */
        const val ASSETS_DIR = "images"
        
        /** Supported image file extensions */
        val SUPPORTED_EXTENSIONS = listOf("svg", "png", "jpg", "jpeg")
        
        /** Image file naming pattern: {medicineId}-1.{extension} */
        const val IMAGE_SUFFIX = "-1"
    }
    
    /**
     * Source Configuration
     */
    object Sources {
        /** Default source for new medicines */
        const val DEFAULT_SOURCE = "Biofrench"
        
        /** Source name for in-house medicines */
        const val BIOFRENCH_SOURCE = "Biofrench"
    }
}
