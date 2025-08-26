<script setup>
import { useKeycloak, getToken } from '@josempgon/vue-keycloak'
import { ref } from 'vue'

const {
  // Reactive State
  isAuthenticated,
  isPending,
  hasFailed,
  token,
  decodedToken,
  username,
  roles,
  resourceRoles,

  // Object Instances
  keycloak,

  // Functions
  hasRoles,
  hasResourceRoles,
} = useKeycloak()

const response = ref('')


async function postMessage(message) {
  response.value = ''
  const validtoken = await getToken()
  fetch('http://localhost:8000/api/v1/documents', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token.value}`
    }
  })
  .then(response => response.json())
  .then(data => {
    response.value = data
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

</script>


<template>

  <main>
    <section v-if="isAuthenticated">
      <h2>Welcome {{ username }}</h2>
      <button @click="keycloak.accountManagement()">Account</button>
      <button @click="keycloak.logout()">Logout</button>
      <button @click="keycloak.register()">Register</button>
      <button @click="postMessage('Hello from the frontend!')">Send Message to backend</button>

      <h3 v-if="response">Response:</h3>
      <pre v-if="response">
      {{ response }}
      </pre>

      <h3>Token Information:</h3>
      <pre>{{ decodedToken }}</pre>
    </section>
    <section v-else>
      <p>Could not parse token. <button @click="keycloak.login()">Login</button></p>
    </section>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
