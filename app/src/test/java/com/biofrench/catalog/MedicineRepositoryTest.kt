package com.biofrench.catalog

import app.cash.turbine.test
import com.biofrench.catalog.data.database.MedicineDao
import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.data.repository.MedicineRepository
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

class MedicineRepositoryTest {

    @Mock
    private lateinit var medicineDao: MedicineDao

    private lateinit var repository: MedicineRepository

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        repository = MedicineRepository(medicineDao)
    }

    @Test
    fun `getAllMedicines returns flow from dao`() = runTest {
        // Given
        val expectedMedicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1"),
            MedicineEntity(id = 2, stringId = "med2", brandName = "Medicine 2")
        )
        whenever(medicineDao.getAllMedicines()).thenReturn(flowOf(expectedMedicines))

        // When
        val result = repository.getAllMedicines()

        // Then
        result.test {
            assertEquals(expectedMedicines, awaitItem())
        }
    }

    @Test
    fun `getActiveMedicines returns flow from dao`() = runTest {
        // Given
        val expectedMedicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1", isActive = true)
        )
        whenever(medicineDao.getActiveMedicines()).thenReturn(flowOf(expectedMedicines))

        // When
        val result = repository.getActiveMedicines()

        // Then
        result.test {
            assertEquals(expectedMedicines, awaitItem())
        }
    }

    @Test
    fun `insertMedicine delegates to dao`() = runTest {
        // Given
        val medicine = MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1")

        // When
        repository.insertMedicine(medicine)

        // Then
        verify(medicineDao).insertMedicine(medicine)
    }

    @Test
    fun `insertMedicines delegates to dao`() = runTest {
        // Given
        val medicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1"),
            MedicineEntity(id = 2, stringId = "med2", brandName = "Medicine 2")
        )

        // When
        repository.insertMedicines(medicines)

        // Then
        verify(medicineDao).insertMedicines(medicines)
    }

    @Test
    fun `updateMedicine delegates to dao`() = runTest {
        // Given
        val medicine = MedicineEntity(id = 1, stringId = "med1", brandName = "Updated Medicine")

        // When
        repository.updateMedicine(medicine)

        // Then
        verify(medicineDao).updateMedicine(medicine)
    }

    @Test
    fun `deleteMedicine delegates to dao`() = runTest {
        // Given
        val medicine = MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1")

        // When
        repository.deleteMedicine(medicine)

        // Then
        verify(medicineDao).deleteMedicine(medicine)
    }

    @Test
    fun `deleteAllMedicines delegates to dao`() = runTest {
        // When
        repository.deleteAllMedicines()

        // Then
        verify(medicineDao).deleteAllMedicines()
    }

    @Test
    fun `getMedicineByStringId delegates to dao`() = runTest {
        // Given
        val expectedMedicine = MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1")
        whenever(medicineDao.getMedicineByStringId("med1")).thenReturn(expectedMedicine)

        // When
        val result = repository.getMedicineByStringId("med1")

        // Then
        assertEquals(expectedMedicine, result)
        verify(medicineDao).getMedicineByStringId("med1")
    }

    @Test
    fun `getMedicineByStringId returns null when not found`() = runTest {
        // Given
        whenever(medicineDao.getMedicineByStringId("nonexistent")).thenReturn(null)

        // When
        val result = repository.getMedicineByStringId("nonexistent")

        // Then
        assertEquals(null, result)
        verify(medicineDao).getMedicineByStringId("nonexistent")
    }
}