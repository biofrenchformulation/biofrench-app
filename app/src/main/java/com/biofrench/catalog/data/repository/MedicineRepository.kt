package com.biofrench.catalog.data.repository

import com.biofrench.catalog.data.database.MedicineDao
import com.biofrench.catalog.data.model.MedicineEntity
import kotlinx.coroutines.flow.Flow

/**
 * Repository for managing medicine data.
 * Provides a clean API for accessing and modifying medicine data.
 * All database operations are delegated to the DAO.
 */
class MedicineRepository(private val medicineDao: MedicineDao) {
    
    /**
     * Get all medicines from the database, including inactive ones.
     * Returns a Flow that emits updates when the data changes.
     */
    fun getAllMedicines(): Flow<List<MedicineEntity>> = medicineDao.getAllMedicines()
    
    /**
     * Get only active medicines (isActive = true).
     * Used for displaying medicines in the catalog.
     */
    fun getActiveMedicines(): Flow<List<MedicineEntity>> = medicineDao.getActiveMedicines()
    
    /**
     * Insert a single medicine into the database.
     * If a medicine with the same ID exists, it will be replaced.
     */
    suspend fun insertMedicine(medicine: MedicineEntity) = medicineDao.insertMedicine(medicine)
    
    /**
     * Insert multiple medicines at once.
     * Useful for bulk imports from JSON files.
     */
    suspend fun insertMedicines(medicines: List<MedicineEntity>) = medicineDao.insertMedicines(medicines)
    
    /**
     * Update an existing medicine's information.
     */
    suspend fun updateMedicine(medicine: MedicineEntity) = medicineDao.updateMedicine(medicine)
    
    /**
     * Delete a medicine from the database.
     */
    suspend fun deleteMedicine(medicine: MedicineEntity) = medicineDao.deleteMedicine(medicine)
    
    /**
     * Delete all medicines from the database.
     * Used before importing a new dataset.
     */
    suspend fun deleteAllMedicines() = medicineDao.deleteAllMedicines()
    
    /**
     * Find a medicine by its string ID.
     * Returns null if not found.
     */
    suspend fun getMedicineByStringId(stringId: String) = medicineDao.getMedicineByStringId(stringId)
}
