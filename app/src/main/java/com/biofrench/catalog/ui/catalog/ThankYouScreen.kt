package com.biofrench.catalog.ui.catalog

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import com.biofrench.catalog.R

@Composable
fun ThankYouScreen() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(id = R.drawable.thank_you_screen),
            contentDescription = "Thank You Screen",
            modifier = Modifier.fillMaxSize()
        )
    }
}
