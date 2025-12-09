package com.biofrench.catalog.data

import android.content.Context
import com.biofrench.catalog.data.model.MedicineEntity
import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileInputStream

class MedicineDataLoader(private val context: Context) {

    // Only use loadMedicinesFromFile for admin import, not for runtime asset loading
    // Remove or comment out loadMedicinesFromAssets if not needed
    suspend fun loadMedicinesFromFile(filePath: String): List<MedicineEntity> = withContext(Dispatchers.IO) {
        try {
            val file = File(filePath)
            val jsonString = FileInputStream(file).bufferedReader().use { it.readText() }
            val gson = Gson()
            val medicines: List<MedicineJson> = gson.fromJson(jsonString, Array<MedicineJson>::class.java).toList()
            medicines.map { it.toEntity() }
        } catch (e: Exception) {
            // Return empty list if loading fails
            emptyList()
        }
    }

    private fun MedicineJson.toEntity(): MedicineEntity {

        return MedicineEntity(
            stringId = id,
            activeIngredient = activeIngredient,
            brandName = brandName,
            category = category,
            dosage = dosage,
            type = type,
            price = price,
            description = description,
            keyFeatures = keyFeatures,
            isActive = isActive,
            commonSideEffects = commonSideEffects,
            indicatedIn = indicatedIn,
            drugInteractions = drugInteractions,
            source = source,
            preferredAffiliate = preferredAffiliate || source.equals("Biofrench", ignoreCase = true)
        )
    }
}

data class MedicineJson(
    @SerializedName("id") val id: String,
    @SerializedName("activeIngredient") val activeIngredient: String,
    @SerializedName("brandName") val brandName: String,
    @SerializedName("category") val category: String,
    @SerializedName("dosage") val dosage: String,
    @SerializedName("type") val type: String,
    @SerializedName("price") val price: String,
    @SerializedName("description") val description: String,
    @SerializedName("keyFeatures") val keyFeatures: List<String>,
    @SerializedName("isActive") val isActive: Boolean = true,
    @SerializedName("commonSideEffects") val commonSideEffects: List<String>,
    @SerializedName("indicatedIn") val indicatedIn: List<String>,
    @SerializedName("drugInteractions") val drugInteractions: List<String>,
    @SerializedName("source") val source: String = "Biofrench",
    @SerializedName("preferredAffiliate") val preferredAffiliate: Boolean = false
)