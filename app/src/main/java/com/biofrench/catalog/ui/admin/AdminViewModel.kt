package com.biofrench.catalog.ui.admin

import android.content.Context
import android.net.Uri
import com.biofrench.catalog.data.ImageImportHandler
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.biofrench.catalog.data.MedicineDataLoader
import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.data.repository.MedicineRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class AdminViewModel(private val repository: MedicineRepository) : ViewModel() {
    val medicines: StateFlow<List<MedicineEntity>> =
        repository.getAllMedicines().stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun addMedicine(medicine: MedicineEntity) {
        viewModelScope.launch {
            repository.insertMedicine(medicine)
        }
    }

    fun updateMedicine(medicine: MedicineEntity) {
        viewModelScope.launch {
            repository.updateMedicine(medicine)
        }
    }

    fun deleteMedicine(medicine: MedicineEntity) {
        viewModelScope.launch {
            repository.deleteMedicine(medicine)
        }
    }

    fun importMedicinesFromJson(context: android.content.Context, filePath: String, onComplete: (Int, String?) -> Unit) {
        viewModelScope.launch {
            try {
                val loader = MedicineDataLoader(context)
                val medicines = loader.loadMedicinesFromFile(filePath)
                if (medicines.isNotEmpty()) {
                    repository.deleteAllMedicines()
                    repository.insertMedicines(medicines)
                    onComplete(medicines.size, null)
                } else {
                    onComplete(0, "No medicines found in the file or invalid format")
                }
            } catch (e: Exception) {
                onComplete(0, "Error importing medicines: ${e.message}")
            }
        }
    }

    fun importMedicineImage(
        context: Context,
        imageUri: Uri,
        medicineId: String,
        onComplete: (String?, String?) -> Unit
    ) {
        viewModelScope.launch {
            try {
                val imageImportHandler = ImageImportHandler(context)
                val importedFileName = imageImportHandler.importMedicineImage(imageUri, medicineId)
                if (importedFileName != null) {
                    onComplete(importedFileName, null)
                } else {
                    onComplete(null, "Invalid image format or failed to import image")
                }
            } catch (e: Exception) {
                onComplete(null, "Error importing image: ${e.message}")
            }
        }
    }
}
