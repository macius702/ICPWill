import React, { useState, useEffect } from 'react'
import { AuthClient } from '@dfinity/auth-client'
import { Actor, HttpAgent, Identity } from '@dfinity/agent'
import { Principal } from '@dfinity/principal'
import { icp_will_backend, canisterId, createActor } from '../../declarations/icp_will_backend'
import { idlFactory as icrc1_ledger_canister_Idl } from '../../declarations/icrc1_ledger_canister'
import { Tokens } from '../../declarations/icrc1_ledger_canister/icrc1_ledger_canister.did';

import type {
  TransferArgs,
  UserData,
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

interface Beneficiary {
  nickname: string
  icpAmount: number
  userPrincipal: Principal
}

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
  const [userData, setUserData] = useState<UserData | undefined>()
  const [newUsername, setNewUsername] = useState<string>('')
  const [allUsers, setAllUsers] = useState<[Principal, UserData][]>([])
  const [balance, setBalance] = useState<BigInt | null>(null)
  const [amountToSend, setAmountToSend] = useState<number>(0)
  const [transferDelay, setTransferDelay] = useState<number>(0)
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([])
  const [executionAfterYears, setExecutionAfterYears] = useState<number>(0)
  const [executionAfterMonths, setExecutionAfterMonths] = useState<number>(0)
  const [executionAfterSeconds, setExecutionAfterSeconds] = useState<number>(0)
  const [showChat, setShowChat] = useState<CheckedState>(false)
  const [showDirectTransfer, setShowDirectTransfer] = useState<CheckedState>(false)
  const [overrideTarget, setOverrideTarget] = useState(false);
  const [overridePrincipal, setOverridePrincipal] = useState('');

  const isBeneficiaryValid =
    targetPrincipal &&
    targetPrincipal !== principal?.toText() &&
    targetPrincipal !== 'Please select one'
  const isSaveAndActivateEnabled =
    beneficiaries.length > 0 &&
    (executionAfterYears > 0 || executionAfterMonths > 0 || executionAfterSeconds > 0)

  const isUserLogged = () => {
    if (!identity || !principal || principal.isAnonymous()) {
      throw new Error('PLZ log in')
    }
    return { identity, principal }
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

  const getAuthClient = () => {
    isUserLogged()
    return createActor(canisterId, {
      agentOptions: {
        identity: identity,
      },
    })
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
    const chatPath = [target, identity.getPrincipal()].sort()
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
    const { principal } = isUserLogged()
    const maybeUserData = await icp_will_backend.get_user(principal)
    setUserData(maybeUserData.length === 0 ? undefined : maybeUserData[0])
    await fetchBalance()
  }

  const getAllUsers = async () => {
    const users = await icp_will_backend.get_users()
    setAllUsers(users)
  }


  const transfer = async () => {
    try {
      if (!identity) throw new Error('Identity is undefined');

      const backend = getAuthClient();
      console.log('backend', backend);

      const target = overrideTarget ? Principal.fromText(overridePrincipal) : validateTargetPrincipal();
      console.log('target', target);

      const { principal } = isUserLogged();
      if (!principal) throw new Error('Principal is undefined');
      console.log('principal', principal);

      const agent = await createAgentWithHost(identity);
      const myledger = createLedgerActor(agent);

      async function getBalance(label: string) {
        await Promise.all(
          allUsers.map(async ([userPrincipal, userData]) => {
            const balance = await myledger.icrc1_balance_of({ owner: userPrincipal, subaccount: [] });
            console.log(label, userData.nickname, balance, userPrincipal.toText());
          })
        );
      }

      await getBalance('balance_before');

      const theSpender = Principal.fromText(canisterId);
      console.log('Spender: ', theSpender.toText());

      const feeFromLedger = await myledger.icrc1_fee() as Tokens;// TODO(mtlk) why Tokens not imported automatically

      const approveResult = await myledger.icrc2_approve({
        fee: [],
        memo: [],
        from_subaccount: [],
        created_at_time: [],
        amount: BigInt(amountToSend) + feeFromLedger,
        spender: { owner: theSpender, subaccount: [] },
      });

      console.log('approve_result', approveResult);

      const allowanceResult = await myledger.icrc2_allowance({
        account: { owner: principal, subaccount: [] },
        spender: { owner: theSpender, subaccount: [] },
      });

      console.log('allowance_result', allowanceResult);

      const transferArgs: TransferArgs = {
        to_account: { owner: target, subaccount: [] },
        amount: BigInt(amountToSend),
        delay_in_seconds: BigInt(transferDelay),
        from_account: { owner: principal, subaccount: [] },
      };

      const result = await backend.transfer(transferArgs);
      await getBalance('balance_after');
      console.log(result);

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
    const authClient = await AuthClient.create()
    await authClient.login({
      identityProvider: IDENTITY_PROVIDER,
      onSuccess: async () => {
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
            icpAmount: 0,
            userPrincipal: selectedUser[0],
          },
        ])
      }
    }
  }

  const removeBeneficiary = (index: number) => {
    setBeneficiaries(beneficiaries.filter((_, i) => i !== index))
  }



  const setupAllowancesForBatchTransfer = async () => {
    try {
      if (!principal || !identity) throw new Error('Principal or Identity is undefined');

      const agent = await createAgentWithHost(identity);
      const myledger = createLedgerActor(agent);

      const feeFromLedger = await myledger.icrc1_fee() as Tokens;
      const overallTransactionCost = feeFromLedger * BigInt(beneficiaries.length) + feeFromLedger;

      const assetsSum = beneficiaries.reduce((sum, { icpAmount }) => sum + icpAmount, 0);
      const overallSum = BigInt(assetsSum) + overallTransactionCost;

      const theSpender = Principal.fromText(canisterId);
      console.log('Spender: ', theSpender.toText());

      const approveResult = await myledger.icrc2_approve({
        fee: [],

        memo: [],

        from_subaccount: [],
        created_at_time: [],
        amount: overallSum,
        expected_allowance : [],
        expires_at : [],
        spender: { owner: theSpender, subaccount: [] },
      });

      console.log('batch_approve_result', approveResult);

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
      console.log('Save and Activate triggered');
      const executionTimeInSeconds = BigInt(executionAfterYears * 31536000 + executionAfterMonths * 2592000 + executionAfterSeconds);
      console.log('this.benefficiaries', beneficiaries);
      const payload = {
        beneficiaries: beneficiaries.map(b => ({
          beneficiary_principal: b.userPrincipal,
          nickname: b.nickname ? b.nickname : "",
          amount_icp: BigInt(b.icpAmount),
          // 
        })),
        execution_delay_seconds: executionTimeInSeconds,
      };
      console.log('Save and Activate triggered with payload:', payload);
      const backend = getAuthClient();
      await backend.register_batch_transfer(payload);
      console.log('After Save and Activate triggered with payload:', payload);

      setupAllowancesForBatchTransfer()

      await backend.execute_batch_transfers();


      //await backend.execute_batch_transfers();


      ;
    }
  }

  const handleAuthentication = async (authClient: AuthClient) => {
    const identity = authClient.getIdentity()
    const principal = identity.getPrincipal()
    setPrincipal(principal)
    setIdentity(identity)
    console.log('Zalogowano', principal)
    await getUserData()
    await getAllUsers()
  }

  const fetchBalance = async () => {
    const { principal } = isUserLogged()
    const backend = getAuthClient()
    let result = await backend.get_balance()
    if ('Ok' in result) {
      setBalance(result.Ok)
    } else {
      setBalance(null)
    }
    console.log(result)
  }
  // Helper function to create an agent
  async function createAgentWithHost(identity: Identity) {
    const fetchRootKey = NETWORK !== '--ic';
    console.log('fetchRootKey: ', fetchRootKey)
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

  useEffect(() => {
    const init = async () => {
      const authClient = await AuthClient.create()
      const isAuthenticated = await authClient.isAuthenticated()
      console.log('Is authenticated', isAuthenticated)
      if (isAuthenticated) {
        await handleAuthentication(authClient)
      }
    }
    console.log('mounted effect');
    init()
  }, [])

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
            <h2 className="text-2xl font-bold mb-4">My testament ICP</h2>
            <Card className="flex flex-col gap-6 py-4 px-8">
              <p>Nick: {userData.nickname}</p>
              <p>Principal: {principal.toString()}</p>
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

              <Button onClick={addBeneficiary} disabled={!isBeneficiaryValid}>
                Add beneficiary
              </Button>

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
                              value={beneficiary.icpAmount}
                              onChange={e => {
                                const newBeneficiaries = [...beneficiaries]
                                newBeneficiaries[index].icpAmount = Number(e.target.value)
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
                </Card>
              )}

              <Card style={{ marginTop: '20px' }}>
                <Button onClick={saveAndActivate} disabled={!isSaveAndActivateEnabled}>
                  Save and Activate
                </Button>
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
        )}
      </>
    </Layout>
  )
}

export default App
