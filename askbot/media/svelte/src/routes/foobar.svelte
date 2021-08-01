<script context="module">
  import client from '../data/client.js'
  import SETTINGS_QUERY from '../data/queries/settings'

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

<h1>foobar</h1>
{#await $settings}
  Loading ...
{:then result}
  {result.data.settings.appShortName}
{:catch error}
  <div>Oops, there was some error</div>
  <div>{error}</div>
{/await}

