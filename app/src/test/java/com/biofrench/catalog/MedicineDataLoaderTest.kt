package com.biofrench.catalog

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.biofrench.catalog.data.MedicineDataLoader
import com.biofrench.catalog.data.model.MedicineEntity
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class MedicineDataLoaderTest {

    private lateinit var dataLoader: MedicineDataLoader
    private lateinit var context: android.content.Context

    @Before
    fun setup() {
        context = InstrumentationRegistry.getInstrumentation().targetContext
        dataLoader = MedicineDataLoader(context)
    }

    @Test
    fun `loadMedicinesFromFile returns empty list for non-existent file`() = runTest {
        // Given
        val nonExistentFile = "/non/existent/file.json"

        // When
        val result = dataLoader.loadMedicinesFromFile(nonExistentFile)

        // Then
        assertEquals(emptyList<MedicineEntity>(), result)
    }

    @Test
    fun `loadMedicinesFromFile handles invalid JSON gracefully`() = runTest {
        // Given
        val tempFile = File.createTempFile("invalid", ".json")
        tempFile.writeText("invalid json content")
        tempFile.deleteOnExit()

        // When
        val result = dataLoader.loadMedicinesFromFile(tempFile.absolutePath)

        // Then
        assertEquals(emptyList<MedicineEntity>(), result)
    }

    @Test
    fun `MedicineJson toEntity converts correctly for Biofrench source`() {
        // Given
        val json = com.biofrench.catalog.data.MedicineJson(
            id = "med001",
            brandName = "Test Medicine",
            isActive = true,
            source = "Biofrench",
            preferredAffiliate = false
        )

        // When
        val entity = json.toEntity()

        // Then
        assertEquals("med001", entity.stringId)
        assertEquals("Test Medicine", entity.brandName)
        assertEquals(true, entity.isActive)
        assertEquals("Biofrench", entity.source)
        assertEquals(true, entity.preferredAffiliate) // Should be true for Biofrench
    }

    @Test
    fun `MedicineJson toEntity converts correctly for non-Biofrench source`() {
        // Given
        val json = com.biofrench.catalog.data.MedicineJson(
            id = "med002",
            brandName = "Other Medicine",
            isActive = true,
            source = "Other Company",
            preferredAffiliate = true
        )

        // When
        val entity = json.toEntity()

        // Then
        assertEquals("med002", entity.stringId)
        assertEquals("Other Medicine", entity.brandName)
        assertEquals(true, entity.isActive)
        assertEquals("Other Company", entity.source)
        assertEquals(true, entity.preferredAffiliate) // Explicitly set to true
    }

    @Test
    fun `MedicineJson toEntity handles inactive medicines`() {
        // Given
        val json = com.biofrench.catalog.data.MedicineJson(
            id = "med003",
            brandName = "Inactive Medicine",
            isActive = false,
            source = "Biofrench"
        )

        // When
        val entity = json.toEntity()

        // Then
        assertEquals(false, entity.isActive)
        assertEquals(true, entity.preferredAffiliate) // Still true for Biofrench
    }

    @Test
    fun `MedicineJson toEntity handles empty source with default values`() {
        // Given
        val json = com.biofrench.catalog.data.MedicineJson(
            id = "med004",
            brandName = "Default Medicine"
            // isActive and source will use defaults
        )

        // When
        val entity = json.toEntity()

        // Then
        assertEquals("Biofrench", entity.source) // Default value
        assertEquals(true, entity.isActive) // Default value
        assertEquals(true, entity.preferredAffiliate) // True for Biofrench
    }

    @Test
    fun `MedicineJson toEntity handles case insensitive Biofrench matching`() {
        // Given
        val json = com.biofrench.catalog.data.MedicineJson(
            id = "med005",
            brandName = "Case Test Medicine",
            source = "biofrench" // lowercase
        )

        // When
        val entity = json.toEntity()

        // Then
        assertEquals(true, entity.preferredAffiliate) // Should match case-insensitively
    }
}