package com.biofrench.catalog

import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.ui.catalog.Medicine
import com.biofrench.catalog.ui.catalog.toMedicine
import org.junit.Assert.assertEquals
import org.junit.Test

class MedicineMapperTest {

    @Test
    fun `toMedicine converts MedicineEntity to Medicine correctly`() {
        // Given
        val entity = MedicineEntity(
            id = 1,
            stringId = "med001",
            brandName = "Test Medicine",
            source = "Biofrench"
        )

        // When
        val medicine = entity.toMedicine()

        // Then
        assertEquals("med001", medicine.id)
        assertEquals("Test Medicine", medicine.brandName)
        assertEquals("Biofrench", medicine.source)
    }

    @Test
    fun `toMedicine handles empty source`() {
        // Given
        val entity = MedicineEntity(
            id = 2,
            stringId = "med002",
            brandName = "Another Medicine",
            source = ""
        )

        // When
        val medicine = entity.toMedicine()

        // Then
        assertEquals("med002", medicine.id)
        assertEquals("Another Medicine", medicine.brandName)
        assertEquals("", medicine.source)
    }

    @Test
    fun `toMedicine handles special characters in brandName`() {
        // Given
        val entity = MedicineEntity(
            id = 3,
            stringId = "med003",
            brandName = "Medicine® Plus™",
            source = "Test Source"
        )

        // When
        val medicine = entity.toMedicine()

        // Then
        assertEquals("med003", medicine.id)
        assertEquals("Medicine® Plus™", medicine.brandName)
        assertEquals("Test Source", medicine.source)
    }

    @Test
    fun `toMedicine preserves all entity fields in Medicine model`() {
        // Given
        val entity = MedicineEntity(
            id = 4,
            stringId = "complex-id-123",
            brandName = "Complex Brand Name",
            source = "Complex Source Name"
        )

        // When
        val medicine = entity.toMedicine()

        // Then
        assertEquals(entity.stringId, medicine.id)
        assertEquals(entity.brandName, medicine.brandName)
        assertEquals(entity.source, medicine.source)
    }
}