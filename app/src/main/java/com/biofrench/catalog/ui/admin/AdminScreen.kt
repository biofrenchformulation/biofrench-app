package com.biofrench.catalog.ui.admin

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.FileOpen
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.StarBorder
import androidx.compose.material.icons.filled.Search
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.clickable
import androidx.compose.ui.window.Dialog
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.ui.platform.LocalContext
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import com.biofrench.catalog.data.model.MedicineEntity
import android.widget.Toast
import com.biofrench.catalog.ui.admin.getFilePathFromUri

@Composable
fun AdminScreen(
    viewModel: AdminViewModel,
    onBackClick: () -> Unit
) {
    val medicines by viewModel.medicines.collectAsState()
    var showDialog by remember { mutableStateOf(false) }
    var editingMedicine by remember { mutableStateOf<MedicineEntity?>(null) }
    var searchText by remember { mutableStateOf("") }
    val context = LocalContext.current

    val filteredMedicines = remember(searchText, medicines) {
        if (searchText.isBlank()) medicines else medicines.filter { med ->
            med.brandName.contains(searchText, ignoreCase = true) ||
            med.stringId.contains(searchText, ignoreCase = true)
        }
    }

    // File picker launcher
    val filePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let {
            val filePath = getFilePathFromUri(context, uri)
            if (filePath != null) {
                viewModel.importMedicinesFromJson(context, filePath) { count, error ->
                    if (error != null) {
                        Toast.makeText(context, error, Toast.LENGTH_LONG).show()
                    } else {
                        Toast.makeText(context, "Successfully imported $count medicines", Toast.LENGTH_LONG).show()
                    }
                }
            } else {
                Toast.makeText(context, "Unable to access the selected file", Toast.LENGTH_SHORT).show()
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Top,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Header with back button and title
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Start
        ) {
            IconButton(
                onClick = onBackClick,
                modifier = Modifier.padding(end = 8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Back to Catalog",
                    tint = MaterialTheme.colorScheme.onSurface
                )
            }
            Text(
                "Admin Medicine List",
                style = MaterialTheme.typography.headlineSmall,
                modifier = Modifier.weight(1f)
            )
        }
        Spacer(modifier = Modifier.height(16.dp))

        // Search Bar
        OutlinedTextField(
            value = searchText,
            onValueChange = { searchText = it },
            label = { Text("Search medicines...") },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Filled.Search,
                    contentDescription = "Search"
                )
            },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (filteredMedicines.isEmpty()) {
            Text("No medicines available.", style = MaterialTheme.typography.bodyLarge)
        } else {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(filteredMedicines) { medicine ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surface
                        )
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(medicine.brandName, fontWeight = FontWeight.Bold)
                            Row {
                                IconButton(
                                    onClick = {
                                        val toggled = medicine.copy(isActive = !medicine.isActive)
                                        viewModel.updateMedicine(toggled)
                                    }
                                ) {
                                    Icon(
                                        imageVector = if (medicine.isActive) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                        contentDescription = if (medicine.isActive) "Hide from catalog" else "Show in catalog",
                                        tint = MaterialTheme.colorScheme.onSurface
                                    )
                                }
                                IconButton(
                                    onClick = {
                                        // Do not allow changing affiliate flag for Biofrench source
                                        if (!medicine.source.equals("Biofrench", ignoreCase = true)) {
                                            val toggled = medicine.copy(preferredAffiliate = !medicine.preferredAffiliate)
                                            viewModel.updateMedicine(toggled)
                                        }
                                    }
                                ) {
                                    Icon(
                                        imageVector = if (medicine.preferredAffiliate) Icons.Default.Star else Icons.Default.StarBorder,
                                        contentDescription = if (medicine.preferredAffiliate) "Remove from preferred affiliates" else "Mark as preferred affiliate",
                                        tint = if (medicine.preferredAffiliate) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                                    )
                                }
                                IconButton(
                                    onClick = {
                                        editingMedicine = medicine
                                        showDialog = true
                                    }
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Edit,
                                        contentDescription = "Edit",
                                        tint = MaterialTheme.colorScheme.onSurface
                                    )
                                }
                                IconButton(
                                    onClick = { viewModel.deleteMedicine(medicine) }
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Delete,
                                        contentDescription = "Delete",
                                        tint = MaterialTheme.colorScheme.error
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Action buttons row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(
                onClick = {
                    editingMedicine = null
                    showDialog = true
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("Add New Medicine")
            }

            Button(
                onClick = {
                    filePickerLauncher.launch("application/json")
                },
                modifier = Modifier.weight(1f),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.secondary
                )
            ) {
                Icon(
                    Icons.Default.FileOpen,
                    contentDescription = "Import",
                    modifier = Modifier.size(16.dp)
                )
                Spacer(Modifier.width(4.dp))
                Text("Import JSON")
            }
        }

        if (showDialog) {
            Dialog(onDismissRequest = { showDialog = false }) {
                Surface(
                    shape = MaterialTheme.shapes.medium,
                    tonalElevation = 8.dp,
                    modifier = Modifier
                        .fillMaxWidth()
                        .heightIn(max = 600.dp) // Limit dialog height
                ) {
                    val scrollState = rememberScrollState()
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .verticalScroll(scrollState)
                            .padding(24.dp),
                        verticalArrangement = Arrangement.Top,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        var brandName by remember { mutableStateOf(editingMedicine?.brandName ?: "") }
                        var source by remember { mutableStateOf(editingMedicine?.source ?: "Biofrench") }
                        var stringId by remember { mutableStateOf(editingMedicine?.stringId ?: "") }
                        var showSuccess by remember { mutableStateOf(false) }

                        OutlinedTextField(
                            value = stringId,
                            onValueChange = { stringId = it },
                            label = { Text("Unique ID (for image)*") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedTextField(
                            value = brandName,
                            onValueChange = { brandName = it },
                            label = { Text("Brand Name*") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        // Source dropdown
                        OutlinedTextField(
                            value = source,
                            onValueChange = { source = it },
                            label = { Text("Source*") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        Button(
                            onClick = {
                                val medicine = MedicineEntity(
                                    id = editingMedicine?.id ?: 0,
                                    stringId = stringId,
                                    brandName = brandName,
                                    isActive = editingMedicine?.isActive ?: true,
                                    source = source
                                )
                                if (editingMedicine == null) {
                                    viewModel.addMedicine(medicine)
                                } else {
                                    viewModel.updateMedicine(medicine)
                                }
                                showSuccess = true
                                showDialog = false
                            },
                            enabled = stringId.isNotBlank() && brandName.isNotBlank(),
                            modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp)
                        ) {
                            Text(if (editingMedicine == null) "Add Medicine" else "Save Changes")
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedTextField(
                            value = stringId,
                            onValueChange = { stringId = it },
                            label = { Text("Unique ID (for image)") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )
                        if (showSuccess) {
                            Spacer(modifier = Modifier.height(16.dp))
                            Text("Medicine ${if (editingMedicine != null) "updated" else "added"} successfully!", color = MaterialTheme.colorScheme.primary)
                        }
                    }
                }
            }
        }
    }
}