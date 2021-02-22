<!-- routify:options preload="proximity" -->
<script>
  import { metatags } from '@roxi/routify'
  import NavBar from './_components/NavBar/index.svelte'
  metatags.title = 'Welcome'
  metatags.description = 'This app welcomes you'
</script>

<NavBar />
<slot />
