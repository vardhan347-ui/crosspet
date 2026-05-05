#include "FlashcardReviewActivity.h"

#include <GfxRenderer.h>
#include <HalGPIO.h>
#include <I18n.h>

#include <cstring>

#include "components/UITheme.h"
#include "CrossPetSettings.h"
#include "fontIds.h"
#include "FlashcardDoneActivity.h"

// --- Font size helper ---

// Returns the Bookerly font ID matching the user's flashcard font size setting.
// Indices: 0=Small(12pt) 1=Medium(14pt) 2=Large(16pt) 3=XLarge(18pt)
static int flashcardBodyFont() {
    switch (PET_SETTINGS.flashcardFontSize) {
        case 0:  return BOOKERLY_12_FONT_ID;
        case 2:  return BOOKERLY_16_FONT_ID;
        case 3:  return BOOKERLY_18_FONT_ID;
        default: return BOOKERLY_14_FONT_ID;  // 1 = Medium (default)
    }
}

// --- Constructor ---

FlashcardReviewActivity::FlashcardReviewActivity(GfxRenderer& renderer,
                                                 MappedInputManager& mappedInput,
                                                 const std::string& deckPath)
    : Activity("FlashcardReview", renderer, mappedInput), deckPath(deckPath) {}

// --- Lifecycle ---

void FlashcardReviewActivity::onEnter() {
    Activity::onEnter();
    today = FlashcardSrs::getToday();
    deck.loadFromCsv(deckPath.c_str());
    reviewQueue = deck.buildReviewQueue(today,
                                        PET_SETTINGS.flashcardNewPerDay,
                                        PET_SETTINGS.flashcardMaxReviewPerDay);
    currentQueueIndex = 0;
    cardState = CardState::Front;
    saveCounter = 0;

    if (reviewQueue.empty()) {
        activityManager.pushActivity(
            std::make_unique<FlashcardDoneActivity>(renderer, mappedInput));
        return;
    }
    maxQueueSize = reviewQueue.size() * 2;
    requestUpdate();
}

// --- Input loop ---

void FlashcardReviewActivity::loop() {
    if (reviewQueue.empty() || currentQueueIndex >= reviewQueue.size()) return;

    if (cardState == CardState::Front) {
        if (mappedInput.wasReleased(MappedInputManager::Button::Back)) {
            deck.saveToCsv(deckPath.c_str());
            finish();
            return;
        }
        if (mappedInput.wasReleased(MappedInputManager::Button::Confirm)) {
            flipCard();
        }
    } else {
        if (mappedInput.wasReleased(MappedInputManager::Button::Back)) {
            rateCard(SrsRating::Again);
        } else if (mappedInput.wasReleased(MappedInputManager::Button::Left) ||
                   mappedInput.wasReleased(MappedInputManager::Button::Up)) {
            rateCard(SrsRating::Hard);
        } else if (mappedInput.wasReleased(MappedInputManager::Button::Right) ||
                   mappedInput.wasReleased(MappedInputManager::Button::Down)) {
            rateCard(SrsRating::Good);
        } else if (mappedInput.wasReleased(MappedInputManager::Button::Confirm)) {
            rateCard(SrsRating::Easy);
        }
    }
}

// --- Card state transitions ---

void FlashcardReviewActivity::flipCard() {
    cardState = CardState::Back;
    requestUpdate();
}

void FlashcardReviewActivity::rateCard(SrsRating rating) {
    size_t cardIdx = reviewQueue[currentQueueIndex];
    auto& card = deck.getCards()[cardIdx];
    SrsState newState = FlashcardSrs::review(card.srs, rating, today);
    deck.updateCard(cardIdx, newState);

    if (rating == SrsRating::Again && reviewQueue.size() < maxQueueSize) {
        reviewQueue.push_back(cardIdx);
    }

    currentQueueIndex++;
    saveCounter++;

    if (saveCounter >= 5) {
        deck.saveToCsv(deckPath.c_str());
        saveCounter = 0;
    }

    if (currentQueueIndex >= reviewQueue.size()) {
        deck.saveToCsv(deckPath.c_str());
        activityManager.pushActivity(
            std::make_unique<FlashcardDoneActivity>(renderer, mappedInput));
    } else {
        cardState = CardState::Front;
        requestUpdate();
    }
}

// --- Render ---

