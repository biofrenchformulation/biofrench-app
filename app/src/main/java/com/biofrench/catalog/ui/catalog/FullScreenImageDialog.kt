package com.biofrench.catalog.ui.catalog

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import coil.compose.AsyncImage
import coil.ImageLoader
import coil.decode.SvgDecoder
import coil.request.ImageRequest
import com.biofrench.catalog.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FullScreenImageDialog(
    medicineId: String,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current

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
                    tint = Color.White
                )
            }

            // Full screen image - use same logic as MedicineCard
            val supportedExts = listOf("svg", "png", "jpg", "jpeg")
            val foundAsset = supportedExts.firstNotNullOfOrNull { ext ->
                val assetName = "${medicineId}-1.$ext"
                try {
                    context.assets.open("images/$assetName").close()
                    assetName
                } catch (_: Exception) {
                    null
                }
            }

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
                    modifier = Modifier
                        .fillMaxSize()
                        .clickable(onClick = onDismiss),
                    contentScale = ContentScale.Fit
                )
            } else {
                // Fallback if image not found
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .clickable(onClick = onDismiss),
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
    }
}