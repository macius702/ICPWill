<script lang="ts">
import { ref } from 'vue';
import { bootcamp_chat_backend, canisterId, createActor } from '../../declarations/bootcamp_chat_backend';
import { AuthClient } from '@dfinity/auth-client';
import { HttpAgent } from '@dfinity/agent';
import type { Identity } from '@dfinity/agent';
import { Principal } from '@dfinity/principal';
import type { UserData } from '../../declarations/bootcamp_chat_backend/bootcamp_chat_backend.did';

export const IDENTITY_PROVIDER = import.meta.env.VITE_IDENTITY_PROVIDER;

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
      allUsers: [] as [Principal, UserData][],
      balance: null,
      amountToSend: 0,
      transferDelay: 0
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
      console.log("Entering dodajChatMSG")

      const targetPrincipal = this.validateTargetPrincipal()
      console.log("Target principal", targetPrincipal)

      const backend = this.getAuthClient();
      console.log("Backend", backend)

      console.log("Before Added chat msg")
      await backend.add_chat_msg(this.newChat, targetPrincipal)
      console.log("After Added chat msg")

      console.log("Before pobierzChaty")
      await this.pobierzChaty()
      console.log("After pobierzChaty")
    },
    async pobierzChaty() {
      const { identity, principal } = this.isUserLogged()
      const targetPrincipal = this.validateTargetPrincipal()

      const chatPath = [targetPrincipal, identity.getPrincipal()].sort()
      console.log("IN pobierzChaty Chat path", chatPath)
      console.log("IN pobierzChaty Chat path str", chatPath.toLocaleString())
      const chats = await bootcamp_chat_backend.get_chat(chatPath)
      console.log("IN pobierzChaty Chats", chats)
      console.log("IN pobierzChaty Chats", chats.toLocaleString())
      
      this.chats = chats
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
      //await this.fetchBalance()      
      console.log("User data", this.userData)
    },
    async getAllUsers() {
      this.allUsers = await bootcamp_chat_backend.get_users()
    },
    async transfer() {
      const { principal } = this.isUserLogged()
      const backend = this.getAuthClient();

      const targetPrincipal = this.validateTargetPrincipal()
      let to_principal = targetPrincipal


      //let to_principal = Principal.fromText('agt74-uhoi3-3eolc-fwiby-qcr6q-b2w7a-gcy7v-t3bpi-rpie2-6yqai-aae');

      //. todo validate amount to send
      

      console.log("Before transfer from", principal, "to", to_principal, "amount", this.amountToSend, "delay", this.transferDelay)

      let acc = { owner: to_principal, subaccount: [] };

      let transferArgs = {
        to_account: acc,
        amount: this.amountToSend
      };


      // the fun ction below returns:
      // type Result = variant { Ok : nat; Err : text };
      let result = await backend.transfer(transferArgs);
      console.log(result);

    },

    async logout() {
      const authClient = await AuthClient.create();
      await authClient.logout()
      this.identity = undefined;
      this.principal = undefined;
      this.chats = [];
      this.userData = undefined
      localStorage.clear()
    },



    async login() {
      const authClient = await AuthClient.create();
      await authClient.login({
        identityProvider: IDENTITY_PROVIDER,
        onSuccess: async () => {
          await this.handleAuthentication(authClient);
        }
      });
    },

    // helpers
    async handleAuthentication(authClient: AuthClient) {
      const identity = authClient.getIdentity();
      const principal = identity.getPrincipal();
      this.principal = principal;
      this.identity = identity;
      console.log("Zalogowano", this.principal);
      await this.getUserData();
      await this.getAllUsers();
    },
    async fetchBalance() {
      const { principal } = this.isUserLogged()
      const backend = this.getAuthClient();
      let result = await backend.get_balance()
      console.log(result)
    },

  },
  async mounted() {
    console.log('Entering mounted');
    const authClient = await AuthClient.create();
    const isAuthenticated = await authClient.isAuthenticated();
    console.log('Is authenticated', isAuthenticated);
    if (isAuthenticated) {
      await this.handleAuthentication(authClient);
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
      <p>Nick: {{ userData.nickname }}</p>
      <p>Principal: {{ principal }}</p>
      <p>Balance: {{ balance }}</p>

      <div v-if="allUsers">
        <select v-model="targetPrincipal" @change="pobierzChaty">
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
      <label for="amountToSend">Amount to send:</label>
      <input v-model="amountToSend" type="number" placeholder="Amount to send" />

      <label for="transferDelay">Delay in seconds:</label>
      <input v-model="transferDelay" type="number" placeholder="Delay in seconds" />
      <button @click="transfer">Transfer</button>
    </div>
  </main>
</template>