void FlashcardReviewActivity::render(RenderLock&&) {
    if (reviewQueue.empty() || currentQueueIndex >= reviewQueue.size()) return;

    const auto& card = deck.getCards()[reviewQueue[currentQueueIndex]];
    renderer.clearScreen();

    const auto& metrics = UITheme::getInstance().getMetrics();
    auto pageWidth = renderer.getScreenWidth();

    GUI.drawHeader(renderer,
                   Rect{0, metrics.topPadding, pageWidth, metrics.headerHeight},
                   deck.getName().c_str());

    if (cardState == CardState::Front) {
        renderFront(card);
    } else {
        renderBack(card);
    }

    renderer.displayBuffer();
}

// --- renderFront ---

void FlashcardReviewActivity::renderFront(const FlashcardCard& card) {
    const auto& metrics = UITheme::getInstance().getMetrics();
    auto pageHeight = renderer.getScreenHeight();
    int contentTop = metrics.topPadding + metrics.headerHeight + metrics.verticalSpacing;
    int contentBottom = pageHeight - metrics.buttonHintsHeight - metrics.verticalSpacing;
    int contentHeight = contentBottom - contentTop;

    std::string mainText = card.frontMain();
    int mainLineHeight = renderer.getLineHeight(flashcardBodyFont());

    int textY = contentTop + contentHeight / 3;

    size_t pos = 0;
    while (pos < mainText.size()) {
        size_t nl = mainText.find('\n', pos);
        std::string line = (nl == std::string::npos)
                               ? mainText.substr(pos)
                               : mainText.substr(pos, nl - pos);
        renderer.drawCenteredText(flashcardBodyFont(), textY, line.c_str());
        textY += mainLineHeight;
        pos = (nl == std::string::npos) ? mainText.size() : nl + 1;
    }

    std::string hint = card.frontHint();
    if (!hint.empty()) {
        textY += metrics.verticalSpacing;
        renderer.drawCenteredText(UI_10_FONT_ID, textY, hint.c_str());
    }

    const auto labels = mappedInput.mapLabels(tr(STR_BACK), tr(STR_FLASHCARD_SHOW), "", "");
    GUI.drawButtonHints(renderer, labels.btn1, labels.btn2, labels.btn3, labels.btn4);
}

// --- renderBack ---

