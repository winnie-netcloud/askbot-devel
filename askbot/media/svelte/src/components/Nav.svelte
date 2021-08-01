<script>
  import { onMount } from 'svelte'
  import { faMedal, faUsers, faTag } from '@fortawesome/free-solid-svg-icons'

	export let segment;

  let Fa

  onMount(async () => {
    const mod = await import('svelte-fa')
    Fa = mod.default
  })

</script>

<style>
  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 3rem;
    color: #d0e296;
    background: #16160f;
    padding: 0 1rem;
  }
  @media (max-width: 400px) {
    nav {
      height: 6rem;
      flex-direction: column;
      align-items: flex-start;
    }
  }
  ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  ul.user-nav li {
    margin-right: 1rem;
  }
  ul.site-nav li {
    margin-left: 1rem;
  }
  ul.site-nav a {
    margin-left: 0.375rem !important;
  }
</style>

<nav>
	<ul class='user-nav'>
		<li><a class='{segment === undefined ? "selected" : ""}' href='login'>Hi there! Please sign in</a></li>
		<li><a class='{segment === "help" ? "selected" : ""}' href='help'>help</a></li>
	</ul>
  <ul class='site-nav'>
    <li><svelte:component this={Fa} icon={faTag} /><a class='{segment === "tags" ? "selected": ""}' href='tags'>tags</a></li>
    <li><svelte:component this={Fa} icon={faUsers} /><a class='{segment === "users" ? "selected": ""}' href='users'>users</a></li>
    <li><svelte:component this={Fa} icon={faMedal} /><a class='{segment === "badges" ? "selected": ""}' href='badges'>badges</a></li>
  </ul>
</nav>
