package com.biofrench.catalog.ui.catalog

import com.biofrench.catalog.ui.catalog.Medicine
import com.biofrench.catalog.data.model.MedicineEntity

// Convert MedicineEntity to UI Medicine model
fun MedicineEntity.toMedicine(): Medicine = Medicine(
    id = this.stringId,
    activeIngredient = this.activeIngredient,
    brandName = this.brandName,
    category = this.category,
    dosage = this.dosage,
    source = this.source
)