void FlashcardReviewActivity::renderBack(const FlashcardCard& card) {
    const auto& metrics = UITheme::getInstance().getMetrics();
    auto pageWidth = renderer.getScreenWidth();
    auto pageHeight = renderer.getScreenHeight();
    int contentTop = metrics.topPadding + metrics.headerHeight + metrics.verticalSpacing;

    const auto origOrientation = renderer.getOrientation();
    renderer.setOrientation(GfxRenderer::Orientation::Portrait);

    constexpr int btnWidth = 106;
    constexpr int btnHeight = 50;
    const int portHeight = renderer.getScreenHeight();
    const int btnY = portHeight - btnHeight;
    const int x4Pos[] = {25, 130, 245, 350};
    const int x3Pos[] = {38, 154, 268, 384};
    const int* btnPos = gpio.deviceIsX3() ? x3Pos : x4Pos;

    const auto& srs = card.srs;
    char iv1[16], iv2[16], iv3[16], iv4[16];
    strncpy(iv1, FlashcardSrs::previewInterval(srs, SrsRating::Again), sizeof(iv1));
    strncpy(iv2, FlashcardSrs::previewInterval(srs, SrsRating::Hard), sizeof(iv2));
    strncpy(iv3, FlashcardSrs::previewInterval(srs, SrsRating::Good), sizeof(iv3));
    strncpy(iv4, FlashcardSrs::previewInterval(srs, SrsRating::Easy), sizeof(iv4));
    iv1[15] = iv2[15] = iv3[15] = iv4[15] = '\0';

    const char* intervals_raw[] = {iv1, iv4, iv2, iv3};
    const char* ratings_raw[] = {
        tr(STR_FLASHCARD_AGAIN), tr(STR_FLASHCARD_EASY),
        tr(STR_FLASHCARD_HARD), tr(STR_FLASHCARD_GOOD)};

    const char* intervals[4];
    const char* ratings[4];
    if (origOrientation == GfxRenderer::Orientation::PortraitInverted) {
        intervals[0] = intervals_raw[3]; intervals[1] = intervals_raw[2];
        intervals[2] = intervals_raw[1]; intervals[3] = intervals_raw[0];
        ratings[0] = ratings_raw[3]; ratings[1] = ratings_raw[2];
        ratings[2] = ratings_raw[1]; ratings[3] = ratings_raw[0];
    } else {
        for (int i = 0; i < 4; i++) { intervals[i] = intervals_raw[i]; ratings[i] = ratings_raw[i]; }
    }

    for (int i = 0; i < 4; i++) {
        int x = btnPos[i];
        renderer.fillRect(x, btnY, btnWidth, btnHeight, false);
        renderer.drawRect(x, btnY, btnWidth, btnHeight);
        int tw1 = renderer.getTextWidth(SMALL_FONT_ID, intervals[i]);
        renderer.drawText(SMALL_FONT_ID, x + (btnWidth - tw1) / 2, btnY + 7, intervals[i]);
        int tw2 = renderer.getTextWidth(UI_10_FONT_ID, ratings[i]);
        renderer.drawText(UI_10_FONT_ID, x + (btnWidth - tw2) / 2, btnY + 27, ratings[i]);
    }

    renderer.setOrientation(origOrientation);

    int contentBottom = pageHeight - btnHeight - metrics.verticalSpacing;
    int contentHeight = contentBottom - contentTop;

    std::string mainText = card.frontMain();
    int mainLineHeight = renderer.getLineHeight(flashcardBodyFont());
    int textY = contentTop + contentHeight / 3;

    size_t pos = 0;
    while (pos < mainText.size()) {
        size_t nl = mainText.find('\n', pos);
        std::string line = (nl == std::string::npos)
                               ? mainText.substr(pos)
                               : mainText.substr(pos, nl - pos);
        renderer.drawCenteredText(flashcardBodyFont(), textY, line.c_str());
        textY += mainLineHeight;
        pos = (nl == std::string::npos) ? mainText.size() : nl + 1;
    }

    std::string hint = card.frontHint();
    if (!hint.empty()) {
        textY += 4;
        renderer.drawCenteredText(UI_10_FONT_ID, textY, hint.c_str());
        textY += renderer.getLineHeight(UI_10_FONT_ID);
    }

    textY += metrics.verticalSpacing;
    renderer.drawLine(metrics.contentSidePadding, textY,
                      pageWidth - metrics.contentSidePadding, textY, true);
    textY += metrics.verticalSpacing;

    renderer.drawCenteredText(UI_10_FONT_ID, textY, card.backContent.c_str());
}    for (const std::string* s : {&s1, &s2, &s3}) {
        const unsigned char* p = reinterpret_cast<const unsigned char*>(s->c_str());
        uint32_t cp;
        while ((cp = utf8NextCodepoint(&p))) {
            if (cp > 0x7F) cps.push_back(cp);  // ASCII always comes from built-in
        }
    }
    if (!cps.empty()) ext->preloadGlyphs(cps.data(), cps.size());
}

// ─── Text wrapping helpers ───────────────────────────────────────────────────
// Wrap plain text so each line fits within maxWidth pixels. Breaks at spaces
// when possible; for space-less scripts (CJK) or over-long words falls back to
// UTF-8 codepoint boundaries so multi-byte characters never get split mid-byte.

static bool isUtf8Start(unsigned char b) { return (b & 0xC0) != 0x80; }

static void wrapByCodepoint(GfxRenderer& r, int fontId, const std::string& seg,
                            int maxWidth, std::vector<std::string>& out) {
    std::string line;
    for (size_t i = 0; i < seg.size();) {
        size_t end = i + 1;
        while (end < seg.size() && !isUtf8Start((unsigned char)seg[end])) ++end;
        std::string candidate = line + seg.substr(i, end - i);
        if (!line.empty() && r.getTextWidth(fontId, candidate.c_str()) > maxWidth) {
            out.push_back(line);
            line = seg.substr(i, end - i);
        } else {
            line = std::move(candidate);
        }
        i = end;
    }
    if (!line.empty()) out.push_back(std::move(line));
}

