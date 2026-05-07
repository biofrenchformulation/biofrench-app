package com.biofrench.catalog.ui.screens

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.booleanResource
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.biofrench.catalog.R

@Composable
fun WelcomeScreen(onContinue: () -> Unit) {
    val isAsvinsBrand = booleanResource(id = R.bool.is_asvins_brand)
    val welcomeDrawable = if (isAsvinsBrand) {
        R.drawable.welcome_screen_asvins
    } else {
        R.drawable.welcome_screen
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White)
            .clickable { onContinue() },
        contentAlignment = Alignment.Center
    ) {
        Image(
            painter = painterResource(id = welcomeDrawable),
            contentDescription = "Welcome Image",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.FillHeight
        )
        if (isAsvinsBrand) {
            Column(
                modifier = Modifier.align(Alignment.Center),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Image(
                    painter = painterResource(id = R.drawable.logo_final),
                    contentDescription = "Asvins Logo",
                    modifier = Modifier.size(96.dp)
                )
                Text(
                    text = stringResource(id = R.string.asvins_brand_title),
                    color = Color.White,
                    fontSize = 30.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}
