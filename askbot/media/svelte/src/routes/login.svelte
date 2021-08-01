<script context="module">
  import client from '../data/client.js'
  import SETTINGS_QUERY from '../data/queries/settings'
  import LoginButtons from '../components/LoginButtons.svelte'

  export async function preload() {
    let settings = await client.query({ query: SETTINGS_QUERY })
    return {
      cache: settings
    }
  }
</script>

<script>
  import { setClient, restore, query } from 'svelte-apollo'
  export let cache;
  //restore(client, SETTINGS_QUERY, cache.data)
  //setClient(client)
  const settings = query(client, {query: SETTINGS_QUERY})
</script>


<h1>Please click any of the buttons below to sign in</h1>
<LoginButtons />
{#await $settings then result}
  <h2>Or enter your {result.data.settings.appShortName} login name and password</h2>
  <p>{window.gettext('Type a message')}</p>
{/await}
