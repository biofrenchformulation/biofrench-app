package com.biofrench.catalog.ui.catalog

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.testTag
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import coil.compose.AsyncImage
import coil.ImageLoader
import coil.decode.SvgDecoder
import coil.request.ImageRequest
import com.biofrench.catalog.R
import androidx.compose.animation.core.animateIntOffsetAsState
import androidx.compose.animation.core.tween
import kotlinx.coroutines.launch
import kotlin.math.abs

@Composable
fun FullScreenImageDialog(
    medicines: List<Medicine>,
    initialIndex: Int,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    var currentPage by remember { mutableStateOf(initialIndex) }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(
            dismissOnBackPress = true,
            dismissOnClickOutside = true,
            usePlatformDefaultWidth = false
        )
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black)
        ) {
            // Swipeable image display
            val medicine = medicines[currentPage]
            val foundAsset = findMedicineImageAsset(context, medicine.id)

            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .pointerInput(Unit) {
                        var totalDrag = 0f
                        detectHorizontalDragGestures(
                            onHorizontalDrag = { _, dragAmount ->
                                totalDrag += dragAmount
                            },
                            onDragEnd = {
                                if (totalDrag < -100) {
                                    // Swipe left - next image
                                    if (currentPage < medicines.size - 1) {
                                        currentPage++
                                    }
                                } else if (totalDrag > 100) {
                                    // Swipe right - previous image
                                    if (currentPage > 0) {
                                        currentPage--
                                    }
                                }
                                totalDrag = 0f
                            }
                        )
                    }
                    .semantics { testTag = "fullScreenDialog" },
                contentAlignment = Alignment.Center
            ) {
                if (foundAsset != null) {
                    android.util.Log.d("FullScreenImageDialog", "Loading asset: file:///android_asset/images/$foundAsset")
                    val imageLoader = ImageLoader.Builder(context)
                        .apply {
                            if (foundAsset.endsWith(".svg", ignoreCase = true)) {
                                components { add(SvgDecoder.Factory()) }
                            }
                        }
                        .build()

                    AsyncImage(
                        model = ImageRequest.Builder(context)
                            .data("file:///android_asset/images/$foundAsset")
                            .crossfade(true)
                            .build(),
                        contentDescription = "Medicine Image",
                        imageLoader = imageLoader,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                } else {
                    // Fallback if image not found
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "Image not available",
                            color = Color.White,
                            style = MaterialTheme.typography.headlineMedium
                        )
                    }
                }
            }

            // Close button (drawn on top)
            IconButton(
                onClick = onDismiss,
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Close,
                    contentDescription = "Close",
                    tint = Color.White
                )
            }

            // Navigation buttons and page indicator
            if (medicines.size > 1) {
                Row(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    IconButton(
                        onClick = {
                            if (currentPage > 0) {
                                currentPage--
                            }
                        },
                        enabled = currentPage > 0
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Previous",
                            tint = if (currentPage > 0) Color.White else Color.Gray
                        )
                    }

                    Text(
                        text = "${currentPage + 1} / ${medicines.size}",
                        color = Color.White,
                        modifier = Modifier.align(Alignment.CenterVertically)
                    )

                    IconButton(
                        onClick = {
                            if (currentPage < medicines.size - 1) {
                                currentPage++
                            }
                        },
                        enabled = currentPage < medicines.size - 1
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowForward,
                            contentDescription = "Next",
                            tint = if (currentPage < medicines.size - 1) Color.White else Color.Gray
                        )
                    }
                }
            }
        }
    }
}