Research:
  Prague 2024 hackaton - see the (fiat) echange combo
  protocol with a beneficiary (while execution )if it is ready/alive (e.g send small amount of tokens with a message - please send something back. When succeededs sent the rest sum)
  license
  print  get_transactions : (GetTransactionsRequest) -> (GetTransactionsResponse) query; after approve, trransfer - after everything that returns BlockIndex
    // mtlk todo
    // The following method is marked as 'update' because it internally performs an inter-canister call.
    // Consider performing the balance retrieval from the frontend?
    "get_balance" : () -> (ResultNat);
  consider all as a plugin into larger app (a wallet ?)
  Perhaps a wallet can be connectable. Can give delegation ?
  How costly are the timers 
  Debuggable frontend and backend
  Who pays for transaction and approval fees - inheritors? - to decide . Option
  Notyfikacje - websocket?
  Jak rozwiązać sprawę ról. Ze beneficiray nie powinien od razu być testatorem 😃
  Frontend Button register as default (pressing Enter)

Features:
  show account-id in GUI, next to the Principal
  refreshing
  Polling - ok . Only update buttons if timer gone. Eventually check the info of transfer got as beneficiary( balance)
  Send - messgae - notofican on recipients side
  toast or snack when timer execution successfull or not
  Frontend - react to all data (beneficiaries) after getUser
  Canelling timers, reinstantiating - may fail - handle it and test
  Frontend - show version
  Frontend - e8 precision
  Frontend show principal along with nickname is select beneficiary drop down list box
  Frontend Display .Info ile czasu zostalo i data exekucji
  Frontend Show token balance (asterisk*** mode)
  Send invite to app to be a beneficiary or testator
  Dockerfile with versions, Dockerfile - print current versions - insert them into Dockerfile
  Is beneficiary ready - small amounts protocol
  Bitcoin
  back to branch main
  Upgrades of canister - hook - jpierw hooki do upgrade


Tests:
  e2e:
    A test for after_inactivity, test for inactivity_period
    A test for timer
  unit
  system

Defects:
  identityToUse - not needed
  Why beneficiary icp count is not displayed after refesh ?
  Frontend - not folnding bak when this same user selected
  Dockerfile - nvm what for ?
  W tescie sleepy. Timy. I refactor zeby bardziej opisowe funckcje. Do kazdego okna ibiekt z nickiem i tym ile ma kasy szidziczyc zamiast vectorów [0.1400,1500] Debugi savepage wywal
  How to name identity that is giving money for nothing (instead of Alice)





DONE DRY setuserdata
DONE Perhaps not polling. But one shot timer in gui ?
DONE Update balance as well
DONE Uruchom test na realu
DONE reac t bug - move (before inactivity_period
    await announceActivity(identity)
    await getUserData()
    await getAllUsers()
DONE to use effect [proncipat]
DONE git stash save cleanup_inactivity_period done , switch to fixes and do it
DONE After inactivity Condition on x of inactivity
DONE Frontend - grey save show Cancel
DONE Test - selenium create 3 II
DONE Loged in as display proncipal. Nick
DONE Save log session
DONE Send - messgae
DONE Nvm use 20 do build.sh
DONE Send - token
DONE Send token delayed
DONE Zablokuj środki pod transakcję
DONE Batch transaction
DONE Wysyłanie na zewnetrzny adres
DONE Bug z balancem
DONE Connect cancel action
DONE Selenium - //TODO(mtlk) - amore sophisticated wait here
