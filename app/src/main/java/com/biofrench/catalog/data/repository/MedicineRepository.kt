package com.biofrench.catalog.data.repository

import com.biofrench.catalog.data.database.MedicineDao
import com.biofrench.catalog.data.model.MedicineEntity
import kotlinx.coroutines.flow.Flow

class MedicineRepository(private val medicineDao: MedicineDao) {
    fun getAllMedicines(): Flow<List<MedicineEntity>> = medicineDao.getAllMedicines()
    fun getActiveMedicines(): Flow<List<MedicineEntity>> = medicineDao.getActiveMedicines()
    suspend fun insertMedicine(medicine: MedicineEntity) = medicineDao.insertMedicine(medicine)
    suspend fun insertMedicines(medicines: List<MedicineEntity>) = medicineDao.insertMedicines(medicines)
    suspend fun updateMedicine(medicine: MedicineEntity) = medicineDao.updateMedicine(medicine)
    suspend fun deleteMedicine(medicine: MedicineEntity) = medicineDao.deleteMedicine(medicine)
    suspend fun deleteAllMedicines() = medicineDao.deleteAllMedicines()
    suspend fun getMedicineByStringId(stringId: String) = medicineDao.getMedicineByStringId(stringId)
}
