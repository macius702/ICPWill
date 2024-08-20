
## Digital Will

This project aims to create a digital will, allowing for the scheduled release of funds and testament orders.



### Features
- **Inheritable Assets:** These can be anything from a secret piece of text, an action of asset transfer, granting access to an asset, transfer of identity.
- **Funds transfer on steroids.**
  - Transfer can be:
    - immediate
    - after some time
    - exact date
    - periodic  / scheduled
    - after some event like:
      - api call
      - absence of api call(s) = inactivity (DEATH?)
    - send the whole sum to 
      - one beneficiary
      - beneficiaries separately
      - the sum can be 
        - fixed amount denominated 
          - in crypto
          - in fiat
        - percent 
    - integrated into NNS
    - Associated Message: This can be a will and can be encrypted. Decryption is available after schedule or auto-decryption.
- **Digital assets:**
    - ICP coins
    - ICP hosted tokens
    - BTC
    - ETH
    - ETH/Solana tokens
    - NFTs
    - Fiat converted from crypto
    - Stocks
    - Real estate
    - Fiat


- **Proof of Life:** The system sends reminders to execute the `i_am_alive` function or checks if there has been any activity on a certain identity.

- **Monetization Options**: The fee needs to cover the cycles for this smart contract, including e.g BTC fees
    - when setting up the testament 
    - at the time of payout to the beneficiaries.
- **The testator options:**
    - The will can be made visible in a register of wills.
    - Can reveal information about pending assets to:
        - Beneficiaries
        - Everyone
        - Nobody
    - Jurisdiction: The will can specify where, when, and under what jurisdiction it was written. Alternatively, it can be kept secret.

- **Beneficiary Controller:** A person (a lawyer, a DAO) can be made the controller of the canister with assets or information.






