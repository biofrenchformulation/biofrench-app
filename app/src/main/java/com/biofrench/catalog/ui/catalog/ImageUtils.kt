package com.biofrench.catalog.ui.catalog

import android.content.Context

/**
 * Finds the first available image asset for the given medicine ID.
 * Checks for supported extensions: svg, png, jpg, jpeg
 */
fun findMedicineImageAsset(context: Context, medicineId: String): String? {
    val supportedExts = listOf("svg", "png", "jpg", "jpeg")
    return supportedExts.firstNotNullOfOrNull { ext ->
        val assetName = "$medicineId-1.$ext"
        try {
            context.assets.open("images/$assetName").close()
            assetName
        } catch (_: Exception) {
            null
        }
    }
}
