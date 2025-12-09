package com.biofrench.catalog.ui.catalog

data class Medicine(
    val id: String,
    val brandName: String,
    val source: String = "Biofrench" // "Biofrench" or "Affiliate"
)
