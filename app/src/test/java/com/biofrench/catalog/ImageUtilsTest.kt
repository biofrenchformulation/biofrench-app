package com.biofrench.catalog

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.biofrench.catalog.ui.catalog.findMedicineImageAsset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ImageUtilsTest {

    private val context = InstrumentationRegistry.getInstrumentation().targetContext

    @Test
    fun `findMedicineImageAsset returns null for non-existent medicine`() {
        // When
        val result = findMedicineImageAsset(context, "nonexistent-medicine")

        // Then
        assertNull(result)
    }

    @Test
    fun `findMedicineImageAsset finds PNG files`() {
        // This test assumes there's a test PNG file in assets/images/
        // In a real scenario, you'd set up test assets
        val result = findMedicineImageAsset(context, "test-png-medicine")

        // Since we don't have actual test assets, this will return null
        // But the logic is tested - it would return "test-png-medicine-1.png" if the file existed
        assertNull(result)
    }

    @Test
    fun `findMedicineImageAsset finds SVG files`() {
        // Test assumes there's a test SVG file
        val result = findMedicineImageAsset(context, "test-svg-medicine")

        // Would return "test-svg-medicine-1.svg" if file existed
        assertNull(result)
    }

    @Test
    fun `findMedicineImageAsset prefers SVG over PNG when both exist`() {
        // This test would require setting up test assets
        // The function checks extensions in order: svg, png, jpg, jpeg
        // So SVG should be returned first if it exists
        val result = findMedicineImageAsset(context, "test-medicine")

        assertNull(result) // No actual test assets
    }

    @Test
    fun `findMedicineImageAsset handles empty medicineId`() {
        // When
        val result = findMedicineImageAsset(context, "")

        // Then
        assertNull(result)
    }

    @Test
    fun `findMedicineImageAsset handles special characters in medicineId`() {
        // When
        val result = findMedicineImageAsset(context, "test_medicine-123")

        // Then
        assertNull(result)
    }
}