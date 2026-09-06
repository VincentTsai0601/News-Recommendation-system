# Reading access: development verification

Checked 2026-09-06 on local development preview at localhost:8502.

- Primary article control uses Streamlit link_button; removed the custom _top link.
- Clicking an article opened a new browser tab and displayed the BBC publisher page.
  Observed article identifier: cly4e0wn452o (Booking.com listing report).
- Expanding the fallback displayed the complete article URL, including its query
  string. A separate offline UI test verifies URL characters are preserved.
- All 45 automated tests passed. These tests are not real-phone evidence.

## Before release

Deploy the development branch to a separate preview. On an actual Android phone,
open that preview in Chrome, choose an article, tap its primary link, and check
that the expected publisher page loads while the briefing remains available.
Repeat from LINE's embedded browser. If blocked, verify the copy control and
paste the URL into Chrome. Record phone model, Android/Chrome/LINE versions,
preview commit, article URL, timestamp, and observed result. Do not replace these
checks with desktop viewport emulation.

The user's prior production rollback remains in effect; no production merge or
deployment was made. Publisher access restrictions remain outside this app.

## Learning point

A test of HTML attributes cannot establish browser navigation. Use unit tests for
URL preservation, an actual browser click for navigation, and the affected device
for platform compatibility. Keep each claim within the scope of its evidence.
