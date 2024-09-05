import React, { useState, useEffect } from 'react'
import { AuthClient } from '@dfinity/auth-client'
import { Identity } from '@dfinity/agent'
import { Principal } from '@dfinity/principal'
import { icp_will_backend, canisterId, createActor } from '../../declarations/icp_will_backend'
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

interface Beneficiary {
  nickname: string
  icpAmount: number
  userPrincipal: Principal
}

const IDENTITY_PROVIDER = import.meta.env.VITE_IDENTITY_PROVIDER

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
    const { principal } = isUserLogged()
    const backend = getAuthClient()
    const target = validateTargetPrincipal()

    const transferArgs: TransferArgs = {
      to_account: {
        owner: target,
        subaccount: [], // This should be compatible with the expected type
      },
      amount: BigInt(amountToSend), // Convert to BigInt if the backend expects it
    }

    let result = await backend.transfer(transferArgs)
    console.log(result)
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

  const saveAndActivate = () => {
    if (isSaveAndActivateEnabled) {
      const executionTime = {
        years: executionAfterYears,
        months: executionAfterMonths,
        seconds: executionAfterSeconds,
      }
      const payload = {
        beneficiaries: beneficiaries.map(b => ({
          principal: b.userPrincipal.toText(),
          nickname: b.nickname,
          icpAmount: b.icpAmount,
        })),
        executionAfter: executionTime,
      }
      console.log('Save and Activate triggered with payload:', payload)
      // Add your activation logic here (API calls, etc.)
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

  useEffect(() => {
    const init = async () => {
      const authClient = await AuthClient.create()
      const isAuthenticated = await authClient.isAuthenticated()
      console.log('Is authenticated', isAuthenticated)
      if (isAuthenticated) {
        await handleAuthentication(authClient)
      }
    }
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
