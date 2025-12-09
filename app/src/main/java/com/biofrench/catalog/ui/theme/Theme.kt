package com.biofrench.catalog.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Modernized Color Palette
val RoyalBlue = Color(0xFF1E3A8A)
val SkyBlue = Color(0xFF38BDF8)
val WarmOrange = Color(0xFFF97316)
val CharcoalGray = Color(0xFF1F2937)
val CoolGray = Color(0xFFF3F4F6)
val PureWhite = Color(0xFFFFFFFF)
val MediumGray = Color(0xFF4B5563)

val LightColorScheme = lightColorScheme(
    primary = RoyalBlue,
    onPrimary = PureWhite,
    primaryContainer = SkyBlue,
    onPrimaryContainer = CharcoalGray,
    secondary = SkyBlue,
    onSecondary = PureWhite,
    secondaryContainer = WarmOrange,
    onSecondaryContainer = PureWhite,
    background = PureWhite,
    onBackground = CharcoalGray,
    surface = CoolGray,
    onSurface = CharcoalGray,
    surfaceVariant = PureWhite,
    onSurfaceVariant = MediumGray,
    outline = MediumGray,
    error = WarmOrange,
    onError = PureWhite,
    tertiary = WarmOrange,
    onTertiary = PureWhite
)

val DarkColorScheme = darkColorScheme(
    primary = RoyalBlue,
    onPrimary = PureWhite,
    primaryContainer = SkyBlue,
    onPrimaryContainer = CharcoalGray,
    secondary = SkyBlue,
    onSecondary = PureWhite,
    secondaryContainer = WarmOrange,
    onSecondaryContainer = PureWhite,
    background = CharcoalGray,
    onBackground = PureWhite,
    surface = CharcoalGray,
    onSurface = PureWhite,
    surfaceVariant = MediumGray,
    onSurfaceVariant = CoolGray,
    outline = MediumGray,
    error = WarmOrange,
    onError = PureWhite,
    tertiary = WarmOrange,
    onTertiary = PureWhite
)

@Composable
fun primaryButtonColors(): ButtonColors = ButtonDefaults.buttonColors(
    containerColor = RoyalBlue,
    contentColor = PureWhite
)

@Composable
fun BioFrenchTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}