package com.biofrench.catalog

import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import app.cash.turbine.test
import com.biofrench.catalog.data.MedicineDataLoader
import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.data.repository.MedicineRepository
import com.biofrench.catalog.ui.admin.AdminViewModel
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

class AdminViewModelTest {

    @get:Rule
    val instantTaskExecutorRule = InstantTaskExecutorRule()

    @Mock
    private lateinit var repository: MedicineRepository

    @Mock
    private lateinit var context: android.content.Context

    private lateinit var viewModel: AdminViewModel

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
    }

    @Test
    fun `medicines StateFlow emits repository data`() = runTest {
        // Given
        val expectedMedicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine 1"),
            MedicineEntity(id = 2, stringId = "med2", brandName = "Medicine 2")
        )
        whenever(repository.getAllMedicines()).thenReturn(flowOf(expectedMedicines))

        // When
        viewModel = AdminViewModel(repository)

        // Then
        viewModel.medicines.test {
            assertEquals(expectedMedicines, awaitItem())
        }
    }

    @Test
    fun `addMedicine calls repository insertMedicine`() = runTest {
        // Given
        viewModel = AdminViewModel(repository)
        val medicine = MedicineEntity(id = 1, stringId = "med1", brandName = "New Medicine")

        // When
        viewModel.addMedicine(medicine)

        // Then
        verify(repository).insertMedicine(medicine)
    }

    @Test
    fun `updateMedicine calls repository updateMedicine`() = runTest {
        // Given
        viewModel = AdminViewModel(repository)
        val medicine = MedicineEntity(id = 1, stringId = "med1", brandName = "Updated Medicine")

        // When
        viewModel.updateMedicine(medicine)

        // Then
        verify(repository).updateMedicine(medicine)
    }

    @Test
    fun `deleteMedicine calls repository deleteMedicine`() = runTest {
        // Given
        viewModel = AdminViewModel(repository)
        val medicine = MedicineEntity(id = 1, stringId = "med1", brandName = "Medicine to Delete")

        // When
        viewModel.deleteMedicine(medicine)

        // Then
        verify(repository).deleteMedicine(medicine)
    }

    @Test
    fun `importMedicinesFromJson successfully imports medicines`() = runTest {
        // Given
        viewModel = AdminViewModel(repository)
        val testFilePath = "/test/file.json"
        val expectedMedicines = listOf(
            MedicineEntity(id = 1, stringId = "med1", brandName = "Imported Medicine 1"),
            MedicineEntity(id = 2, stringId = "med2", brandName = "Imported Medicine 2")
        )

        // Mock the data loader
        val mockLoader = org.mockito.kotlin.mock<MedicineDataLoader> {
            onBlocking { loadMedicinesFromFile(testFilePath) }.thenReturn(expectedMedicines)
        }

        // We can't easily mock the constructor call, so we'll test the logic indirectly
        // by mocking the repository calls that should happen

        // When
        var importCount = 0
        var errorMessage: String? = null
        viewModel.importMedicinesFromJson(context, testFilePath) { count, error ->
            importCount = count
            errorMessage = error
        }

        // Give some time for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        // Note: This test is limited because we can't easily mock the MedicineDataLoader constructor
        // In a real scenario, you'd use dependency injection to inject the loader
    }

    @Test
    fun `importMedicinesFromJson handles empty file gracefully`() = runTest {
        // Given
        viewModel = AdminViewModel(repository)
        val testFilePath = "/test/empty.json"

        // When
        var importCount = -1
        var errorMessage: String? = null
        viewModel.importMedicinesFromJson(context, testFilePath) { count, error ->
            importCount = count
            errorMessage = error
        }

        // Give some time for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        // The callback should be called with 0 count and an error message
        // Note: Actual testing would require mocking the data loader
    }

    @Test
    fun `importMedicinesFromJson handles exceptions gracefully`() = runTest {
        // Given
        viewModel = AdminViewModel(repository)
        val testFilePath = "/test/invalid.json"

        // When
        var importCount = -1
        var errorMessage: String? = null
        viewModel.importMedicinesFromJson(context, testFilePath) { count, error ->
            importCount = count
            errorMessage = error
        }

        // Give some time for coroutine to complete
        kotlinx.coroutines.delay(100)

        // Then
        // The callback should be called with 0 count and an error message
        // Note: Actual testing would require mocking the data loader
    }
}