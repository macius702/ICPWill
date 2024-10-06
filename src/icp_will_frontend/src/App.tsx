import React, { useState, useEffect } from 'react'
import { AuthClient } from '@dfinity/auth-client'
import { Actor, HttpAgent, Identity } from '@dfinity/agent'
import { Principal } from '@dfinity/principal'
import { icp_will_backend, canisterId, createActor } from '../../declarations/icp_will_backend'
import { idlFactory as icrc1_ledger_canister_Idl } from '../../declarations/icrc1_ledger_canister'
import { Tokens } from '../../declarations/icrc1_ledger_canister/icrc1_ledger_canister.did';

import type {
  TransferArgs,
  ResponseUserData,
  BatchTransfer
} from '../../declarations/icp_will_backend/icp_will_backend.did'
import { Button } from './components/ui/button'
import { Textarea } from './components/ui/textarea'
import { Label } from './components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './components/ui/select'
import { Input } from './components/ui/input'
import { Card } from './components/ui/card'
import Layout from './components/ui/layout'
import { Checkbox } from './components/ui/checkbox'
import { CheckedState } from '@radix-ui/react-checkbox'

import { createAgent } from "@dfinity/utils";
import { SaveIcon } from 'lucide-react'
import { getAccountId } from "./accountUtils"

interface IBeneficiary {
  nickname: string
  icpAmount: bigint
  userPrincipal: Principal
}

enum TimerStatus {
  Active = 'active',
  Inactive = 'inactive',
  CannotTell = 'cannot_tell'
}

const customLog = (message: any, ...optionalParams: any[]) => {
  //console.log(`[Custom Log]:`, message, ...optionalParams);
};




const IDENTITY_PROVIDER = import.meta.env.VITE_IDENTITY_PROVIDER
const AGENT_HOST = import.meta.env.VITE_AGENT_HOST
const LEDGER_CANISTER_ID = import.meta.env.VITE_LEDGER_CANISTER_ID
const NETWORK = import.meta.env.VITE_NETWORK

