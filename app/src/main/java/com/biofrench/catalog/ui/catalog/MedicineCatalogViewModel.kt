package com.biofrench.catalog.ui.catalog

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.biofrench.catalog.data.model.MedicineEntity
import com.biofrench.catalog.data.repository.MedicineRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn

class MedicineCatalogViewModel(repository: MedicineRepository) : ViewModel() {
    val medicines: StateFlow<List<MedicineEntity>> =
        repository.getActiveMedicines().stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())
}
