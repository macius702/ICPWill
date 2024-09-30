
Research:
  - Prague 2024 hackathon - see the (fiat) exchange combo.
  - Protocol with a beneficiary (during execution): Check if it is ready/alive (e.g., send a small amount of tokens with a message - "please send something back". If successful, send the remaining sum).
  - License.
  - Print `get_transactions`: `(GetTransactionsRequest) -> (GetTransactionsResponse)` query; after approval, transfer - after everything that returns `BlockIndex`.
    - // mtlk todo
    - The following method is marked as 'update' because it internally performs an inter-canister call.
    - Consider performing the balance retrieval from the frontend?
    - `"get_balance" : () -> (ResultNat);`
  - Consider all as a plugin into a larger app (a wallet?).
  - Perhaps a wallet can be connectable. Can it give delegation?
  - How costly are the timers?
  - Debuggable frontend and backend.
  - Who pays for transaction and approval fees - inheritors? - To decide. Option.
  - Notifications - websocket?
  - How to handle roles: the beneficiary should not immediately become the testator 😃.
  - Frontend: Button register as default (pressing Enter).

Features:
  - Show account-id in GUI, next to the Principal.
  - Refreshing.
  - Polling - ok. Only update buttons if the timer is gone. Eventually, check the transfer info obtained as the beneficiary (balance).
  - Send - message - notification on the recipient's side.
  - Toast or snack when timer execution is successful or not.
  - Frontend - react to all data (beneficiaries) after `getUser`.
  - Canceling timers, reinstantiating - may fail - handle it and test.
  - Frontend - show version.
  - Frontend - e8 precision.
  - Frontend - show principal along with nickname in the select beneficiary dropdown list box.
  - Frontend - display information about the remaining time and execution date.
  - Frontend - show token balance (asterisk*** mode).
  - Send an invite to the app to be a beneficiary or testator.
  - Dockerfile with versions, Dockerfile - print current versions - insert them into Dockerfile.
  - Is the beneficiary ready? - small amounts protocol.
  - Bitcoin.
  - Back to branch main.
  - Upgrades of canister - hook - use hooks for upgrade first.

Tests:
  - e2e:
    - A test for `after_inactivity`.
    - A test for `inactivity_period`.
    - A test for the timer.
  - Unit.
  - System.

Defects:
  - `identityToUse` - not needed.
  - Why is the beneficiary ICP count not displayed after refresh?
  - Frontend - not finding back when the same user is selected.
  - Dockerfile - `nvm` what for?
  - In the `sleepy` test. `Timy`. Refactor to have more descriptive functions. For each window, include an object with a nickname and how much money it should allocate instead of vectors [0.1400,1500]. Remove debugging `savepage`.
  - How to name the identity that is giving money for nothing (instead of Alice).

DONE:
  - DRY `setUserData`.
  - Perhaps not polling. Use a one-shot timer in the GUI?
  - Update balance as well.
  - Run the test on the real system.
  - React bug - move (before `inactivity_period`):
    - `await announceActivity(identity)`.
    - `await getUserData()`.
    - `await getAllUsers()`.
  - Use effect `[principal]`.
  - `git stash save cleanup_inactivity_period done`, switch to fixes, and do it.
  - After inactivity: Condition on `x` of inactivity.
  - Frontend - grey save, show Cancel.
  - Test - Selenium, create 3 II.
  - Logged in as: display principal and nickname.
  - Save log session.
  - Send - message.
  - `nvm` use 20 for `build.sh`.
  - Send - token.
  - Send token delayed.
  - Block funds for the transaction.
  - Batch transaction.
  - Send to an external address.
  - Bug with balance.
  - Connect cancel action.
  - Selenium - //TODO(mtlk) - a more sophisticated wait here.