static void wrapSegment(GfxRenderer& r, int fontId, const std::string& seg,
                        int maxWidth, std::vector<std::string>& out) {
    if (seg.empty()) { out.push_back(""); return; }
    if (r.getTextWidth(fontId, seg.c_str()) <= maxWidth) {
        out.push_back(seg);
        return;
    }
    std::string line;
    size_t i = 0;
    while (i < seg.size()) {
        size_t wend = seg.find(' ', i);
        if (wend == std::string::npos) wend = seg.size();
        std::string word = seg.substr(i, wend - i);
        std::string candidate = line.empty() ? word : line + " " + word;
        if (r.getTextWidth(fontId, candidate.c_str()) <= maxWidth) {
            line = std::move(candidate);
        } else {
            if (!line.empty()) { out.push_back(std::move(line)); line.clear(); }
            if (r.getTextWidth(fontId, word.c_str()) > maxWidth) {
                wrapByCodepoint(r, fontId, word, maxWidth, out);
            } else {
                line = std::move(word);
            }
        }
        i = (wend < seg.size()) ? wend + 1 : wend;
    }
    if (!line.empty()) out.push_back(std::move(line));
}

static std::vector<std::string> wrapText(GfxRenderer& r, int fontId,
                                         const std::string& text, int maxWidth) {
    std::vector<std::string> lines;
    size_t i = 0;
    while (i <= text.size()) {
        size_t nl = text.find('\n', i);
        if (nl == std::string::npos) nl = text.size();
        wrapSegment(r, fontId, text.substr(i, nl - i), maxWidth, lines);
        if (nl == text.size()) break;
        i = nl + 1;
    }
    return lines;
}

// Pick the largest main-text font whose wrapped line count fits within availH.
// Falls through to the smallest option if none fit.
static int pickMainFont(GfxRenderer& r, const std::string& text,
                            int maxWidth, int availH,
                            std::vector<std::string>& outLines) {
    const int candidates[] = {NOTOSERIF_18_FONT_ID, NOTOSERIF_16_FONT_ID, NOTOSERIF_14_FONT_ID};
    for (int f : candidates) {
        auto lines = wrapText(r, f, text, maxWidth);
        int needed = r.getLineHeight(f) * (int)lines.size();
        if (needed <= availH) { outLines = std::move(lines); return f; }
    }
    outLines = wrapText(r, NOTOSERIF_14_FONT_ID, text, maxWidth);
    return NOTOSERIF_14_FONT_ID;
}

// ─── Constructor ─────────────────────────────────────────────────────────────

FlashcardReviewActivity::FlashcardReviewActivity(GfxRenderer& renderer,
                                                 MappedInputManager& mappedInput,
                                                 const std::string& deckPath)
    : Activity("FlashcardReview", renderer, mappedInput), deckPath(deckPath) {}

// ─── Lifecycle ────────────────────────────────────────────────────────────────

void FlashcardReviewActivity::onEnter() {
    Activity::onEnter();
    today = FlashcardSrs::getToday();
    deck.loadFromCsv(deckPath.c_str());
    reviewQueue = deck.buildReviewQueue(today,
                                        PET_SETTINGS.flashcardNewPerDay,
                                        PET_SETTINGS.flashcardMaxReviewPerDay);
    currentQueueIndex = 0;
    cardState = CardState::Front;
    saveCounter = 0;

    if (reviewQueue.empty()) {
        startActivityForResult(
            std::make_unique<FlashcardDoneActivity>(renderer, mappedInput),
            [this](const ActivityResult&) { finish(); });
        return;
    }
    maxQueueSize = reviewQueue.size() * 2;
    requestUpdate();
}

// ─── Input loop ───────────────────────────────────────────────────────────────

void FlashcardReviewActivity::loop() {
    // Flush deferred deck save when no render is pending; keeps the SD bus
    // free while the render task is drawing (prevents glyph-read contention).
    if (pendingSave) {
        deck.saveToCsv(deckPath.c_str());
        pendingSave = false;
    }

    if (reviewQueue.empty() || currentQueueIndex >= reviewQueue.size()) return;

    if (cardState == CardState::Front) {
        if (mappedInput.wasReleased(MappedInputManager::Button::Back)) {
            deck.saveToCsv(deckPath.c_str());
            finish();
            return;
        }
        if (mappedInput.wasReleased(MappedInputManager::Button::Confirm)) {
            flipCard();
        }
    } else {
        // Back state — 4 buttons map to 4 SRS ratings
        // Back→Again, Left/Up→Hard, Right/Down→Good, Confirm→Easy
        if (mappedInput.wasReleased(MappedInputManager::Button::Back)) {
            rateCard(SrsRating::Again);
        } else if (mappedInput.wasReleased(MappedInputManager::Button::Left) ||
                   mappedInput.wasReleased(MappedInputManager::Button::Up)) {
            rateCard(SrsRating::Hard);
        } else if (mappedInput.wasReleased(MappedInputManager::Button::Right) ||
                   mappedInput.wasReleased(MappedInputManager::Button::Down)) {
            rateCard(SrsRating::Good);
        } else if (mappedInput.wasReleased(MappedInputManager::Button::Confirm)) {
            rateCard(SrsRating::Easy);
        }
    }
}

