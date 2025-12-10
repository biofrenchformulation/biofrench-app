package com.biofrench.catalog

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.biofrench.catalog.ui.catalog.MedicineCatalogScreen
import com.biofrench.catalog.ui.theme.BioFrenchTheme
import com.biofrench.catalog.ui.admin.AdminScreen
import com.biofrench.catalog.ui.screens.WelcomeScreen
import com.biofrench.catalog.ui.screens.ThankYouScreen
import androidx.compose.runtime.remember
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory

/**
 * Main Activity for the BioFrench Catalog application.
 * This is the single activity that hosts all screens using Jetpack Compose navigation.
 */
class MainActivity : ComponentActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BioFrenchTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    BioFrenchApp()
                }
            }
        }
    }
}

/**
 * Root composable for the BioFrench application.
 * Sets up database, repository, ViewModels, and navigation.
 */
@Composable
fun BioFrenchApp() {
    val navController = rememberNavController()
    val context = androidx.compose.ui.platform.LocalContext.current
    
    // Initialize database and repository - done once and remembered
    val db = remember {
        com.biofrench.catalog.data.database.AppDatabase.getDatabase(context.applicationContext)
    }
    val repository = remember { com.biofrench.catalog.data.repository.MedicineRepository(db.medicineDao()) }
    
    // Create ViewModels with repository dependency
    val catalogViewModel = androidx.lifecycle.viewmodel.compose.viewModel<
        com.biofrench.catalog.ui.catalog.MedicineCatalogViewModel>(
        factory = androidx.lifecycle.viewmodel.viewModelFactory {
            initializer { com.biofrench.catalog.ui.catalog.MedicineCatalogViewModel(repository) }
        }
    )
    val adminViewModel = androidx.lifecycle.viewmodel.compose.viewModel<
        com.biofrench.catalog.ui.admin.AdminViewModel>(
        factory = androidx.lifecycle.viewmodel.viewModelFactory {
            initializer { com.biofrench.catalog.ui.admin.AdminViewModel(repository) }
        }
    )
    
    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        BioFrenchNavHost(
            navController = navController,
            catalogViewModel = catalogViewModel,
            adminViewModel = adminViewModel,
            modifier = Modifier.padding(innerPadding)
        )
    }
}

/**
 * Navigation host for the BioFrench application.
 * Defines all navigation routes and screen destinations.
 * 
 * Navigation Routes:
 * - "welcome" - Initial welcome/splash screen
 * - "catalog" - Main medicine catalog screen (default after welcome)
 * - "admin" - Admin panel for medicine management
 * - "thankyou" - Thank you screen
 */
@Composable
fun BioFrenchNavHost(
    navController: NavHostController,
    catalogViewModel: com.biofrench.catalog.ui.catalog.MedicineCatalogViewModel,
    adminViewModel: com.biofrench.catalog.ui.admin.AdminViewModel,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = "welcome",
        modifier = modifier
    ) {
        // Welcome screen - shown on app launch
        composable("welcome") {
            WelcomeScreen(
                onContinue = { navController.navigate("catalog") }
            )
        }

        // Main catalog screen - browse and search medicines
        composable("catalog") {
            MedicineCatalogScreen(
                viewModel = catalogViewModel,
                onAdminClick = { navController.navigate("admin") },
                onThankYou = { navController.navigate("thankyou") }
            )
        }

        // Admin screen - manage medicine database
        composable("admin") {
            AdminScreen(
                viewModel = adminViewModel,
                onBackClick = { navController.popBackStack() }
            )
        }

        // Thank you screen
        composable("thankyou") {
            ThankYouScreen()
        }
    }
}