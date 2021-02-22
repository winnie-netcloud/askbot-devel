<script>
  import { Router } from "@roxi/routify";
  import { routes } from "../.routify/routes";
  import { beforeUrlChange } from '@roxi/routify';
  import i18nStore from './stores/i18nStore'
  $beforeUrlChange(async (event, extra) => {
    if (event.type === 'pushstate') {
      await i18nStore.loadCatalog(event.url)
    }
    return true
  })
</script>

<style global>
  @import "../assets/global.css";
</style>

<Router {routes} />
