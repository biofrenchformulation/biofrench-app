package com.biofrench.catalog.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Database entity representing a medicine in the catalog.
 * 
 * @property id Auto-generated unique identifier for database
 * @property stringId User-defined unique ID used for image file naming (e.g., "med001")
 * @property brandName Display name of the medicine
 * @property isActive Whether the medicine is visible in the catalog (true) or hidden (false)
 * @property source Source of the medicine: "Biofrench" for in-house or other affiliates
 * @property preferredAffiliate If true, shown in the "Affiliate" tab; false shows in "Other" tab
 */
@Entity(tableName = "medicines")
data class MedicineEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val stringId: String = "",
    val brandName: String,
    val isActive: Boolean = true,
    val source: String = "Biofrench",
    val preferredAffiliate: Boolean = false
)
