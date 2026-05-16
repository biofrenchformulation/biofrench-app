package com.biofrench.catalog.ui.catalog

import android.content.Context
import com.biofrench.catalog.data.ImageImportHandler

/**
 * Finds the first available image source for the given medicine ID.
 * Returns either:
 * - "files:{absolute-path}" for imported images
 * - "asset:images/{file-name}" for bundled assets
 */
fun findMedicineImageAsset(context: Context, medicineId: String): String? {
    if (medicineId.isBlank()) return null
    return ImageImportHandler(context).findMedicineImage(medicineId)
}

fun buildImageDataFromSource(imageSource: String): String {
    return when {
        imageSource.startsWith("asset:") -> "file:///android_asset/${imageSource.removePrefix("asset:")}"
        imageSource.startsWith("files:") -> "file://${imageSource.removePrefix("files:")}"
        else -> imageSource
    }
}
