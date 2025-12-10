package com.biofrench.catalog.ui.catalog

/**
 * UI model for displaying medicine information.
 * This is a simplified model used in the presentation layer.
 * 
 * @property id Unique identifier used for image file lookup
 * @property brandName Display name shown to users
 * @property source Origin of the medicine ("Biofrench" or affiliate name)
 */
data class Medicine(
    val id: String,
    val brandName: String,
    val source: String = "Biofrench"
)
