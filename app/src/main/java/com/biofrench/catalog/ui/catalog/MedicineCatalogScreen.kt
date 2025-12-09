package com.biofrench.catalog.ui.catalog

import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import com.biofrench.catalog.ui.catalog.FullScreenImageDialog
import com.biofrench.catalog.ui.theme.BioFrenchTheme
import com.biofrench.catalog.R
import com.biofrench.catalog.ui.theme.primaryButtonColors
import com.biofrench.catalog.ui.catalog.Medicine
import com.biofrench.catalog.ui.catalog.MedicineCard
import com.biofrench.catalog.ui.catalog.toMedicine
import com.biofrench.catalog.ui.catalog.FullScreenImageDialog
import com.biofrench.catalog.data.database.AppDatabase
import com.biofrench.catalog.data.repository.MedicineRepository
import com.biofrench.catalog.ui.catalog.MedicineCatalogViewModel
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.room.Room

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MedicineCatalogScreen(
    viewModel: MedicineCatalogViewModel,
    onAdminClick: () -> Unit,
    onThankYou: () -> Unit,
    columns: Int = 3,
    cardAspectRatio: Float = 0.9f
) {
    var searchText by remember { mutableStateOf("") }
    var selectedSource by remember { mutableStateOf("Biofrench") }
    var showFullScreenImage by remember { mutableStateOf(false) }
    var selectedIndex by remember { mutableStateOf<Int?>(null) }
    var showOtherTab by remember { mutableStateOf(false) }
    val medicines by viewModel.medicines.collectAsState()
    val filteredMedicines = remember(searchText, medicines, selectedSource) {
        medicines
            .filter { med ->
                when (selectedSource) {
                    "Biofrench" -> med.source.equals("Biofrench", ignoreCase = true)
                    "Affiliate" -> med.preferredAffiliate && !med.source.equals("Biofrench", ignoreCase = true)
                    "Other" -> !med.source.equals("Biofrench", ignoreCase = true) && !med.preferredAffiliate
                    else -> true
                }
            }
            .filter { med ->
                searchText.isBlank() ||
                med.activeIngredient.contains(searchText, ignoreCase = true) ||
                med.brandName.contains(searchText, ignoreCase = true) ||
                med.category.contains(searchText, ignoreCase = true)
            }
            .map { it.toMedicine() }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header with logo, title, and Admin button
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Image(
                    painter = painterResource(id = R.drawable.logo_final),
                    contentDescription = "BioFrench Logo",
                    modifier = Modifier
                        .size(40.dp)
                        .padding(end = 8.dp)
                )
                Text(
                    text = "BioFrench Catalog",
                    style = MaterialTheme.typography.headlineMedium
                )
            }
            Row {
                IconButton(
                    onClick = onAdminClick,
                ) {
                    Icon(Icons.Default.Settings, contentDescription = "Settings")
                }
                Spacer(Modifier.width(8.dp))
                IconButton(
                    onClick = {
                        showOtherTab = !showOtherTab
                        if (!showOtherTab && selectedSource == "Other") {
                            selectedSource = "Biofrench"
                        }
                    },
                ) {
                    Icon(Icons.Filled.Star, contentDescription = "Toggle Other Tab")
                }
                Spacer(Modifier.width(8.dp))
                IconButton(
                    onClick = onThankYou,
                ) {
                    Icon(
                        painter = painterResource(id = R.drawable.ic_thank_you),
                        contentDescription = "Thank You"
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Source Switch Buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center
        ) {
            Button(
                onClick = { selectedSource = "Biofrench" },
                colors = if (selectedSource == "Biofrench") ButtonDefaults.buttonColors() else ButtonDefaults.outlinedButtonColors(),
                modifier = Modifier.padding(end = 4.dp)
            ) {
                Text("Biofrench")
            }
            Button(
                onClick = { selectedSource = "Affiliate" },
                colors = if (selectedSource == "Affiliate") ButtonDefaults.buttonColors() else ButtonDefaults.outlinedButtonColors(),
                modifier = Modifier.padding(horizontal = 4.dp)
            ) {
                Text("Affiliate")
            }
            if (showOtherTab) {
                Button(
                    onClick = { selectedSource = "Other" },
                    colors = if (selectedSource == "Other") ButtonDefaults.buttonColors() else ButtonDefaults.outlinedButtonColors(),
                    modifier = Modifier.padding(start = 4.dp)
                ) {
                    Text("Other")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Search Bar
        OutlinedTextField(
            value = searchText,
            onValueChange = { searchText = it },
            label = { Text("Search medicines...") },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Default.Search,
                    contentDescription = "Search"
                )
            },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Medicine List
        if (filteredMedicines.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (searchText.isBlank()) "No medicines available" else "No medicines found",
                    style = MaterialTheme.typography.bodyLarge
                )
            }
        } else {
            LazyVerticalGrid(
                columns = GridCells.Fixed(columns),
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(filteredMedicines) { medicine ->
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(4.dp)
                    ) {
                        MedicineCard(
                            medicine = medicine,
                            onClick = {
                                val index = filteredMedicines.indexOf(medicine)
                                if (index >= 0) {
                                    selectedIndex = index
                                    showFullScreenImage = true
                                }
                            },
                            aspectRatio = cardAspectRatio,
                            fixedHeight = 140.dp
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = medicine.brandName,
                            style = MaterialTheme.typography.bodySmall,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.onSurface,
                            maxLines = 2,
                            modifier = Modifier.padding(horizontal = 4.dp)
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Thank you button at the end
        IconButton(
            onClick = onThankYou,
            modifier = Modifier.align(Alignment.CenterHorizontally)
        ) {
            Icon(
                painter = painterResource(id = R.drawable.ic_thank_you),
                contentDescription = "Thank You"
            )
        }
    }

    // Full screen image dialog
    if (showFullScreenImage && selectedIndex != null) {
        FullScreenImageDialog(
            medicines = filteredMedicines,
            initialIndex = selectedIndex!!,
            onDismiss = {
                showFullScreenImage = false
                selectedIndex = null
            }
        )
    }
}
