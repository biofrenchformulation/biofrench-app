package com.biofrench.catalog.ui.details

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.data.repository.MedicineRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MedicineDetailViewModel(private val repository: MedicineRepository) : ViewModel() {
    private val _medicine = MutableStateFlow<MedicineEntity?>(null)
    val medicine: StateFlow<MedicineEntity?> = _medicine

    fun loadMedicine(stringId: String) {
        android.util.Log.d("MedicineDetailViewModel", "loadMedicine called with stringId=$stringId")
        viewModelScope.launch {
            try {
                val result = repository.getMedicineByStringId(stringId)
                android.util.Log.d("MedicineDetailViewModel", "Medicine loaded from repository: $result")
                _medicine.value = result
            } catch (e: Exception) {
                android.util.Log.e("MedicineDetailViewModel", "Error loading medicine for id=$stringId", e)
            }
        }
    }
}