const App: React.FC = () => {
  const [newChat, setNewChat] = useState<string>('')
  const [chats, setChats] = useState<string[][]>([])
  const [identity, setIdentity] = useState<Identity | undefined>()
  const [principal, setPrincipal] = useState<Principal | undefined>()
  const [targetPrincipal, setTargetPrincipal] = useState<string>('')
  const [userData, setUserData] = useState<ResponseUserData | undefined>()
  const [newUsername, setNewUsername] = useState<string>('')
  const [allUsers, setAllUsers] = useState<[Principal, ResponseUserData][]>([])
  const [balance, setBalance] = useState<BigInt | null>(null)
  const [amountToSend, setAmountToSend] = useState<number>(0)
  const [transferDelay, setTransferDelay] = useState<number>(0)
  const [beneficiaries, setBeneficiaries] = useState<IBeneficiary[]>([])
  const [executionAfterYears, setExecutionAfterYears] = useState<number>(0)
  const [executionAfterMonths, setExecutionAfterMonths] = useState<number>(0)
  const [executionAfterSeconds, setExecutionAfterSeconds] = useState<number>(0)
  const [showChat, setShowChat] = useState<CheckedState>(false)
  const [showDirectTransfer, setShowDirectTransfer] = useState<CheckedState>(false)
  const [overrideTarget, setOverrideTarget] = useState(false);
  const [overridePrincipal, setOverridePrincipal] = useState('');
  const [inactivityChecked, setInactivityChecked] = useState(true);
  const [loading, setLoading] = useState(false);
  const [BITCOIN, setBITCOIN] = useState(true);
  const [btcAddress, setBtcAddress] = useState<string | null>(null);




  const isBeneficiaryValid =
    targetPrincipal &&
    targetPrincipal !== principal?.toText() &&
    targetPrincipal !== 'Please select one'
  const isSaveAndActivateEnabled =
    beneficiaries.length > 0 &&
    (executionAfterYears > 0 || executionAfterMonths > 0 || executionAfterSeconds > 0) &&
    !(userData && userData.has_active_timer)


  const isUserLogged = (a_identity?: Identity) => {
    const identityToUse = a_identity || identity;
    const principalToUse = a_identity ? a_identity.getPrincipal() : principal;

    if (!identityToUse || !principalToUse || principalToUse.isAnonymous()) {
      throw new Error('PLZ log in');
    }

    return { identity: identityToUse, principal: principalToUse };
  }

  const validateTargetPrincipal = () => {
    const cleanTargetPrincipal = targetPrincipal.trim()
    if (cleanTargetPrincipal === '') {
      throw new Error('No principal')
    }
    const target = Principal.fromText(cleanTargetPrincipal)
    if (!target || target.isAnonymous()) {
      throw new Error('Wrong target')
    }
    return target
  }

  const getAuthClient = (a_identity?: Identity) => {
    const identityToUse = a_identity || identity;
    isUserLogged(identityToUse);

    return createActor(canisterId, {
      agentOptions: {
        identity: identityToUse,
      },
    });
  }

  const dodajChatMSG = async () => {
    const target = validateTargetPrincipal()
    const backend = getAuthClient()
    await backend.add_chat_msg(newChat, target)
    await pobierzChaty()
  }

  const pobierzChaty = async () => {
    const { identity, principal } = isUserLogged()
    const target = validateTargetPrincipal()
    const chatPath = [target, principal].sort()
    const fetchedChats = await icp_will_backend.get_chat(chatPath)
    setChats(fetchedChats)
  }

  const registerUsername = async () => {
    const trimedUsername = newUsername.trim()
    const backend = getAuthClient()
    await backend.register(trimedUsername)
    await getUserData()
    await getAllUsers()
  }

  const getUserData = async () => {
    setLoading(true);
    const { principal } = isUserLogged();
    const maybeUserData = await icp_will_backend.get_user(principal);
    const userData = maybeUserData.length === 0 ? undefined : maybeUserData[0];

    setUserData(userData);

    if (userData && userData.batch_transfer.length > 0) {
      updateUIwithBatchTransferData(userData)
    } else {
      customLog('No batch transfer available');
    }

    await fetchBalance();
    setLoading(false);
  };


  const getUserHasActiveTimer = async (): Promise<TimerStatus> => {
    customLog('Entering getUserHasActiveTimer')
    const { principal } = isUserLogged();
    customLog('getUserHasActiveTimer principal: ', principal)

    const maybeUserData = await icp_will_backend.get_user(principal);
    customLog('getUserHasActiveTimer maybeUserData: ', maybeUserData)

    const userData = maybeUserData.length === 0 ? undefined : maybeUserData[0];
    customLog('getUserHasActiveTimer userData: ', userData)

    if (userData) {
      customLog('getUserHasActiveTimer if(userData)')
      if (userData.has_active_timer)
        return TimerStatus.Active
      else
        return TimerStatus.Inactive
    }
    else {
      customLog('getUserHasActiveTimer else')
      return TimerStatus.CannotTell
    }
  };


  const getAllUsers = async () => {
    const users = await icp_will_backend.get_users()
    setAllUsers(users)
  }


  const transfer = async () => {
    try {
      if (!identity) throw new Error('Identity is undefined');

      const backend = getAuthClient();
      customLog('backend', backend);

      const target = overrideTarget ? Principal.fromText(overridePrincipal) : validateTargetPrincipal();
      customLog('target', target);

      const { principal } = isUserLogged();
      if (!principal) throw new Error('Principal is undefined');
      customLog('principal', principal);

      const agent = await createAgentWithHost(identity);
      const myledger = createLedgerActor(agent);

      async function getBalance(label: string) {
        await Promise.all(
          allUsers.map(async ([userPrincipal, userData]) => {
            const balance = await myledger.icrc1_balance_of({ owner: userPrincipal, subaccount: [] });
            customLog(label, userData.nickname, balance, userPrincipal.toText());
          })
        );
      }

      await getBalance('balance_before');

      const theSpender = Principal.fromText(canisterId);
      customLog('Spender: ', theSpender.toText());

      const feeFromLedger = await myledger.icrc1_fee() as Tokens;// TODO(mtlk) why Tokens not imported automatically

      const approveResult = await myledger.icrc2_approve({
        fee: [],
        memo: [],
        from_subaccount: [],
        created_at_time: [],
        amount: BigInt(amountToSend) + feeFromLedger,
        expected_allowance: [],
        expires_at: [],
        spender: { owner: theSpender, subaccount: [] },
      });

      customLog('approve_result', approveResult);

      const allowanceResult = await myledger.icrc2_allowance({
        account: { owner: principal, subaccount: [] },
        spender: { owner: theSpender, subaccount: [] },
      });

      customLog('allowance_result', allowanceResult);

      const transferArgs: TransferArgs = {
        to_account: { owner: target, subaccount: [] },
        amount: BigInt(amountToSend),
        delay_in_seconds: BigInt(transferDelay),
        from_account: { owner: principal, subaccount: [] },
      };

      const result = await backend.transfer(transferArgs);
      await getBalance('balance_after');
      customLog(result);

    } catch (error) {
      if (error instanceof Error) {
        console.error('Error during transfer:', error.message);
      } else {
        console.error('Unknown error during transfer:', error);
      }
    }
  }

  const logout = async () => {
    const authClient = await AuthClient.create()
    await authClient.logout()
    setIdentity(undefined)
    setPrincipal(undefined)
    setChats([])
    setUserData(undefined)
    localStorage.clear()
  }

  const login = async () => {
    customLog('In frontent login->')
    const authClient = await AuthClient.create()
    customLog('In frontent login-> authClient: ', authClient)
    await authClient.login({
      identityProvider: IDENTITY_PROVIDER,
      onSuccess: async () => {
        customLog('In frontent login on success authClient: ', authClient)
        await handleAuthentication(authClient)
      },
    })
  }

  const addBeneficiary = () => {
    if (isBeneficiaryValid) {
      const selectedUser = allUsers.find(
        ([userPrincipal]) => userPrincipal.toText() === targetPrincipal
      )
      if (selectedUser) {
        setBeneficiaries([
          ...beneficiaries,
          {
            nickname: selectedUser[1].nickname,
            icpAmount: BigInt(0),
            userPrincipal: selectedUser[0],
          },
        ])
      }
    }
  }

  const removeBeneficiary = (index: number) => {
    setBeneficiaries(beneficiaries.filter((_, i) => i !== index))
  }

  const clearBeneficiaries = async () => {
    const payload = {
      beneficiaries: [],
      execution_delay_seconds: BigInt(0),
      of_inactivity: true,
    };
    customLog('clearBeneficiaries triggered with payload:', payload);
    const backend = getAuthClient();
    await backend.register_batch_transfer(payload);
  }


  const setupAllowancesForBatchTransfer = async () => {
    try {
      if (!principal || !identity) throw new Error('Principal or Identity is undefined');

      const agent = await createAgentWithHost(identity);
      const myledger = createLedgerActor(agent);

      const feeFromLedger = await myledger.icrc1_fee() as Tokens;
      const overallTransactionCost = feeFromLedger * BigInt(beneficiaries.length) + feeFromLedger;

      const assetsSum = beneficiaries.reduce((sum: bigint, { icpAmount }) => sum + icpAmount, BigInt(0));
      const overallSum = BigInt(assetsSum) + overallTransactionCost;

      const theSpender = Principal.fromText(canisterId);
      customLog('Spender: ', theSpender.toText());

      const approveResult = await myledger.icrc2_approve({
        fee: [],

        memo: [],

        from_subaccount: [],
        created_at_time: [],
        amount: overallSum,
        expected_allowance: [],
        expires_at: [],
        spender: { owner: theSpender, subaccount: [] },
      });

      customLog('batch_approve_result', approveResult);

    } catch (error) {
      if (error instanceof Error) {
        console.error('Error during transfer:', error.message);
      } else {
        console.error('Unknown error during transfer:', error);
      }
    }
  };


  const saveAndActivate = async () => {
    if (isSaveAndActivateEnabled) {


      // 
      customLog('saveAndActivate userData: ', userData)
      if (userData) {
        customLog('saveAndActivate userData: ', userData)
        setUserData(prevData => {
          customLog('saveAndActivate prevData =>', prevData)
          if (!prevData) {
            // If prevData is undefined, return it or handle accordingly
            return prevData;
          }

          customLog('saveAndActivate After prevData =>')

          // Prepare the new object
          const updatedData = {
            nickname: prevData.nickname,
            avatar_url: prevData.avatar_url,
            batch_transfer: prevData.batch_transfer,
            has_active_timer: true,
          };


          // Log the new object being returned
          customLog('Returning updated data:', updatedData);
          return updatedData;
        });
      }
      else {
        customLog('saveAndActivate no userData')
      }


      customLog('Save and Activate triggered');
      const executionTimeInSeconds = BigInt(executionAfterYears * 31536000 + executionAfterMonths * 2592000 + executionAfterSeconds);
      customLog('this.benefficiaries', beneficiaries);
      const payload = {
        beneficiaries: beneficiaries.map(b => ({
          beneficiary_principal: b.userPrincipal,
          nickname: b.nickname ? b.nickname : "",
          assets: BITCOIN ? [{
            ticker: 'BTC',
            amount: BigInt(b.icpAmount),     //TODO(mtlk) - amount is more general, not only for ICP
        }] : [],
        amount_icp: BigInt(b.icpAmount),
          // 
        })),
        execution_delay_seconds: executionTimeInSeconds,
        of_inactivity: inactivityChecked,
      };
      customLog('Save and Activate triggered with payload:', payload);
      const backend = getAuthClient();
      await backend.register_batch_transfer(payload);
      customLog('After Save and Activate triggered with payload:', payload);

      setupAllowancesForBatchTransfer()

      await backend.execute_batch_transfers();


    }
  }

  const handleAuthentication = async (authClient: AuthClient) => {
    const identity = authClient.getIdentity()
    customLog('In handleAuthentication , identity: ', identity)
    const principal = identity.getPrincipal()
    customLog('In handleAuthentication , principal: ', principal)
    setPrincipal(principal)
    setIdentity(identity)

    customLog('Zalogowano', principal)
    await announceActivity(identity)
  }

  const announceActivity = async (identity: Identity) => {
    //  customLog('In frontend announceActivity')
    //  customLog('In frontend announceActivity before isUserLogged()')
    // const { principal } = isUserLogged()
    customLog('In frontend announceActivity after isUserLogged()')
    const backend = getAuthClient(identity)
    customLog('In frontend announceActivity backend:}', backend)
    customLog('In frontend announceActivity Before await backend.announce_activity()')
    await backend.announce_activity()
    customLog('In frontend announceActivity After await backend.announce_activity()')
  }

  const fetchBalance = async () => {
    const { principal } = isUserLogged()
    const backend = getAuthClient()
    console.log('fetching balance')
    if(BITCOIN)
    {
      if(btcAddress)
      {
        let result = await backend.btc_get_balance(btcAddress)
        setBalance(result)
        return
      }
    }
    else
    {
      let result = await backend.get_balance()
        if ('Ok' in result) {
          setBalance(result.Ok)
          return
        }
    }
    setBalance(null)
  }


  const cancelTimer = async () => {
    customLog('in cancelTimer')
    const backend = getAuthClient()
    customLog('in cancelTimer backend: ', backend)

    let result = await backend.cancel_batch_activation()
    customLog('in cancelTimer result ', result)


  }

  // Helper function to create an agent
  async function createAgentWithHost(identity: Identity) {
    const fetchRootKey = NETWORK !== '--ic';
    customLog('fetchRootKey: ', fetchRootKey)
    return await createAgent({
      identity,
      host: AGENT_HOST,
      fetchRootKey: fetchRootKey,
    });
  }

  // Helper function to create an actor
  function createLedgerActor(agent: HttpAgent) {
    return Actor.createActor(icrc1_ledger_canister_Idl, {
      agent,
      canisterId: Principal.fromText(LEDGER_CANISTER_ID),
    });
  }

  // Helper for getUserData
  function updateUIwithBatchTransferData(userData: ResponseUserData) {
    const batchTransfer = userData.batch_transfer[0]!

    setInactivityChecked(batchTransfer.of_inactivity)

    updateUIwithseconds(batchTransfer)

    updateUIWithBeneficiaries(batchTransfer)
  }

  // Helper for getUserData
  function updateUIWithBeneficiaries(batchTransfer: BatchTransfer) {
    const benes = batchTransfer.beneficiaries

    if (benes) {

      const updatedbenes: IBeneficiary[] = benes.map(
        (beneficiary: any) => {

          const updated = {
            nickname: beneficiary.nickname,
            icpAmount: beneficiary.amount_icp,
            userPrincipal: beneficiary.beneficiary_principal,
          }


          return updated
        }
      )


      setBeneficiaries(updatedbenes)
    }
  }

  // Helper for getUserData
  function updateUIwithseconds(batchTransfer: BatchTransfer) {
    const totalSeconds = Number(batchTransfer.execution_delay_seconds)

    const SECONDS_IN_YEAR = 365 * 24 * 60 * 60 // 31,536,000 seconds
    const SECONDS_IN_MONTH = 30 * 24 * 60 * 60 // 2,592,000 seconds

    const executionAfterYears = Math.floor(totalSeconds / SECONDS_IN_YEAR)
    const remainderAfterYears = totalSeconds % SECONDS_IN_YEAR

    const executionAfterMonths = Math.floor(remainderAfterYears / SECONDS_IN_MONTH)
    const remainderAfterMonths = remainderAfterYears % SECONDS_IN_MONTH

    const executionAfterSeconds = remainderAfterMonths


    setExecutionAfterYears(executionAfterYears)
    setExecutionAfterMonths(executionAfterMonths)
    setExecutionAfterSeconds(executionAfterSeconds)
  }

  // Helper function to get BTC address of the canister
  const getBtcAddress = async (principal : Principal) => {
    customLog('Entering getBtcAddress');
    const backend = getAuthClient()
    customLog('in getBtcAddress backend: ', backend);
    const principalArray = principal.toUint8Array();
    customLog('in getBtcAddress principalArray: ', principalArray)

    const address = await backend.btc_get_p2pkh_address([principalArray]);
    customLog('in getBtcAddress address: ', address);
    return address;
  }

  function startPolling(intervalTime: number) {
    customLog('in startPolling identity: ', identity)
    const intervalId = setInterval(async () => {
      customLog('in setInterval identity: ', identity)
      try {
        // const data = await canister.getData();
        customLog('in setInterval try{: ', identity)
        //const backend = getAuthClient();
        const timerStatus = await getUserHasActiveTimer()
        customLog('in setInterval timerStatus: ', timerStatus)
        customLog('in setInterval userData: ', userData)

        if (userData) {
          setUserData(prevData => {
            if (!prevData) {
              // If prevData is undefined, return it or handle accordingly
              return prevData;
            }

            // Return a new object with all required properties
            return {
              // Explicitly set all required properties
              nickname: prevData.nickname,
              avatar_url: prevData.avatar_url,
              batch_transfer: prevData.batch_transfer,
              // Update has_active_timer
              has_active_timer: timerStatus === TimerStatus.Active,
            };
          });
        }
        else {
          customLog('Cannot tell the timer status')
        }
      } catch (error) {
        console.error('Error telling the timer status: ', error);
      }
    }, intervalTime);
    return intervalId;
  }

  useEffect(() => {
    const init = async () => {
      customLog('In useEffect ()')
      const authClient = await AuthClient.create()
      const isAuthenticated = await authClient.isAuthenticated()
      customLog('Is authenticated', isAuthenticated)
      if (isAuthenticated) {
        await handleAuthentication(authClient)
      }
    }
    init()
  }, [])

  // Effect for reacting to changes in `principal`
  useEffect(() => {
    if (principal !== undefined) {
      // Define an async function inside the effect
      const fetchData = async () => {
        customLog('Principal is now defined', principal);
        await getUserData();
        await getAllUsers();
        if (BITCOIN)
        {
          try {
            const address = await getBtcAddress(principal);
            setBtcAddress(address);
          } catch (error) {
            console.error('Failed to fetch BTC address:', error);
            setBtcAddress(null);
          }        }
      };

      // Call the async function
      fetchData();
    }
  }, [principal]);

  useEffect(() => {
    console.log('useEffect [userData]:', userData)
    if (userData != undefined) {
      if (userData.has_active_timer) {
        const intervalId = startPolling(10000)

        return () => {
          console.log('Cleanup: Clearing interval', intervalId);
          clearInterval(intervalId);
        }
      }
      else {
        console.log('Define and call an async function to handle the asynchronous fetchBalance')
        const fetchBalanceAsync = async () => {
          await fetchBalance();
        };

        fetchBalanceAsync();
      }

    }
  }, [userData]);

  return (
    <Layout
      navItems={[
        !principal ? (
          <Button onClick={login}>login</Button>
        ) : (
          <Button onClick={logout}>logout</Button>
        ),
      ]}
    >
      <>
        {loading ? (
          <p>Loading...</p> // Show loading message when fetching data
        ) : (
          <>
            {principal && !userData && (
              <Card className="flex flex-col gap-6 py-4 px-8">
                <Input
                  value={newUsername}
                  onChange={e => setNewUsername(e.target.value)}
                  placeholder="nick"
                />
                <Button onClick={registerUsername}>register</Button>
              </Card>
            )}

            {principal && userData && (
              <>
                <h2 className="text-2xl font-bold mb-4">
                My testament {BITCOIN ? 'BTC' : 'ICP'}
                </h2>
                <Card className="flex flex-col gap-6 py-4 px-8">
                  <p>Nick: {userData.nickname}</p>
                  <p>Principal: {principal.toString()}</p>
                  {BITCOIN ? (
                    <p>Address: {btcAddress ? btcAddress : 'Loading...'}</p>
                  ) : (
                    <p>Account-id: {getAccountId(principal)}</p>
                  )}
                  <p>Balance: {Number(balance)}</p>

                  {allUsers && (
                    <Select
                      onValueChange={value => {
                        setTargetPrincipal(value)
                        pobierzChaty()
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Please select one" />
                      </SelectTrigger>
                      <SelectContent>
                        {allUsers.map(([userPrincipal, userData]) => (
                          <SelectItem key={userPrincipal.toText()} value={userPrincipal.toText()}>
                            {userData.nickname}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <Button onClick={addBeneficiary} disabled={!isBeneficiaryValid}>
                      Add beneficiary
                    </Button>
                    <Button onClick={clearBeneficiaries} disabled={beneficiaries.length === 0}>
                      Clear
                    </Button>
                  </div>

                  <div className="container mx-auto p-6">
                    <h2 className="text-2xl font-bold mb-4">Will beneficiaries</h2>
                    <div className="overflow-x-auto">
                      <table className="min-w-full bg-white border border-gray-300">
                        <thead>
                          <tr className="bg-gray-100">
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Beneficiary
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Amount
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Date
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-300">
                          {beneficiaries.map((beneficiary, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                <Input value={beneficiary.nickname} readOnly />
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                <Input
                                  value={beneficiary.icpAmount.toString()}
                                  onChange={e => {
                                    const newBeneficiaries = [...beneficiaries]
                                    newBeneficiaries[index].icpAmount = BigInt(e.target.value)
                                    setBeneficiaries(newBeneficiaries)
                                  }}
                                  placeholder="ICP value"
                                />
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                <Button onClick={() => removeBeneficiary(index)}>Remove</Button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {beneficiaries.length > 0 && (
                    <Card className="gap-4 flex flex-col justify-center items-center">
                      <h4>Execution after:</h4>

                      <div className="flex gap-4">
                        <div className="flex gap-6 items-center">
                          <Label htmlFor="years">Years:</Label>
                          <Input
                            id="years"
                            value={executionAfterYears}
                            onChange={e => setExecutionAfterYears(Number(e.target.value))}
                            placeholder="Years"
                          />
                        </div>

                        <div className="flex gap-6">
                          <Label htmlFor="years">Months:</Label>
                          <Input
                            id="months"
                            value={executionAfterMonths}
                            onChange={e => setExecutionAfterMonths(Number(e.target.value))}
                            placeholder="Months"
                          />
                        </div>

                        <div className="flex gap-6">
                          <Label htmlFor="seconds">Seconds:</Label>
                          <Input
                            id="seconds"
                            value={executionAfterSeconds}
                            onChange={e => setExecutionAfterSeconds(Number(e.target.value))}
                            placeholder="Seconds"
                          />
                        </div>
                      </div>


                      <div className="flex items-center gap-4">
                        <input
                          type="checkbox"
                          id="inactivity"
                          checked={inactivityChecked}
                          onChange={e => setInactivityChecked(e.target.checked)}
                        />
                        <Label htmlFor="inactivity" className="mb-4">of inactivity</Label>

                      </div>
                    </Card>
                  )}

                  {/* Buttons Container */}
                  <Card style={{ marginTop: '20px' }}>
                    <div className="flex flex-row gap-4 justify-center items-center">
                      <Button onClick={saveAndActivate} disabled={!isSaveAndActivateEnabled}>
                        <SaveIcon className="mr-2" />
                        Save and Activate
                      </Button>
                      <Button onClick={cancelTimer} disabled={!userData.has_active_timer || loading}>
                        {loading ? 'Cancelling...' : 'Cancel'}
                      </Button>
                    </div>
                  </Card>

                  <div className="flex flex-row gap-8">
                    <div className="flex flex-col gap-4">
                      <Label htmlFor="showChat">Show chat</Label>
                      <Checkbox id="showChat" checked={showChat} onCheckedChange={setShowChat} />
                    </div>

                    <div className="flex flex-row gap-8">
                      <div className="flex flex-col gap-4">
                        <Label htmlFor="showDirectTransfer">Show direct transfer</Label>
                        <Checkbox
                          id="showDirectTransfer"
                          checked={showDirectTransfer}
                          onCheckedChange={setShowDirectTransfer}
                        />
                      </div>
                    </div>
                  </div>

                  {showChat && (
                    <>
                      <Card>{chats[0]?.map((chat, index) => <div key={index}>{chat}</div>)}</Card>

                      <Textarea
                        value={newChat}
                        onChange={e => setNewChat(e.target.value)}
                        placeholder="wiadomosc"
                      />
                      <Button onClick={dodajChatMSG}>Dodaj notatke</Button>
                    </>
                  )}

                  {showDirectTransfer && (
                    <>
                      <Label htmlFor="amountToSend">Amount to send:</Label>
                      <Input
                        value={amountToSend}
                        onChange={e => setAmountToSend(Number(e.target.value))}
                        placeholder="Amount to send"
                      />

                      <Label htmlFor="transferDelay">Delay in seconds:</Label>
                      <Input
                        value={transferDelay}
                        onChange={e => setTransferDelay(Number(e.target.value))}
                        placeholder="Delay in seconds"
                      />

                      <div className="flex items-center mb-2">
                        <Label htmlFor="overrideTarget" className="mr-2 flex items-center">Override target principal</Label>
                        <input
                          type="checkbox"
                          id="overrideTarget"
                          checked={overrideTarget}
                          onChange={(e) => setOverrideTarget(e.target.checked)}
                          className="mr-2"
                        />
                        <div className={`flex items-center ${overrideTarget ? '' : 'opacity-0'}`}>
                          <Label htmlFor="overridePrincipal" className="mr-2">Overriding with principal:</Label>
                          <input
                            type="text"
                            id="overridePrincipal"
                            value={overridePrincipal}
                            onChange={(e) => setOverridePrincipal(e.target.value)}
                            className="block border border-gray-300 mb-2"
                            disabled={!overrideTarget}
                          />
                        </div>
                      </div>

                      <Button onClick={transfer}>Direct transfer</Button>
                    </>
                  )}
                </Card>
              </>
            )}            </>
        )}
      </>
    </Layout>
  )
}

export default App
