<script>
  import userStore from '../../../stores/userStore.js'
  import { onMount } from 'svelte'

  let user
  const unsubscribe = userStore.subscribe(store => user = store)

  function logout(evt) {
    evt.preventDefault()
    userStore.empty()
  }

  onMount(() => {
    userStore.init()
  })
</script>

<style>
  nav {
    margin-bottom: 0;
    text-align: center;
  }
  a {
    border-right: 1px solid #aaa;
    padding-right: 0.5rem;
    margin-right: 0.5rem;
  }
  a:last-child {
    border: none;
  }
</style>

<nav>
  <a href='/'>Home</a>
  <a href='/questions/'>Questions</a>
  {#if user?.token }
    <a href='/' on:click={logout}>Logout</a>
  {:else}
    <a href='/login'>Login</a>
    <a href='/register'>Register</a>
  {/if}
</nav>
