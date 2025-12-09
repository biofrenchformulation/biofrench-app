package com.biofrench.catalog.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "medicines")
data class MedicineEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val stringId: String = "",
    val brandName: String,
    val isActive: Boolean = true,
    val source: String = "Biofrench",
    val preferredAffiliate: Boolean = false
)
