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
import com.biofrench.catalog.ui.details.MedicineDetailScreen
import com.biofrench.catalog.ui.theme.BioFrenchTheme
import com.biofrench.catalog.ui.admin.AdminScreen
import androidx.compose.runtime.remember
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory

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

@Composable
fun BioFrenchApp() {
    val navController = rememberNavController()
    val context = androidx.compose.ui.platform.LocalContext.current
    val db = remember {
        com.biofrench.catalog.data.database.AppDatabase.getDatabase(context.applicationContext)
    }
    val repository = remember { com.biofrench.catalog.data.repository.MedicineRepository(db.medicineDao()) }
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
        // Welcome screen
        composable("welcome") {
            com.biofrench.catalog.ui.welcome.WelcomeScreen(
                onContinue = { navController.navigate("catalog") }
            )
        }

        // Main catalog screen
        composable("catalog") {
            com.biofrench.catalog.ui.catalog.MedicineCatalogScreen(
                viewModel = catalogViewModel,
                onAdminClick = { navController.navigate("admin") },
                onMedicineClick = { medicineId -> navController.navigate("detail/$medicineId") },
                onThankYou = { navController.navigate("thankyou") }
            )
        }

        // Admin screen
        composable("admin") {
            com.biofrench.catalog.ui.admin.AdminScreen(
                viewModel = adminViewModel,
                onBackClick = { navController.popBackStack() }
            )
        }

        // Medicine detail screen
        composable("detail/{medicineId}") { backStackEntry ->
            val medicineId = backStackEntry.arguments?.getString("medicineId") ?: ""
            com.biofrench.catalog.ui.details.MedicineDetailScreen(
                medicineId = medicineId,
                onBackClick = {
                    navController.popBackStack()
                }
            )
        }

        // Thank you screen
        composable("thankyou") {
            com.biofrench.catalog.ui.catalog.ThankYouScreen()
        }
    }
}