// ─── Card state transitions ───────────────────────────────────────────────────

void FlashcardReviewActivity::flipCard() {
    cardState = CardState::Back;
    requestUpdate();
}

void FlashcardReviewActivity::rateCard(SrsRating rating) {
    size_t cardIdx = reviewQueue[currentQueueIndex];
    auto& card = deck.getCards()[cardIdx];
    SrsState newState = FlashcardSrs::review(card.srs, rating, today);
    deck.updateCard(cardIdx, newState);

    if (rating == SrsRating::Again && reviewQueue.size() < maxQueueSize) {
        reviewQueue.push_back(cardIdx);  // re-queue failed card at end
    }

    currentQueueIndex++;
    saveCounter++;

    if (saveCounter >= 5) {
        pendingSave = true;  // flushed by loop() after next render completes
        saveCounter = 0;
    }

    if (currentQueueIndex >= reviewQueue.size()) {
        deck.saveToCsv(deckPath.c_str());  // final save — no further render
        pendingSave = false;
        // startActivityForResult so when Done finishes we pop Review too —
        // otherwise Review is stranded on the stack with no active input
        // handler (loop() early-returns on exhausted queue) and the device
        // appears hung.
        startActivityForResult(
            std::make_unique<FlashcardDoneActivity>(renderer, mappedInput),
            [this](const ActivityResult&) { finish(); });
    } else {
        cardState = CardState::Front;
        requestUpdate();
    }
}

// ─── Render ───────────────────────────────────────────────────────────────────

void FlashcardReviewActivity::render(RenderLock&&) {
    if (reviewQueue.empty() || currentQueueIndex >= reviewQueue.size()) return;

    const auto& card = deck.getCards()[reviewQueue[currentQueueIndex]];

    // Warm the external-font cache with this card's glyphs up-front; batched
    // sequential SD reads are ~10x faster than interleaving with drawText.
    preloadCardGlyphs(card.frontMain(), card.frontHint(), card.backContent);

    renderer.clearScreen();

    const auto& metrics = UITheme::getInstance().getMetrics();
    auto pageWidth = renderer.getScreenWidth();

    GUI.drawHeader(renderer,
                   Rect{0, metrics.topPadding, pageWidth, metrics.headerHeight},
                   deck.getName().c_str());

    if (cardState == CardState::Front) {
        renderFront(card);
    } else {
        renderBack(card);
    }

    renderer.displayBuffer();
}

// ─── renderFront ──────────────────────────────────────────────────────────────

void FlashcardReviewActivity::renderFront(const FlashcardCard& card) {
    const auto& metrics = UITheme::getInstance().getMetrics();
    auto pageWidth = renderer.getScreenWidth();
    auto pageHeight = renderer.getScreenHeight();
    int contentTop = metrics.topPadding + metrics.headerHeight + metrics.verticalSpacing;
    int contentBottom = pageHeight - metrics.buttonHintsHeight - metrics.verticalSpacing;
    int contentHeight = contentBottom - contentTop;
    const int contentWidth = pageWidth - metrics.contentSidePadding * 2;

    std::string mainText = card.frontMain();
    std::string hint = card.frontHint();
    int hintReserve = hint.empty() ? 0 : (renderer.getLineHeight(UI_10_FONT_ID) + metrics.verticalSpacing);

    std::vector<std::string> mainLines;
    int mainFont = pickMainFont(renderer, mainText, contentWidth,
                                    contentHeight - hintReserve, mainLines);
    int mainLineHeight = renderer.getLineHeight(mainFont);
    int blockH = mainLineHeight * (int)mainLines.size();

    // Center the main-text block vertically in (contentTop..contentBottom - hint)
    int textY = contentTop + ((contentHeight - hintReserve) - blockH) / 2;
    if (textY < contentTop) textY = contentTop;
    for (const auto& line : mainLines) {
        renderer.drawCenteredText(mainFont, textY, line.c_str());
        textY += mainLineHeight;
    }

    if (!hint.empty()) {
        textY += metrics.verticalSpacing;
        auto hintLines = wrapText(renderer, UI_10_FONT_ID, hint, contentWidth);
        for (const auto& line : hintLines) {
            renderer.drawCenteredText(UI_10_FONT_ID, textY, line.c_str());
            textY += renderer.getLineHeight(UI_10_FONT_ID);
        }
    }

    const auto labels = mappedInput.mapLabels(tr(STR_BACK), tr(STR_FLASHCARD_SHOW), "", "");
    GUI.drawButtonHints(renderer, labels.btn1, labels.btn2, labels.btn3, labels.btn4);
}

