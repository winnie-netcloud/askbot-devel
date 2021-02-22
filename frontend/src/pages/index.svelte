<script>
  import { fade } from 'svelte/transition'
  import userStore from '../stores/userStore.js'
  import { gettext, ngettext } from 'django-i18n'
  let userName
  // tr: translator comment
  gettext('hello world')
  const unsubscribe = userStore.subscribe(store => {
    userName = store.userName
  })
</script>
<style>
  div {
    align-items: center;
    display: flex;
    font-size: 5rem;
    height: calc(100vh - 2rem);
    justify-content: center;
  }
  span {
    text-transform: capitalize;
    margin-left: 0.5rem;
  }
</style>
<div in:fade={{duration: 250}}>
  <div>Welcome <span>{userName || 'Stranger'}</span>!</div>
  { ngettext('auaouaou %d', 'aouaou %d', 5) }
</div>
