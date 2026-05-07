package com.biofrench.catalog.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.booleanResource
import androidx.compose.ui.res.painterResource
import com.biofrench.catalog.R

@Composable
fun ThankYouScreen() {
    val isAsvinsBrand = booleanResource(id = R.bool.is_asvins_brand)
    val thankYouDrawable = if (isAsvinsBrand) {
        R.drawable.thank_you_screen_asvins
    } else {
        R.drawable.thank_you_screen
    }

    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(id = thankYouDrawable),
            contentDescription = "Thank You Screen",
            modifier = Modifier.fillMaxSize()
        )
    }
}
