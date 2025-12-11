package com.biofrench.catalog

import app.cash.turbine.test
import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.data.repository.MedicineRepository
import com.biofrench.catalog.ui.catalog.MedicineCatalogViewModel
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.whenever

class MedicineCatalogViewModelTest {

    @Mock
    private lateinit var repository: MedicineRepository

    private lateinit var viewModel: MedicineCatalogViewModel

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
    }

    @Test
    fun `medicines StateFlow emits repository data`() = runTest {
        // Given
        val expectedMedicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1", isActive = true),
            MedicineEntity(id = 2, stringId = "med2", brandName = "Medicine 2", isActive = true)
        )
        whenever(repository.getActiveMedicines()).thenReturn(flowOf(expectedMedicines))

        // When
        viewModel = MedicineCatalogViewModel(repository)

        // Then
        viewModel.medicines.test {
            assertEquals(expectedMedicines, awaitItem())
        }
    }

    @Test
    fun `medicines StateFlow emits empty list when repository returns empty`() = runTest {
        // Given
        whenever(repository.getActiveMedicines()).thenReturn(flowOf(emptyList()))

        // When
        viewModel = MedicineCatalogViewModel(repository)

        // Then
        viewModel.medicines.test {
            assertEquals(emptyList<MedicineEntity>(), awaitItem())
        }
    }

    @Test
    fun `medicines StateFlow starts with empty list before repository data arrives`() = runTest {
        // Given
        val expectedMedicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1", isActive = true)
        )
        whenever(repository.getActiveMedicines()).thenReturn(flowOf(expectedMedicines))

        // When
        viewModel = MedicineCatalogViewModel(repository)

        // Then
        viewModel.medicines.test {
            // Initially empty (Eagerly sharing starts with initial value)
            assertEquals(emptyList<MedicineEntity>(), awaitItem())
            // Then emits repository data
            assertEquals(expectedMedicines, awaitItem())
        }
    }
}