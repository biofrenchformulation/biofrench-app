package com.biofrench.catalog.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverters
import androidx.room.TypeConverter
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

@Entity(tableName = "medicines")
@TypeConverters(StringListConverter::class)
data class MedicineEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val stringId: String = "",
    val activeIngredient: String,
    val brandName: String,
    val category: String,
    val dosage: String,
    val type: String = "",
    val price: String = "",
    val description: String = "",
    val keyFeatures: List<String> = emptyList(),
    val isActive: Boolean = true,
    val commonSideEffects: List<String> = emptyList(),
    val indicatedIn: List<String> = emptyList(),
    val drugInteractions: List<String> = emptyList(),
    val source: String = "Biofrench"
)

class StringListConverter {
    @TypeConverter
    fun fromList(list: List<String>?): String = Gson().toJson(list ?: emptyList<String>())
    @TypeConverter
    fun toList(json: String): List<String> = Gson().fromJson(json, object : TypeToken<List<String>>() {}.type)
}