// ─── renderBack ───────────────────────────────────────────────────────────────

void FlashcardReviewActivity::renderBack(const FlashcardCard& card) {
    const auto& metrics = UITheme::getInstance().getMetrics();
    auto pageWidth = renderer.getScreenWidth();
    auto pageHeight = renderer.getScreenHeight();
    int contentTop = metrics.topPadding + metrics.headerHeight + metrics.verticalSpacing;

    // SRS labels (interval + rating) via system drawButtonHints.
    // Physical mapping: Back→Again, Confirm→Easy, Previous→Hard, Next→Good
    const auto& srs = card.srs;
    char lbl1[24], lbl2[24], lbl3[24], lbl4[24];
    snprintf(lbl1, sizeof(lbl1), "%s %s", tr(STR_FLASHCARD_AGAIN),
             FlashcardSrs::previewInterval(srs, SrsRating::Again));
    snprintf(lbl2, sizeof(lbl2), "%s %s", tr(STR_FLASHCARD_EASY),
             FlashcardSrs::previewInterval(srs, SrsRating::Easy));
    snprintf(lbl3, sizeof(lbl3), "%s %s", tr(STR_FLASHCARD_HARD),
             FlashcardSrs::previewInterval(srs, SrsRating::Hard));
    snprintf(lbl4, sizeof(lbl4), "%s %s", tr(STR_FLASHCARD_GOOD),
             FlashcardSrs::previewInterval(srs, SrsRating::Good));
    const auto labels = mappedInput.mapLabels(lbl1, lbl2, lbl3, lbl4);
    GUI.drawButtonHints(renderer, labels.btn1, labels.btn2, labels.btn3, labels.btn4);

    // --- Content area: front text + hint + separator + answer ---
    int contentBottom = pageHeight - metrics.buttonHintsHeight - metrics.verticalSpacing;
    int contentHeight = contentBottom - contentTop;
    const int contentWidth = pageWidth - metrics.contentSidePadding * 2;

    // Budget the content area: reserve ~40% for front text, rest for hint/sep/back
    std::string mainText = card.frontMain();
    std::string hint = card.frontHint();
    int hintReserve = hint.empty() ? 0 : renderer.getLineHeight(UI_10_FONT_ID);
    int mainBudget = std::max(60, (contentHeight - hintReserve) * 2 / 5);

    std::vector<std::string> mainLines;
    int mainFont = pickMainFont(renderer, mainText, contentWidth, mainBudget, mainLines);
    int mainLineHeight = renderer.getLineHeight(mainFont);

    int textY = contentTop;
    for (const auto& line : mainLines) {
        renderer.drawCenteredText(mainFont, textY, line.c_str());
        textY += mainLineHeight;
    }

    if (!hint.empty()) {
        textY += 4;
        auto hintLines = wrapText(renderer, UI_10_FONT_ID, hint, contentWidth);
        for (const auto& line : hintLines) {
            renderer.drawCenteredText(UI_10_FONT_ID, textY, line.c_str());
            textY += renderer.getLineHeight(UI_10_FONT_ID);
        }
    }

    // Separator line
    textY += metrics.verticalSpacing;
    renderer.drawLine(metrics.contentSidePadding, textY,
                      pageWidth - metrics.contentSidePadding, textY, true);
    textY += metrics.verticalSpacing;

    // Back content (answer) — wrapped, may use smaller font if needed
    int backBudget = contentBottom - textY;
    std::vector<std::string> backLines;
    int backFont = pickMainFont(renderer, card.backContent, contentWidth, backBudget, backLines);
    int backLineHeight = renderer.getLineHeight(backFont);
    for (const auto& line : backLines) {
        if (textY + backLineHeight > contentBottom) break;
        renderer.drawCenteredText(backFont, textY, line.c_str());
        textY += backLineHeight;
    }
}
