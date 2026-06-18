package com.biofrench.catalog.data

import android.content.Context
import android.net.Uri
import java.io.File

/**
 * Handles importing and managing medicine images.
 * Images are stored in the app's files directory with the naming format: {medicineId}.{extension}
 */
class ImageImportHandler(private val context: Context) {

    companion object {
        private const val IMAGES_DIR = "images"
        private const val IMAGE_SUFFIX = ""
    }

    /**
     * Imports an image for a medicine and renames it to the correct format.
     * Returns the filename if successful, null otherwise.
     */
    fun importMedicineImage(imageUri: Uri, medicineId: String): String? {
        return try {
            val imageDir = File(context.filesDir, IMAGES_DIR)
            if (!imageDir.exists()) {
                imageDir.mkdirs()
            }

            // Get the original file extension
            val extension = getFileExtension(imageUri)
            if (extension == null || !isValidImageExtension(extension)) {
                return null
            }

            // Create the new filename: medicineId.extension
            val newFileName = "$medicineId$IMAGE_SUFFIX.$extension"
            val newFile = File(imageDir, newFileName)

            // Copy the file content
            context.contentResolver.openInputStream(imageUri)?.use { inputStream ->
                newFile.outputStream().use { outputStream ->
                    inputStream.copyTo(outputStream)
                }
            }

            newFileName
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * Gets the path to the images directory for accessing imported images.
     */
    fun getImagesDirectory(): File {
        return File(context.filesDir, IMAGES_DIR)
    }

    /**
     * Finds an image file for the given medicine ID.
     * Checks the imported images directory first, then falls back to assets.
     */
    fun findMedicineImage(medicineId: String): String? {
        val supportedExts = listOf("svg", "png", "jpg", "jpeg")
        
        // Check imported images directory first
        val imagesDir = getImagesDirectory()
        if (imagesDir.exists()) {
            for (ext in supportedExts) {
                val fileName = "$medicineId$IMAGE_SUFFIX.$ext"
                val file = File(imagesDir, fileName)
                if (file.exists()) {
                    return "files:${file.absolutePath}"
                }
            }
        }
        
        // Fall back to assets
        return supportedExts.firstNotNullOfOrNull { ext ->
            val assetName = "$medicineId$IMAGE_SUFFIX.$ext"
            try {
                context.assets.open("images/$assetName").close()
                "asset:images/$assetName"
            } catch (_: Exception) {
                null
            }
        }
    }

    /**
     * Deletes the imported image for a medicine.
     */
    fun deleteMedicineImage(medicineId: String): Boolean {
        return try {
            val supportedExts = listOf("svg", "png", "jpg", "jpeg")
            val imagesDir = getImagesDirectory()
            
            for (ext in supportedExts) {
                val fileName = "$medicineId$IMAGE_SUFFIX.$ext"
                val file = File(imagesDir, fileName)
                if (file.exists()) {
                    return file.delete()
                }
            }
            false
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }

    private fun getFileExtension(uri: Uri): String? {
        return try {
            val cursor = context.contentResolver.query(uri, null, null, null, null)
            cursor?.use {
                val nameIndex = it.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                if (nameIndex >= 0) {
                    it.moveToFirst()
                    val displayName = it.getString(nameIndex)
                    return displayName.substringAfterLast('.').lowercase()
                }
            }
            null
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    private fun isValidImageExtension(ext: String): Boolean {
        return ext in listOf("svg", "png", "jpg", "jpeg")
    }
}
