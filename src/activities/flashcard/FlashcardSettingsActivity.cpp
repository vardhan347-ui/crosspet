#include "FlashcardSettingsActivity.h"

#include <GfxRenderer.h>
#include <I18n.h>

#include "CrossPetSettings.h"
#include "components/UITheme.h"
#include "fontIds.h"

static constexpr int SETTINGS_COUNT = 3;
static constexpr uint8_t NEW_PER_DAY_MIN  = 5;
static constexpr uint8_t NEW_PER_DAY_MAX  = 50;
static constexpr uint8_t NEW_PER_DAY_STEP = 5;
static constexpr uint8_t MAX_REVIEW_MIN   = 25;
static constexpr uint8_t MAX_REVIEW_MAX   = 250;
static constexpr uint8_t MAX_REVIEW_STEP  = 25;
static constexpr uint8_t FONT_SIZE_MIN    = 0;
static constexpr uint8_t FONT_SIZE_MAX    = 3;

void FlashcardSettingsActivity::onEnter() {
    Activity::onEnter();
    newPerDay = PET_SETTINGS.flashcardNewPerDay;
    maxReview = PET_SETTINGS.flashcardMaxReviewPerDay;
    fontSizeIndex = PET_SETTINGS.flashcardFontSize;

    if (newPerDay < NEW_PER_DAY_MIN || newPerDay > NEW_PER_DAY_MAX)
        newPerDay = (newPerDay < NEW_PER_DAY_MIN) ? NEW_PER_DAY_MIN : NEW_PER_DAY_MAX;
    if (maxReview < MAX_REVIEW_MIN || maxReview > MAX_REVIEW_MAX)
        maxReview = (maxReview < MAX_REVIEW_MIN) ? MAX_REVIEW_MIN : MAX_REVIEW_MAX;
    if (fontSizeIndex > FONT_SIZE_MAX)
        fontSizeIndex = FONT_SIZE_MAX;

    requestUpdate();
}

void FlashcardSettingsActivity::saveSettings() {
    PET_SETTINGS.flashcardNewPerDay = newPerDay;
    PET_SETTINGS.flashcardMaxReviewPerDay = maxReview;
    PET_SETTINGS.flashcardFontSize = fontSizeIndex;
    PET_SETTINGS.saveToFile();
}

void FlashcardSettingsActivity::loop() {
    if (!editing) {
        buttonNavigator.onNext([this] {
            selectedIndex = ButtonNavigator::nextIndex(selectedIndex, SETTINGS_COUNT);
            requestUpdate();
        });
        buttonNavigator.onPrevious([this] {
            selectedIndex = ButtonNavigator::previousIndex(selectedIndex, SETTINGS_COUNT);
            requestUpdate();
        });
        if (mappedInput.wasReleased(MappedInputManager::Button::Confirm)) {
            editing = true;
            requestUpdate();
        }
        if (mappedInput.wasReleased(MappedInputManager::Button::Back)) {
            saveSettings();
            finish();
        }
    } else {
        buttonNavigator.onNext([this] {
            if (selectedIndex == 0) {
                if (static_cast<int>(newPerDay) + NEW_PER_DAY_STEP <= NEW_PER_DAY_MAX)
                    newPerDay += NEW_PER_DAY_STEP;
                else
                    newPerDay = NEW_PER_DAY_MAX;
            } else if (selectedIndex == 1) {
                if (static_cast<int>(maxReview) + MAX_REVIEW_STEP <= MAX_REVIEW_MAX)
                    maxReview += MAX_REVIEW_STEP;
                else
                    maxReview = MAX_REVIEW_MAX;
            } else {
                if (fontSizeIndex < FONT_SIZE_MAX)
                    fontSizeIndex++;
            }
            requestUpdate();
        });
        buttonNavigator.onPrevious([this] {
            if (selectedIndex == 0) {
                if (static_cast<int>(newPerDay) - NEW_PER_DAY_STEP >= NEW_PER_DAY_MIN)
                    newPerDay -= NEW_PER_DAY_STEP;
                else
                    newPerDay = NEW_PER_DAY_MIN;
            } else if (selectedIndex == 1) {
                if (static_cast<int>(maxReview) - MAX_REVIEW_STEP >= MAX_REVIEW_MIN)
                    maxReview -= MAX_REVIEW_STEP;
                else
                    maxReview = MAX_REVIEW_MIN;
            } else {
                if (fontSizeIndex > FONT_SIZE_MIN)
                    fontSizeIndex--;
            }
            requestUpdate();
        });
        if (mappedInput.wasReleased(MappedInputManager::Button::Confirm) ||
            mappedInput.wasReleased(MappedInputManager::Button::Back)) {
            editing = false;
            requestUpdate();
        }
    }
}

void FlashcardSettingsActivity::render(RenderLock&&) {
    const auto& metrics = UITheme::getInstance().getMetrics();
    const int pageWidth = renderer.getScreenWidth();
    const int pageHeight = renderer.getScreenHeight();

    renderer.clearScreen();

    GUI.drawHeader(renderer,
                   Rect{0, metrics.topPadding, pageWidth, metrics.headerHeight},
                   tr(STR_FLASHCARD_SETTINGS));

    const int menuTop = metrics.topPadding + metrics.headerHeight + metrics.verticalSpacing;
    const int menuHeight = pageHeight - menuTop - metrics.buttonHintsHeight - metrics.verticalSpacing;

    static const char* const FONT_SIZE_LABELS[] = {
        tr(STR_SMALL), tr(STR_MEDIUM), tr(STR_LARGE), tr(STR_X_LARGE)};

    char val0[16], val1[16], val2[32];
    if (editing && selectedIndex == 0) {
        snprintf(val0, sizeof(val0), "[ %d ]", static_cast<int>(newPerDay));
    } else {
        snprintf(val0, sizeof(val0), "%d", static_cast<int>(newPerDay));
    }
    if (editing && selectedIndex == 1) {
        snprintf(val1, sizeof(val1), "[ %d ]", static_cast<int>(maxReview));
    } else {
        snprintf(val1, sizeof(val1), "%d", static_cast<int>(maxReview));
    }
    const char* sizeLabel = FONT_SIZE_LABELS[fontSizeIndex];
    if (editing && selectedIndex == 2) {
        snprintf(val2, sizeof(val2), "[ %s ]", sizeLabel);
    } else {
        snprintf(val2, sizeof(val2), "%s", sizeLabel);
    }

    const char* values[SETTINGS_COUNT] = {val0, val1, val2};

    GUI.drawList(
        renderer,
        Rect{0, menuTop, pageWidth, menuHeight},
        SETTINGS_COUNT,
        selectedIndex,
        [](int i) -> std::string {
            if (i == 0) return tr(STR_FLASHCARD_NEW_PER_DAY);
            if (i == 1) return tr(STR_FLASHCARD_MAX_REVIEW);
            return tr(STR_FONT_SIZE);
        },
        nullptr,
        nullptr,
        [&values](int i) -> std::string {
            return values[i];
        },
        true);

    const auto labels = mappedInput.mapLabels(tr(STR_BACK), tr(STR_SELECT),
                                             tr(STR_DIR_UP), tr(STR_DIR_DOWN));
    GUI.drawButtonHints(renderer, labels.btn1, labels.btn2, labels.btn3, labels.btn4);

    renderer.displayBuffer();
}
