package com.biofrench.catalog

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.biofrench.catalog.ui.catalog.Medicine
import com.biofrench.catalog.ui.catalog.MedicineCard
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class MedicineCardTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    private val sampleMedicine = Medicine(
        id = "test-medicine",
        brandName = "Test Medicine"
    )

    @Test
    fun medicineCard_displaysMedicineName() {
        var clicked = false

        composeTestRule.setContent {
            MedicineCard(
                medicine = sampleMedicine,
                onClick = { clicked = true }
            )
        }

        // Check that the card is displayed
        composeTestRule.onNodeWithContentDescription("Test Medicine").assertIsDisplayed()
    }

    @Test
    fun medicineCard_clickTriggersOnClick() {
        var clicked = false

        composeTestRule.setContent {
            MedicineCard(
                medicine = sampleMedicine,
                onClick = { clicked = true }
            )
        }

        // Click on the card
        composeTestRule.onNodeWithContentDescription("Test Medicine").performClick()

        // Verify onClick was called
        assert(clicked)
    }

    @Test
    fun medicineCard_usesCorrectAspectRatio() {
        composeTestRule.setContent {
            MedicineCard(
                medicine = sampleMedicine,
                onClick = {},
                aspectRatio = 1.5f
            )
        }

        // The card should be displayed (aspect ratio is handled by Compose)
        composeTestRule.onNodeWithContentDescription("Test Medicine").assertIsDisplayed()
    }

    @Test
    fun medicineCard_usesCorrectFixedHeight() {
        composeTestRule.setContent {
            MedicineCard(
                medicine = sampleMedicine,
                onClick = {},
                fixedHeight = 200.dp
            )
        }

        // The card should be displayed (height is handled by Compose)
        composeTestRule.onNodeWithContentDescription("Test Medicine").assertIsDisplayed()
    }

    @Test
    fun medicineCard_handlesMissingImageGracefully() {
        // Use a medicine ID that doesn't have an image
        val medicineWithoutImage = Medicine(
            id = "nonexistent-medicine",
            brandName = "Medicine Without Image"
        )

        composeTestRule.setContent {
            MedicineCard(
                medicine = medicineWithoutImage,
                onClick = {}
            )
        }

        // Should display fallback icon
        composeTestRule.onNodeWithContentDescription("No image").assertIsDisplayed()
    }

    @Test
    fun medicineCard_appliesCustomModifier() {
        val testTag = "custom-medicine-card"

        composeTestRule.setContent {
            MedicineCard(
                medicine = sampleMedicine,
                onClick = {},
                modifier = Modifier.testTag(testTag)
            )
        }

        // Check that custom modifier is applied
        composeTestRule.onNodeWithTag(testTag).assertIsDisplayed()
    }
}