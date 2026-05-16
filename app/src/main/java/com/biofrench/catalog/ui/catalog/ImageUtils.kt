package com.biofrench.catalog.ui.catalog

import android.content.Context
import com.biofrench.catalog.data.ImageImportHandler

/**
 * Finds the first available image source for the given medicine ID.
 * Returns either:
 * - "files:{absolute-path}" for imported images
 * - "asset:images/{file-name}" for bundled assets
 * - null when no image exists for the medicine ID
 */
fun findMedicineImageAsset(context: Context, medicineId: String): String? {
    if (medicineId.isBlank()) return null
    return ImageImportHandler(context).findMedicineImage(medicineId)
}

/**
 * Converts an internal image source token into a URI string consumable by Coil.
 *
 * Supported source formats:
 * - `asset:images/{fileName}` -> `file:///android_asset/images/{fileName}`
 * - `files:{absolutePath}` -> `file://{absolutePath}`
 */
fun buildImageDataFromSource(imageSource: String): String {
    return when {
        imageSource.startsWith("asset:") -> "file:///android_asset/${imageSource.removePrefix("asset:")}"
        imageSource.startsWith("files:") -> "file://${imageSource.removePrefix("files:")}"
        else -> imageSource
    }
}
