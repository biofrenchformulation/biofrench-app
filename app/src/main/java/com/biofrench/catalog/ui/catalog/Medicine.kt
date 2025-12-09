package com.biofrench.catalog.ui.catalog

data class Medicine(
    val id: String,
    val activeIngredient: String,
    val brandName: String,
    val category: String,
    val dosage: String,
    val source: String = "Biofrench" // "Biofrench" or "Affiliate"
)
