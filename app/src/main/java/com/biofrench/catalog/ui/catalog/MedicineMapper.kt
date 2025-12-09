package com.biofrench.catalog.ui.catalog

import com.biofrench.catalog.ui.catalog.Medicine
import com.biofrench.catalog.data.model.MedicineEntity

// Convert MedicineEntity to UI Medicine model
fun MedicineEntity.toMedicine(): Medicine = Medicine(
    id = this.stringId,
    brandName = this.brandName,
    source = this.source
)
