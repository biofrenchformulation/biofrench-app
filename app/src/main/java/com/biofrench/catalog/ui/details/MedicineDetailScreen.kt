package com.biofrench.catalog.ui.details

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.graphics.Color
import coil.compose.AsyncImage
import coil.ImageLoader
import coil.decode.SvgDecoder
import androidx.compose.ui.res.painterResource
import coil.request.ImageRequest
import androidx.compose.ui.layout.ContentScale
import com.biofrench.catalog.data.database.AppDatabase
import com.biofrench.catalog.data.repository.MedicineRepository
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.lifecycle.viewmodel.initializer
import com.biofrench.catalog.ui.theme.BioFrenchTheme

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MedicineDetailScreen(
    medicineId: String,
    onBackClick: () -> Unit = {}
) {
    val context = LocalContext.current
    android.util.Log.d("MedicineDetailScreen", "Composing MedicineDetailScreen for medicineId=$medicineId")
    val db = remember {
        androidx.room.Room.databaseBuilder(
            context.applicationContext,
            AppDatabase::class.java,
            "biofrench-db"
        ).build()
    }
    val repository = remember { MedicineRepository(db.medicineDao()) }
    val viewModel: MedicineDetailViewModel = viewModel(
        factory = viewModelFactory {
            initializer { MedicineDetailViewModel(repository) }
        }
    )
    val medicine by viewModel.medicine.collectAsState()

    LaunchedEffect(medicineId) {
        android.util.Log.d("MedicineDetailScreen", "LaunchedEffect: calling viewModel.loadMedicine($medicineId)")
        viewModel.loadMedicine(medicineId)
    }

    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        TopAppBar(
            title = { Text("Medicine Details") },
            navigationIcon = {
                IconButton(onClick = onBackClick) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back"
                    )
                }
            }
        )

        if (medicine == null) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                android.util.Log.d("MedicineDetailScreen", "medicine is null for id=$medicineId")
                Text("Medicine details not available.")
            }
        } else {
            val med = medicine!!
            android.util.Log.d("MedicineDetailScreen", "Loaded medicine: id=${med.id}, brandName=${med.brandName}, genericName=${med.activeIngredient}")
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            text = med.activeIngredient,
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = med.brandName,
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Surface(
                                color = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f),
                                shape = RoundedCornerShape(16.dp)
                            ) {
                                Text(
                                    text = med.category,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.primary
                                )
                            }
                            Surface(
                                color = MaterialTheme.colorScheme.secondary.copy(alpha = 0.1f),
                                shape = RoundedCornerShape(16.dp)
                            ) {
                                Text(
                                    text = med.dosage,
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.secondary
                                )
                            }
                        }
                        // Main image display using id-based logic: show up to three images (id-1, id-2, id-3)
                        val localContext = LocalContext.current
                        val supportedExts = listOf("svg", "png", "jpg", "jpeg")
                        val imageIds = listOf(1, 2, 3)
                        android.util.Log.d("MedicineDetailScreen", "Checking images for med.stringId=${med.stringId}")
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 8.dp),
                            horizontalArrangement = Arrangement.Center
                        ) {
                            imageIds.mapNotNull { idx ->
                                android.util.Log.d("MedicineDetailScreen", "Trying image index $idx for med.stringId=${med.stringId}")
                                supportedExts.firstNotNullOfOrNull { ext ->
                                    val assetName = "${med.stringId}-$idx.$ext"
                                    android.util.Log.d("MedicineDetailScreen", "Checking asset existence: images/$assetName")
                                    try {
                                        localContext.assets.open("images/$assetName").close()
                                        android.util.Log.d("MedicineDetailScreen", "Asset exists: images/$assetName")
                                        assetName
                                    } catch (_: Exception) {
                                        android.util.Log.d("MedicineDetailScreen", "Asset not found: images/$assetName")
                                        null
                                    }
                                }
                            }.let { assetsList ->
                                if (assetsList.isEmpty()) {
                                    android.util.Log.d("MedicineDetailScreen", "No asset found for ${med.stringId} (1,2,3), showing fallback icon")
                                    Icon(
                                        painter = painterResource(id = com.biofrench.catalog.R.drawable.ic_broken_image),
                                        contentDescription = "No image",
                                        modifier = Modifier.size(48.dp).align(Alignment.CenterVertically),
                                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
                                    )
                                } else {
                                    var showDialog by remember { mutableStateOf<String?>(null) }
                                    assetsList.forEach { foundAsset ->
                                        android.util.Log.d("MedicineDetailScreen", "Loading asset: file:///android_asset/images/$foundAsset")
                                        val imageLoader = ImageLoader.Builder(localContext)
                                            .apply {
                                                if (foundAsset.endsWith(".svg", ignoreCase = true)) {
                                                    components { add(SvgDecoder.Factory()) }
                                                }
                                            }
                                            .build()
                                        Card(
                                            modifier = Modifier
                                                .weight(1f)
                                                .aspectRatio(1f)
                                                .padding(horizontal = 4.dp)
                                                .clickable { showDialog = foundAsset },
                                            shape = RoundedCornerShape(20.dp),
                                            elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
                                        ) {
                                            android.util.Log.d("MedicineDetailScreen", "Displaying image card for asset: $foundAsset")
                                            AsyncImage(
                                                model = ImageRequest.Builder(localContext)
                                                    .data("file:///android_asset/images/$foundAsset")
                                                    .crossfade(true)
                                                    .build(),
                                                imageLoader = imageLoader,
                                                contentDescription = null,
                                                modifier = Modifier.fillMaxSize(),
                                                contentScale = ContentScale.Fit
                                            )
                                        }
                                        if (showDialog == foundAsset) {
                                            FullscreenImageDialog(
                                                imageUrl = foundAsset,
                                                imageLoader = imageLoader,
                                                onDismiss = { showDialog = null }
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        // (removed duplicate/old AsyncImage code)

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            text = "Description",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = med.description.ifBlank { "No description available." },
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
                InfoCard(title = "Key Features", items = med.keyFeatures)
                Spacer(modifier = Modifier.height(8.dp))
                InfoCard(title = "Common Side Effects", items = med.commonSideEffects)
                Spacer(modifier = Modifier.height(8.dp))
                InfoCard(title = "Indicated In", items = med.indicatedIn)
                Spacer(modifier = Modifier.height(8.dp))
                        InfoCard(title = "Drug Interactions", items = med.drugInteractions)
                    }
                }
            }
        }
    }
}

@Composable
fun InfoCard(
    title: String,
    items: List<String>
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            items.forEach { item ->
                Row(
                    modifier = Modifier.padding(vertical = 2.dp)
                ) {
                    Text(
                        text = "• ",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = item,
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

@Composable
fun FullscreenImageDialog(
    imageUrl: String,
    imageLoader: ImageLoader,
    onDismiss: () -> Unit
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            usePlatformDefaultWidth = false,
            dismissOnBackPress = true,
            dismissOnClickOutside = true
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black)
                .clickable { onDismiss() },
            contentAlignment = Alignment.Center
        ) {
            val imageContext = LocalContext.current
            AsyncImage(
                model = coil.request.ImageRequest.Builder(imageContext)
                    .data("file:///android_asset/images/$imageUrl")
                    .crossfade(true)
                    .build(),
                imageLoader = imageLoader,
                contentDescription = "Fullscreen image",
                modifier = Modifier.fillMaxSize()
            )
            
            // Close button
            IconButton(
                onClick = onDismiss,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Close",
                    tint = Color.White,
                    modifier = Modifier.size(32.dp)
                )
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun MedicineDetailScreenPreview() {
    BioFrenchTheme {
        MedicineDetailScreen(medicineId = "1")
    }
}