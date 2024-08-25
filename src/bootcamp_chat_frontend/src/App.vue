<script lang="ts">
import { ref } from 'vue';
import { bootcamp_chat_backend, canisterId, createActor } from '../../declarations/bootcamp_chat_backend';
import { AuthClient } from '@dfinity/auth-client';
import { Actor, HttpAgent} from '@dfinity/agent';
import type { HttpAgentOptions }  from '@dfinity/agent';
  
import type { Identity } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import type { UserData } from '../../declarations/bootcamp_chat_backend/bootcamp_chat_backend.did';
import { IcrcLedgerCanister } from "@dfinity/ledger-icrc";
import { createAgent } from "@dfinity/utils";
import { idlFactory as icrc1_ledger_canister_idl } from '../../declarations/icrc1_ledger_canister';

const LEDGER_CANISTER_ID='ryjl3-tyaaa-aaaaa-aaaba-cai'



export default {
  data() {
    return {
      newChat: "",
      chats: [] as string[][],
      identity: undefined as undefined | Identity,
      principal: undefined as undefined | Principal,
      targetPrincipal: "",
      userData: undefined as undefined | UserData,
      newUsername: "",
      allUsers: [] as [Principal, UserData][]
    }
  },
  methods: {
    isUserLogged() {
      if (!this.identity || !this.principal || this.principal === Principal.anonymous()) {
        throw new Error("PLZ log in")
      }
      return {
        identity: this.identity,
        principal: this.principal
      }
    },
    validateTargetPrincipal() {
      const cleanTargetPrincipal = this.targetPrincipal.trim();
      if (cleanTargetPrincipal === "") {
        throw new Error("No principal")
      }
      const targetPrincipal = Principal.fromText(cleanTargetPrincipal)
      if (!targetPrincipal || targetPrincipal === Principal.anonymous()) {
        throw new Error("Wrong target")
      }
      return targetPrincipal
    },
    getAuthClient() {
      this.isUserLogged()
      return createActor(canisterId, {
        agentOptions: {
          identity: this.identity
        }
      });
    },
    async dodajChatMSG() {
      const targetPrincipal = this.validateTargetPrincipal()
      const backend = this.getAuthClient();
      await backend.add_chat_msg(this.newChat, targetPrincipal)
      await this.pobierzChaty()
    },
    async pobierzChaty() {
      const { identity, principal } = this.isUserLogged()
      const targetPrincipal = this.validateTargetPrincipal()

      const chatPath = [targetPrincipal, identity.getPrincipal()].sort()
      this.chats = await bootcamp_chat_backend.get_chat(chatPath)
    },
    async login() {
      const authClient = await AuthClient.create();
      await authClient.login({
        //identityProvider: import.meta.env.VITE_APP_IDENTITY_PROVIDER,
        identityProvider: "https://identity.ic0.app/#authorize",
        //identityProvider: "http://be2us-64aaa-aaaaa-qaabq-cai.localhost:4943/",
        onSuccess: async () => {
          const identity = authClient.getIdentity();
          
          const principal = identity.getPrincipal();
          this.principal = principal;
          this.identity = identity;
          console.log("Zalogowano", this.principal)
          await this.getUserData()
          await this.getAllUsers()
        }
      })
    },
    async logout() {
      const authClient = await AuthClient.create();
      await authClient.logout()
      this.identity = undefined;
      this.principal = undefined;
      this.chats = [];
      this.userData = undefined
    },
    async registerUsername() {
      const trimedUsername = this.newUsername.trim();
      const backend = this.getAuthClient();
      await backend.register(trimedUsername)
      await this.getUserData()
      await this.getAllUsers()
    },
    async getUserData() {
      const { principal } = this.isUserLogged()
      const maybeUserData = await bootcamp_chat_backend.get_user(principal as Principal)
      if (maybeUserData.length === 0) {
        this.userData = undefined
      } else {
        this.userData = maybeUserData[0]
      }
      console.log("User data", this.userData)
    },
    async getAllUsers() {
      this.allUsers = await bootcamp_chat_backend.get_users()
    },
    async transfer() {
      

      //   //const a = await icrc1_ledger_canister.icrc2_approve("
      //   const agent = await createAgent({
      //     host: "http://localhost:8000",
      //     identity: this.identity,
      //   });

      // const { metadata } = IcrcLedgerCanister.create({
      //   agent,
      //   canisterId: import.meta.env.VITE_APP_LEDGER_CANISTER_ID,
      // });

      //   const data = await metadata({});
      //   console.log('data:', data);

      // i want the global ledger canister
      // const icrc1_ledger_canister = IcrcLedgerCanister.create({
      //   agent,
      //   canisterId: Principal.fromText("icrc1-aaaaa-aaaaa-aaaaa-aaaaa-aaaaa-aaaaa-aaaaa-aaaaa-aaaaa-aaaaa"),
      // });

      // const a = createActor(import.meta.env.VITE_APP_LEDGER_CANISTER_ID, {
      //   agentOptions: {
      //     identity: this.identity
      //   }
      // });
      // a.


      console.log('mtlk Matiki here');


      //caller in backend :  22hlo-vukku-nwwrv-hndxd-p6vwz-thrwl-udox2-gchyj-kbtpm-7watc-jqe



        const { principal } = this.isUserLogged()
      let from_acc = { owner: principal, subaccount: [] };
       const backend = this.getAuthClient();

       console.log(backend);
       console.log('identity:', this.identity);
       console.log('identity principal:', this.identity?.getPrincipal());
       console.log('identity principal toText:', this.identity?.getPrincipal().toText());

       console.log('mtlk Matiki here 2');

        // Create an agent to interact with the Internet Computer

        // const  options : HttpAgentOptions = {
        //   host: "http://localhost:4943",
        //   identity: this.identity,
        // };

        if (!this.identity) {
          throw new Error("mtlk No identity")
        }

        const identity = this.identity || {
          getPrincipal: () => Principal.fromText('default-principal-id'),
          transformRequest: async (request) => {
            // Transform the request here if needed
            return request;
          },
        };

        console.log('identity principal toText:', identity.getPrincipal().toText());

        console.log('mtlk Matiki here 2f');
        console.log('identity:', identity);
        console.log('host:', import.meta.env.VITE_AUTH_PROVIDER_URL); 
        console.log('dfx netowrk:', process.env.DFX_NETWORK);
        console.log('fetchRootKey:', process.env.DFX_NETWORK === "local");

        console.log('canisterId:', canisterId);
        
        const agent = await createAgent({
          identity: identity,
          host: import.meta.env.VITE_AUTH_PROVIDER_URL,
          fetchRootKey: process.env.DFX_NETWORK === "local",
        });

        console.log('agent:', agent); 
        console.log('mtlk Matiki here 3');


        console.log('icrc1_ledger_canister_id :', LEDGER_CANISTER_ID);

        // Create an instance of the icrc1_ledger_canister
        const icrc1_ledger_canister = Actor.createActor(icrc1_ledger_canister_idl, { agent, canisterId: LEDGER_CANISTER_ID });

        console.log('mtlk Matiki here 4');
        console.log('icrc1_ledger_canister:', icrc1_ledger_canister);

        // Now you can call functions on the icrc1_ledger_canister instance. For example:

        console.log('mtlk Matiki here 5');


        const name = await icrc1_ledger_canister.icrc1_name();
        console.log('icrc1_ledger_canister.icrc1_name():', name);
        
        // //'icrc1_balance_of' : IDL.Func([Account], [Tokens], ['query']),
        // balance = await this.actor.icrc1_balance_of({
        // owner: Principal.fromText(address),


        const identity_balance = await icrc1_ledger_canister.icrc1_balance_of({
          owner: Principal.fromText('zgcr3-w3e7h-6okfu-e5dke-k66xm-kadri-lvnuw-kipko-mysl7-r6p53-xae'),   subaccount: [],
        });
        console.log('identity_balance:', identity_balance);

        const metadata = await icrc1_ledger_canister.icrc1_metadata();
        console.log('metadata:', metadata);


  //       const ApproveArgs = IDL.Record({
  //   'fee' : IDL.Opt(IDL.Nat),
  //   'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
  //   'from_subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
  //   'created_at_time' : IDL.Opt(IDL.Nat64),
  //   'amount' : IDL.Nat,
  //   'expected_allowance' : IDL.Opt(IDL.Nat),
  //   'expires_at' : IDL.Opt(IDL.Nat64),
  //   'spender' : Account,
  // });

//   dfx canister $NETWORK call --identity Alice $LEDGER icrc2_approve "(
//   record {
//     spender= record {
//       owner = principal \"$BACKEND_CANISTER_ID\";
//     };
//     amount = 10_300: nat;
//   }
// )"

        const approveResult = await icrc1_ledger_canister.icrc2_approve({
          fee: [],
          memo: [],
          from_subaccount:  [],
          created_at_time:  [],
          amount: BigInt(20000),
          expected_allowance:  [],
          expires_at:  [],
          spender: {
            owner: Principal.fromText('dxzul-dqaaa-aaaan-qmvuq-cai'),
            subaccount:  []
          }
        });

        console.log('approveResult:', approveResult);

        console.log('mtlk Matiki here 5f');

        //'icrc2_allowance' : IDL.Func([AllowanceArgs], [Allowance], ['query']),
  //       const AllowanceArgs = IDL.Record({
  //   'account' : Account,
  //   'spender' : Account,
  // });

  const mtlk_allowance = 
        await icrc1_ledger_canister.icrc2_allowance(
          {
            account: from_acc,
            spender: {
              owner: Principal.fromText('dxzul-dqaaa-aaaan-qmvuq-cai'),
              subaccount:  []
            }
          }
        );
        
        console.log('mtlk_allowance:', mtlk_allowance);
        

        console.log('mtlk Matiki here 6');

        console.log(name);      

        console.log('mtlk Matiki here 7');


      let to_principal = Principal.fromText('agt74-uhoi3-3eolc-fwiby-qcr6q-b2w7a-gcy7v-t3bpi-rpie2-6yqai-aae');

      let to_acc = { owner: to_principal, subaccount: [] };

      let transferArgs = {
        amount: BigInt(300),
        to_account: to_acc,
        from_account: from_acc,
        delay_in_seconds: 20
      };

      console.log('transferArgs:', transferArgs);


      // the function below returns:
      // type Result = variant { Ok : nat; Err : text };
      let result = await backend.transfer(transferArgs);
      console.log(result);

    }
  },
}
</script>

<template>
  <main>
    <button v-if="!principal" @click="login">login</button>
    <button v-if="principal" @click="logout">logout</button>

    <div v-if="principal && !userData">
      <input v-model="newUsername" placeholder="nick" /> <button @click="registerUsername">register</button>
    </div>
    <div v-if="principal && userData">
      {{ userData.nickname }}
      <div v-if="allUsers">
        <select v-model="targetPrincipal">
          <option disabled value="">Please select one</option>
          <option v-for="[userPrincipal, userData] in allUsers" :value="userPrincipal.toText()">{{ userData.nickname }}
          </option>
        </select>
      </div>
      <div>
        <div v-for="chat in chats[0]">
          {{ chat }}
        </div>
      </div>
      <div>
        <textarea v-model="newChat" placeholder="wiadomosc"></textarea><button @click="dodajChatMSG">Dodaj
          notatke</button>
      </div>
      <button @click="transfer">Transferuj</button>
    </div>
    <div v-else>
      <button @click="transfer">Transferuj w/o authorization</button>
    </div>
  </main>
</template>
