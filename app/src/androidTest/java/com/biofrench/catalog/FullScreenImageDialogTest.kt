package com.biofrench.catalog

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.biofrench.catalog.ui.catalog.Medicine
import com.biofrench.catalog.ui.catalog.FullScreenImageDialog
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class FullScreenImageDialogTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    private val sampleMedicines = listOf(
        Medicine(id = "1", brandName = "Brand 1"),
        Medicine(id = "2", brandName = "Brand 2"),
        Medicine(id = "3", brandName = "Brand 3")
    )

    @Test
    fun fullScreenImageDialog_displaysCorrectInitialImage() {
        var dismissed = false

        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 1,
                onDismiss = { dismissed = true }
            )
        }

        // Check that the dialog is displayed
        composeTestRule.onNodeWithTag("fullScreenDialog").assertIsDisplayed()

        // Check that the page indicator shows correct initial index
        composeTestRule.onNodeWithText("2 / 3").assertIsDisplayed()
    }

    @Test
    fun fullScreenImageDialog_closeButtonDismissesDialog() {
        var dismissed = false

        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 0,
                onDismiss = { dismissed = true }
            )
        }

        // Click the close button
        composeTestRule.onNodeWithContentDescription("Close").performClick()

        // Check that onDismiss was called
        assert(dismissed)
    }

    @Test
    fun fullScreenImageDialog_swipeLeftToNextImage() {
        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 0,
                onDismiss = {}
            )
        }

        // Initially shows 1 / 3
        composeTestRule.onNodeWithText("1 / 3").assertIsDisplayed()

        // Perform swipe left (to next image)
        composeTestRule.onNodeWithTag("fullScreenDialog")
            .performTouchInput {
                swipeLeft()
            }

        // Should now show 2 / 3
        composeTestRule.onNodeWithText("2 / 3").assertIsDisplayed()
    }

    @Test
    fun fullScreenImageDialog_swipeRightToPreviousImage() {
        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 1,
                onDismiss = {}
            )
        }

        // Initially shows 2 / 3
        composeTestRule.onNodeWithText("2 / 3").assertIsDisplayed()

        // Perform swipe right (to previous image)
        composeTestRule.onNodeWithTag("fullScreenDialog")
            .performTouchInput {
                swipeRight()
            }

        // Should now show 1 / 3
        composeTestRule.onNodeWithText("1 / 3").assertIsDisplayed()
    }

    @Test
    fun fullScreenImageDialog_navigationButtonsWork() {
        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 1,
                onDismiss = {}
            )
        }

        // Initially shows 2 / 3
        composeTestRule.onNodeWithText("2 / 3").assertIsDisplayed()

        // Click next button
        composeTestRule.onNodeWithContentDescription("Next").performClick()

        // Should show 3 / 3
        composeTestRule.onNodeWithText("3 / 3").assertIsDisplayed()

        // Click previous button
        composeTestRule.onNodeWithContentDescription("Previous").performClick()

        // Should show 2 / 3 again
        composeTestRule.onNodeWithText("2 / 3").assertIsDisplayed()
    }

    @Test
    fun fullScreenImageDialog_navigationButtonsDisabledAtBoundaries() {
        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 0,
                onDismiss = {}
            )
        }

        // At first image, previous button should be disabled
        composeTestRule.onNodeWithContentDescription("Previous").assertIsNotEnabled()

        // Navigate to last image
        repeat(2) {
            composeTestRule.onNodeWithContentDescription("Next").performClick()
        }

        // At last image, next button should be disabled
        composeTestRule.onNodeWithContentDescription("Next").assertIsNotEnabled()
    }

    @Test
    fun fullScreenImageDialog_clickOnImageDismissesDialog() {
        var dismissed = false

        composeTestRule.setContent {
            FullScreenImageDialog(
                medicines = sampleMedicines,
                initialIndex = 0,
                onDismiss = { dismissed = true }
            )
        }

        // Click on the image area (assuming it's clickable)
        composeTestRule.onNodeWithTag("fullScreenDialog").performClick()

        // Check that onDismiss was called
        assert(dismissed)
    }
}