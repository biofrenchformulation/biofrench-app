package com.biofrench.catalog.ui.catalog

import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import com.biofrench.catalog.R
import coil.compose.AsyncImage
import androidx.compose.foundation.background
import com.biofrench.catalog.ui.catalog.Medicine

@Composable
fun MedicineCard(
    medicine: Medicine,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    aspectRatio: Float = 0.9f,
    fixedHeight: Dp = 140.dp
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .aspectRatio(aspectRatio)
            .height(fixedHeight)
            .clickable { onClick() },
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.Transparent, // No white background
            contentColor = MaterialTheme.colorScheme.onSurface,
            disabledContainerColor = Color.Transparent,
            disabledContentColor = MaterialTheme.colorScheme.onSurface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp), // No shadow
        contentPadding = PaddingValues(0.dp)
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
                // Use id-based image logic: try id-1 with supported extensions
                val context = androidx.compose.ui.platform.LocalContext.current
                val supportedExts = listOf("svg", "png", "jpg", "jpeg")
                val foundAsset = supportedExts.firstNotNullOfOrNull { ext ->
                    val assetName = "${medicine.id}-1.$ext"
                    try {
                        context.assets.open("images/$assetName").close()
                        assetName
                    } catch (_: Exception) {
                        null
                    }
                }
                if (foundAsset != null) {
                    android.util.Log.d("MedicineCard", "Loading asset: file:///android_asset/images/$foundAsset")
                    val imageLoader = coil.ImageLoader.Builder(context)
                        .apply {
                            if (foundAsset.endsWith(".svg", ignoreCase = true)) {
                                components { add(coil.decode.SvgDecoder.Factory()) }
                            }
                        }
                        .build()
                    AsyncImage(
                        model = coil.request.ImageRequest.Builder(context)
                            .data("file:///android_asset/images/$foundAsset")
                            .crossfade(true)
                            .build(),
                        imageLoader = imageLoader,
                        contentDescription = medicine.brandName,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = androidx.compose.ui.layout.ContentScale.Fit
                    )
                } else {
                    android.util.Log.d("MedicineCard", "No asset found for ${medicine.id}-1, showing fallback icon")
                    Icon(
                        painter = painterResource(id = com.biofrench.catalog.R.drawable.ic_broken_image),
                        contentDescription = "No image",
                        modifier = Modifier.size(48.dp).align(Alignment.Center),
                        tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)
                    )
                }
        }
    }
}