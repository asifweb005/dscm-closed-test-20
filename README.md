# DSCM Closed Test 20 - 5 Hours (No AI)

Separate repo for Google closed testing, no AI, no API key.

Fixed - never change code to run:
- 20 emulators in parallel (API 29-34, Pixel / Nexus)
- Run time: 5 hours fixed (300 minutes, check every 10 minutes)
- Package: com.paradox.dscm (fixed)
- Flow: install APK -> launch -> Continue as guest -> type name -> Start playing -> Decline notifications -> open a game -> stay alive 5 hours, screenshot every 10 min, relaunch if app dies

To run:
1. Actions tab -> "Closed Test 20 - 5 Hours" -> Run workflow
2. Paste only the direct APK download URL
3. Run

That is the only input. Everything else is fixed in this repo.
Old repo dscm-android-test is untouched.
